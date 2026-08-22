"""The interactive application: menu hub, command loop, autocompletion."""

import difflib

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import PromptSession
from rich.markup import escape
from rich.table import Table

from .commands import ALIASES, COMMANDS
from .ui import InteractiveMenu
from .ui.theme import make_console
from .ui.banner import render_banner
from .ui.components import (
    busy, error, ok, render_dialogs, render_entity_info, render_live_message,
    render_messages, render_stats, warn,
)
from .ui.theme import ACCENT, ACCENT_2, BOX, DIM

console = make_console()

# prompt_toolkit formatted text (its own HTML dialect, not rich markup)
PROMPT = HTML(
    '✈️ <ansicyan><b>tg</b></ansicyan><ansibrightmagenta>·</ansibrightmagenta>'
    '<ansibrightmagenta><b>ce</b></ansibrightmagenta> <b>❯</b> '
)

HUB_ITEMS = [
    ("💬  Chats & Channels", "browse and open conversations"),
    ("📜  Read Messages",    "view recent posts of any chat"),
    ("📨  Send Message",     "reply or post to a chat"),
    ("🔍  Search",           "find chats by name or @username"),
("📊  Account Overview",  "channels, groups, unread stats"),
    ("ℹ️  Profile Info",      "inspect any channel or user"),
    ("➕  Join / ➖ Leave",   "manage channel memberships"),
    ("❓  Help",             "full command reference"),
    ("🚪  Quit",             "disconnect safely"),
]


class CommandCompleter(Completer):
    """Completes command names, and @usernames from cached dialogs."""

    def __init__(self, app: "App"):
        self.app = app

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        parts = text.split(" ")
        if len(parts) <= 1:
            for name, meta in COMMANDS.items():
                if name.startswith(parts[0]):
                    yield Completion(
                        name, start_position=-len(parts[0]),
                        display_meta=f"{meta['args']}  —  {meta['desc']}",
                    )
            return
        if parts[0] in ("/view", "/info", "/send", "/reply", "/join", "/leave", "/read"):
            frag = parts[-1]
            for d in self.app.cached_dialogs[:60]:
                cand = f"@{d['username']}" if d["username"] else d["title"]
                if cand.lower().startswith(frag.lower()) and frag:
                    yield Completion(
                        cand + " ", start_position=-len(frag),
                        display=d["title"], display_meta=d["type"],
                    )


class App:
    """Wires the service layer to the terminal UI."""

    def __init__(self, service, live_feed: bool = True):
        self.service = service
        self.live_feed_enabled = live_feed
        self.cached_dialogs: list[dict] = []
        self.me: dict | None = None

    # ── helpers ─────────────────────────────────────────────────────────────

    def _resolve_target(self, token: str) -> str:
        """Resolve #index (from the cached dialog list) to an entity handle."""
        token = token.lstrip("#").lstrip("@")
        if token.isdigit() and self.cached_dialogs:
            idx = int(token) - 1
            if 0 <= idx < len(self.cached_dialogs):
                d = self.cached_dialogs[idx]
                return f"@{d['username']}" if d["username"] else str(d["id"])
        return token if token.lstrip("-").isdigit() else f"@{token}"

    async def _ensure_dialogs(self, limit: int = 50) -> list[dict]:
        if not self.cached_dialogs:
            with busy("Loading chat list…"):
                self.cached_dialogs = await self.service.get_dialogs(limit=limit)
        return self.cached_dialogs

    async def _ask_target(self, action: str) -> str | None:
        """Pick a chat via the interactive menu (falls back to typing)."""
        dialogs = await self._ensure_dialogs()
        menu = InteractiveMenu(
            f"Select a chat to {action}",
            [(f"{d['type']:<7} {d['title']}", f"@{d['username']}" if d["username"] else f"id {d['id']}")
             for d in dialogs[:30]],
        )
        idx = menu.select()
        if idx is None:
            return None
        d = dialogs[:30][idx]
        return f"@{d['username']}" if d["username"] else str(d["id"])

    # ── actions ─────────────────────────────────────────────────────────────

    async def show_dialogs(self) -> None:
        with busy("Fetching channels and chats…"):
            try:
                self.cached_dialogs = await self.service.get_dialogs(limit=50)
            except Exception as e:
                error(f"Could not fetch chat list: {e}")
                return
        render_dialogs(self.cached_dialogs)

    async def view_messages(self, target: str, limit: int = 15) -> None:
        target = self._resolve_target(target)
        with busy(f"Fetching messages from {escape(target)}…"):
            try:
                messages = await self.service.get_messages(target, limit=limit)
            except Exception as e:
                error(f"Could not fetch messages: {e}")
                return
        render_messages(target, messages)

    async def entity_info(self, target: str) -> None:
        target = self._resolve_target(target)
        with busy(f"Fetching info for {escape(target)}…"):
            try:
                info = await self.service.entity_info(target)
            except Exception as e:
                error(f"Could not fetch info: {e}")
                return
        render_entity_info(info)

    async def send_message(self, target: str, text: str) -> None:
        target = self._resolve_target(target)
        with busy(f"Sending to {escape(target)}…"):
            try:
                await self.service.send_message(target, text)
            except Exception as e:
                error(f"Failed to send: {e}")
                return
        ok(f"Message sent to [bold]{escape(target)}[/bold]")

    async def join(self, target: str) -> None:
        with busy(f"Joining {escape(target)}…"):
            try:
                await self.service.join_channel(target)
            except Exception as e:
                error(f"Failed to join: {e}")
                return
        self.cached_dialogs = []
        ok(f"Joined [bold]{escape(target)}[/bold]")

    async def leave(self, target: str) -> None:
        with busy(f"Leaving {escape(target)}…"):
            try:
                await self.service.leave_channel(target)
            except Exception as e:
                error(f"Failed to leave: {e}")
                return
        self.cached_dialogs = []
        warn(f"Left [bold]{escape(target)}[/bold]")

    async def mark_read(self, target: str) -> None:
        target = self._resolve_target(target)
        try:
            await self.service.mark_read(target)
            ok(f"Marked [bold]{escape(target)}[/bold] as read")
        except Exception as e:
            error(f"Failed: {e}")

    async def search(self, query: str) -> None:
        with busy(f"Searching for '{escape(query)}'…"):
            try:
                results = await self.service.search_dialogs(query)
            except Exception as e:
                error(f"Search failed: {e}")
                return
        if not results:
            warn(f"No chats matching '{escape(query)}'")
            return
        render_dialogs(results)

    async def stats(self) -> None:
        with busy("Crunching your account numbers…"):
            try:
                stats = await self.service.stats()
            except Exception as e:
                error(f"Could not compute stats: {e}")
                return
        render_stats(stats)

    async def show_me(self) -> None:
        render_banner(await self.service.me_info())

    def render_help(self) -> None:
        table = Table(
            title="✈️  Telegram CE — Command Guide",
            box=BOX,
            border_style=ACCENT,
            header_style=f"bold {ACCENT_2}",
        )
        table.add_column("Command", style="bold bright_cyan", no_wrap=True)
        table.add_column("Arguments", style="bright_yellow")
        table.add_column("Description", style="white")
        for name, meta in COMMANDS.items():
            table.add_row(name, meta["args"], meta["desc"])
        console.print(table)
        console.print(
            f"[{DIM}]Tip: ↑/↓ recalls history · Tab completes commands and "
            "chat names · type[/] [bold green]/menu[/] "
            f"[{DIM}]for the interactive hub.[/]\n"
        )

    # ── live feed ───────────────────────────────────────────────────────────

    async def on_live_message(self, msg: dict) -> None:
        if not self.live_feed_enabled:
            return
        try:
            render_live_message(msg)
        except Exception:
            # a single malformed message must never break the event loop
            warn("Skipped a live message that could not be rendered.")

    # ── hub menu ────────────────────────────────────────────────────────────

    async def open_menu(self) -> None:
        menu = InteractiveMenu("Main Menu — what would you like to do?", HUB_ITEMS)
        choice = menu.select()
        if choice is None:
            return
        try:
            await self._run_menu_choice(choice)
        except Exception as e:
            error(f"{e}")

    async def _run_menu_choice(self, choice: int) -> None:
        if choice == 0:
            await self.show_dialogs()
        elif choice == 1:
            target = await self._ask_target("read")
            if target:
                await self.view_messages(target)
        elif choice == 2:
            target = await self._ask_target("message")
            if target:
                text = console.input(f"[bold cyan]Message for {target}:[/bold cyan] ")
                if text.strip():
                    await self.send_message(target, text)
        elif choice == 3:
            query = console.input("[bold cyan]Search chats:[/bold cyan] ").strip()
            if query:
                await self.search(query)
        elif choice == 4:
            await self.stats()
        elif choice == 5:
            target = console.input("[bold cyan]Channel/user (@username or id):[/bold cyan] ").strip()
            if target:
                await self.entity_info(target)
        elif choice == 6:
            sub = InteractiveMenu("Membership", [
                ("➕  Join a channel", "by @username"),
                ("➖  Leave a channel", "pick from your chats"),
            ])
            sub_choice = sub.select()
            if sub_choice == 0:
                target = console.input("[bold cyan]Channel to join (@username):[/bold cyan] ").strip()
                if target:
                    await self.join(target)
            elif sub_choice == 1:
                target = await self._ask_target("leave")
                if target:
                    await self.leave(target)
        elif choice == 7:
            self.render_help()
        elif choice == 8:
            raise SystemExit(0)

    # ── main loop ───────────────────────────────────────────────────────────

    async def run(self) -> None:
        with busy("Signing in…"):
            self.me = await self.service.me_info()
        render_banner(self.me)
        console.print(
            f"[{DIM}]Welcome, [bold]{escape(self.me['name'])}[/bold]! "
            "Type[/] [bold green]/menu[/] " f"[{DIM}]for the interactive hub or[/] "
            "[bold green]/help[/] " f"[{DIM}]for all commands.[/]\n"
        )

        session = PromptSession(history=InMemoryHistory(), complete_while_typing=True)

        while True:
            try:
                # raw=True: pass output through untouched — re-parsing ANSI
                # from the proxy corrupts escape codes on some terminals
                with patch_stdout(raw=True):
                    user_input = await session.prompt_async(
                        PROMPT, completer=CommandCompleter(self)
                    )
            except (KeyboardInterrupt, EOFError):
                console.print(f"\n[{ACCENT_2}]Goodbye! 👋[{ACCENT_2}]")
                break

            command = user_input.strip()
            if not command:
                continue

            try:
                if await self.dispatch(command):
                    break
            except SystemExit:
                console.print(f"\n[{ACCENT_2}]Goodbye! 👋[{ACCENT_2}]")
                break
            except Exception as e:
                error(f"Unexpected error: {e}")

    async def dispatch(self, command: str) -> bool:
        """Execute one command; returns True when the app should exit."""
        cmd, _, rest = command.partition(" ")
        cmd = ALIASES.get(cmd.lower(), cmd.lower())
        args = rest.strip()

        if cmd in ("/quit", "quit", "exit"):
            return True
        if cmd == "/help":
            self.render_help()
        elif cmd == "/menu":
            await self.open_menu()
        elif cmd == "/clear":
            console.clear()
            render_banner(self.me)
        elif cmd in ("/chats",):
            await self.show_dialogs()
        elif cmd == "/view":
            if not args:
                warn("Usage: /view <@username | #index | id> [count]")
            else:
                parts = args.split()
                limit = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 15
                await self.view_messages(parts[0], limit)
        elif cmd == "/info":
            if args:
                await self.entity_info(args)
            else:
                warn("Usage: /info <@username | id>")
        elif cmd in ("/send", "/reply"):
            parts = args.split(" ", 1)
            if len(parts) < 2:
                warn(f"Usage: {cmd} <@target | #index> <message>")
            else:
                await self.send_message(parts[0], parts[1])
        elif cmd == "/join":
            if args:
                await self.join(args)
            else:
                warn("Usage: /join <@channel>")
        elif cmd == "/leave":
            if args:
                await self.leave(args)
            else:
                warn("Usage: /leave <@channel>")
        elif cmd == "/read":
            if args:
                await self.mark_read(args)
            else:
                warn("Usage: /read <@target | #index>")
        elif cmd == "/search":
            if args:
                await self.search(args)
            else:
                warn("Usage: /search <query>")
        elif cmd == "/stats":
            await self.stats()
        elif cmd == "/me":
            await self.show_me()
        else:
            close = difflib.get_close_matches(cmd, list(COMMANDS) + list(ALIASES), n=1, cutoff=0.6)
            hint = f" Did you mean [bold green]{close[0]}[/bold green]?" if close else ""
            warn(f"Unknown command '{cmd}'.{hint} "
                 "Type [bold green]/help[/bold green] for the guide.")
        return False
