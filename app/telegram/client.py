"""Telethon client lifecycle management with a resilient interactive login."""

import getpass
import io
import os

import qrcode
from ..ui.theme import make_console
from rich.panel import Panel

from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    FloodWaitError,
    PasswordHashInvalidError,
    PhoneCodeEmptyError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberBannedError,
    PhoneNumberUnoccupiedError,
    RPCError,
    SessionPasswordNeededError,
)

console = make_console()

CODE_DELIVERY_LABELS = {
    "CodeTypeApp": "your Telegram app (open Telegram — the code should already be there)",
    "CodeTypeSms": "an SMS to your phone",
    "CodeTypeCall": "a phone call to your number",
    "CodeTypeFlashCall": "a flash call (missed-call style)",
    "CodeTypeFragment": "Fragment",
    "CodeTypeEmailCode": "your email",
}


class LoginAborted(Exception):
    """User cancelled the interactive login."""


def normalize_phone(raw: str) -> str | None:
    """Validate a phone number and return it in international `+<digits>` form.

    Returns None (with a printed hint) when the number cannot be valid.
    """
    cleaned = raw.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    digits = cleaned.lstrip("+")
    if cleaned.startswith("0") or cleaned.startswith("+0"):
        console.print(
            "[bright_red]✘[/] Leading zero detected. Use the full international format "
            "with your country code — e.g. [bold]+98 912 345 6789[/bold] (no 0 after the +)."
        )
        return None
    if not digits.isdigit() or not (10 <= len(digits) <= 15):
        console.print(
            "[bright_red]✘[/] That doesn't look like a phone number. "
            "Enter 10–15 digits including the country code, e.g. [bold]+989123456789[/bold]."
        )
        return None
    return "+" + digits


def _describe_code_delivery(sent) -> str:
    return CODE_DELIVERY_LABELS.get(type(sent.type).__name__, type(sent.type).__name__)


def _fmt_wait(seconds: int) -> str:
    if seconds >= 3600:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
    if seconds >= 60:
        return f"{seconds // 60}m {seconds % 60}s"
    return f"{seconds}s"


def _render_qr(url: str) -> str:
    """Render a login URL as a terminal-scannable ASCII QR code block."""
    buf = io.StringIO()
    qr = qrcode.QRCode(border=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(out=buf, invert=True)
    return buf.getvalue().rstrip("\n")


class TelegramConnection:
    """Owns the Telethon client and handles connect / login / disconnect."""

    def __init__(self, api_id: int, api_hash: str, session_path: str):
        self.client = TelegramClient(session_path, api_id, api_hash)
        self.session_path = session_path
        self._logged_in_interactively = False

    async def start(self) -> None:
        """Connect and authenticate, prompting for phone/code/2FA if needed."""
        await self.client.connect()

        if not await self.client.is_user_authorized():
            console.print("")
            console.print(Panel(
                "[bold bright_yellow]First run — interactive login required.[/]\n"
                "[dim]Your session will be saved to the Docker volume and reused "
                "automatically afterwards.[/]",
                title="[bold bright_white]🔐  Login[/]",
                border_style="bright_yellow",
            ))
            await self._login_interactively()
            self._logged_in_interactively = True

        # the session file holds the auth key (= full account access):
        # keep it readable by the owner only
        self._restrict_session_perms()

        await self.client.get_me()  # warm up the session

    def _restrict_session_perms(self) -> None:
        try:
            os.chmod(self.session_path + ".session", 0o600)
        except OSError:
            pass  # fresh/missing session file — nothing to lock down yet

    async def _login_interactively(self) -> None:
        from ..ui.menu import InteractiveMenu  # local import: ui layer stays optional

        menu = InteractiveMenu("How would you like to log in?", [
            ("📱  QR code  [bright_green](recommended)[/]", "scan with your phone — no code needed"),
            ("🔢  Phone number + code", "classic SMS / app-code login"),
        ])
        choice = menu.select()
        if choice is None:
            raise LoginAborted("Login cancelled at method selection.")

        if choice == 0:
            await self._login_via_qr()
        else:
            await self._login_via_code()

    # ── QR login (no SMS/code needed, immune to code-delivery rate limits) ──

    async def _login_via_qr(self) -> None:
        console.print("")
        console.print(Panel(
            "[bold white]1.[/] Open Telegram on your phone\n"
            "[bold white]2.[/] Go to  [bold bright_cyan]Settings → Devices → Link Desktop Device[/]\n"
            "[bold white]3.[/] Point the camera at the QR code below\n\n"
            f"[dim]The QR refreshes automatically. It never expires into an error —\n"
            "just keep this window open until the scan confirms.[/dim]",
            title="[bold bright_white]🔐  QR Login[/]",
            border_style="bright_cyan",
        ))

        while True:
            with console.status("[bright_cyan]Generating QR code…[/bright_cyan]"):
                qr = await self.client.qr_login()
            console.print(_render_qr(qr.url))

            try:
                await qr.wait(timeout=120)
                break  # scanned and authorized
            except SessionPasswordNeededError:
                await self._ask_2fa_password()
                break
            except TimeoutError:
                console.print("[dim]QR token expired — showing a fresh one…[/dim]\n")
                continue
            except FloodWaitError as e:
                raise LoginAborted(
                    f"Telegram asks to wait {_fmt_wait(e.seconds)} before retrying."
                )
            except RPCError as e:
                raise LoginAborted(f"QR login failed: {e}")

        console.print("[bright_green]✔[/] [bold]Login successful![/bold] "
                      "[dim]Saving session…[/dim]\n")

    # ── phone + code login ──────────────────────────────────────────────────

    async def _login_via_code(self) -> None:
        phone = await self._ask_phone()
        sent = await self._request_code(phone)

        while True:
            raw = console.input(
                "[bold cyan]Login code[/bold cyan] "
                "[dim](digits only · r = resend · blank = cancel)[/dim]: "
            ).strip()

            if raw == "":
                raise LoginAborted("Login cancelled at code prompt.")
            if raw.lower() in ("r", "resend"):
                sent = await self._request_code(phone, previous=sent)
                continue
            if not raw.isdigit():
                console.print(
                    "[bright_yellow]⚠[/] The login code is digits only (like [bold]24683[/bold]). "
                    "Try again, or press [bold]r[/bold] to resend."
                )
                continue

            try:
                await self.client.sign_in(phone=phone, code=raw)
                break
            except SessionPasswordNeededError:
                await self._ask_2fa_password()
                break
            except (PhoneCodeInvalidError, PhoneCodeExpiredError, PhoneCodeEmptyError) as e:
                reason = {
                    PhoneCodeExpiredError: "has expired",
                    PhoneCodeEmptyError: "was empty",
                }.get(type(e), "was not accepted")
                console.print(
                    f"[bright_yellow]⚠[/] That code {reason}. Make sure you use the "
                    "[bold]newest[/bold] code — Telegram shows it inside the app under "
                    "Telegram → Settings → Devices, or as a message from the service "
                    "notifications chat. Enter it again, or press [bold]r[/bold] to resend."
                )
                continue
            except PhoneNumberUnoccupiedError:
                raise LoginAborted(
                    "This phone number has no Telegram account. "
                    "Register it first with the official Telegram app."
                )
            except PhoneNumberBannedError:
                raise LoginAborted("This phone number is banned from Telegram.")
            except FloodWaitError as e:
                raise LoginAborted(
                    f"Too many attempts — Telegram asks to wait {_fmt_wait(e.seconds)} "
                    "before trying again."
                )
            except RPCError as e:
                console.print(f"[bright_red]✘[/] Telegram rejected the login: {e}")
                continue

        console.print("[bright_green]✔[/] [bold]Login successful![/bold] "
                      "[dim]Saving session…[/dim]\n")

    async def _ask_phone(self) -> str:
        while True:
            raw = console.input(
                "[bold cyan]Phone number[/bold cyan] "
                "[dim](international format, e.g. +989123456789)[/dim]: "
            )
            phone = normalize_phone(raw)
            if phone:
                return phone

    async def _request_code(self, phone: str, previous=None):
        """Request (or resend) a login code, with friendly flood handling."""
        action = "Resending" if previous else "Requesting"
        try:
            with console.status(f"[bright_cyan]{action} login code…[/bright_cyan]"):
                sent = await self.client.send_code_request(phone)
        except FloodWaitError as e:
            raise LoginAborted(
                f"Code delivery limit reached — please wait {_fmt_wait(e.seconds)} "
                "and run the app again."
            )
        except ApiIdInvalidError:
            raise LoginAborted(
                "API ID / API hash are invalid. Double-check TELEGRAM_API_ID and "
                "TELEGRAM_API_HASH in your .env file."
            )
        except RPCError as e:
            raise LoginAborted(
                f"Could not send a login code ({e}). If you've requested many codes "
                "recently, wait a few minutes before trying again."
            )

        console.print(
            f"[bright_green]✔[/] A fresh login code was sent via "
            f"[bold]{_describe_code_delivery(sent)}[/bold]."
        )
        if previous is not None:
            console.print("[dim]Previous codes are now invalid — use this newest one.[/dim]")
        return sent

    async def _ask_2fa_password(self) -> None:
        console.print("[dim]Two-step verification is enabled for this account.[/dim]")
        while True:
            password = getpass.getpass("2FA password (hidden input): ")
            try:
                await self.client.sign_in(password=password)
                return
            except PasswordHashInvalidError:
                console.print("[bright_yellow]⚠[/] Wrong password, try again.")
            except FloodWaitError as e:
                raise LoginAborted(
                    f"Too many password attempts — wait {_fmt_wait(e.seconds)} and retry."
                )

    @property
    def logged_in_interactively(self) -> bool:
        return self._logged_in_interactively

    async def stop(self) -> None:
        await self.client.disconnect()
