import asyncio
import sys
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED, DOUBLE, HEAVY
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

console = Console()

BANNER_ART = """
[bold cyan]  ████████╗███████╗██╗     ███████╗██████╗ ██████╗  █████╗ ███╗   ███╗  ██████╗███████╗[/bold cyan]
[bold blue]  ╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║ ██╔════╝██╔════╝[/bold blue]
[bold magenta]     ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██╔████╔██║ ██║     █████╗  [/bold magenta]
[bold violet]     ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║ ██║     ██╔══╝  [/bold violet]
[bold cyan]     ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║ ╚██████╗███████╗[/bold cyan]
[bold cyan]     ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═════╝╚══════╝[/bold cyan]
"""


def render_banner(user_info: dict | None = None):
    """Render the application banner and current account information."""
    console.print(BANNER_ART)

    user_details = "[yellow]Fetching user account details...[/yellow]"
    if user_info:
        name = (
            f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
            or "User"
        )
        username = (
            f"@{user_info.get('username')}"
            if user_info.get("username")
            else "[italic dim]No Username[/italic dim]"
        )
        phone = f"+{user_info.get('phone')}" if user_info.get("phone") else "Hidden"
        user_id = user_info.get("id", "-")

        user_details = (
            f"[bold green]Name:[/bold green] [bold white]{name}[/bold white]  |  "
            f"[bold cyan]Username:[/bold cyan] {username}  |  "
            f"[bold yellow]ID:[/bold yellow] [dim]{user_id}[/dim]  |  "
            f"[bold magenta]Phone:[/bold magenta] {phone}"
        )

    header_panel = Panel(
        user_details,
        title="[bold green]Connected to Telegram (Telegram CE)[/bold green]",
        subtitle="[dim]Type /help to display available commands[/dim]",
        border_style="cyan",
        box=ROUNDED,
    )
    console.print(header_panel)


def render_help():
    """Render the help menu with all available commands."""
    table = Table(
        title="Telegram CE Terminal - Commands Guide",
        box=ROUNDED,
        border_style="bright_blue",
    )
    table.add_column("Command", style="bold cyan", no_wrap=True)
    table.add_column("Parameters", style="yellow")
    table.add_column("Description", style="white")

    table.add_row("/channels (or /dialogs)", "-", "Display all active channels, groups, and direct chats")
    table.add_row("/view (or /read)", "<@username | ID | #index>", "View recent posts from a channel or chat")
    table.add_row("/info", "<@username | ID>", "Display metadata and subscriber count of a channel")
    table.add_row("/send", "<@target> <message>", "Send a message to a channel, group, or user")
    table.add_row("/join", "<@channel>", "Join a public channel or group")
    table.add_row("/leave", "<@channel>", "Leave a channel or group")
    table.add_row("/search", "<query>", "Search through your channels and chats")
    table.add_row("/clear", "-", "Clear the terminal screen")
    table.add_row("/help", "-", "Display this help menu")
    table.add_row("/quit (or /exit)", "-", "Safely exit the application")

    console.print(table)


class TerminalUI:
    """Interactive terminal interface for Telegram CE."""

    def __init__(self):
        self.cached_dialogs = []
        self.user_info = None

    def set_user_info(self, me_entity):
        """Store current authenticated user info for display."""
        if me_entity:
            self.user_info = {
                "id": me_entity.id,
                "first_name": getattr(me_entity, "first_name", ""),
                "last_name": getattr(me_entity, "last_name", ""),
                "username": getattr(me_entity, "username", ""),
                "phone": getattr(me_entity, "phone", ""),
            }

    async def show_message(self, message: dict) -> None:
        """Display a live incoming message using plain text output.

        Uses print() instead of Rich to avoid ANSI escape code rendering
        issues in terminals that do not fully support them."""
        sender = message.get("sender", "Unknown")
        username = message.get("username", "")
        text = message.get("text", "")
        chat = message.get("chat_title", "")
        is_channel = message.get("is_channel", False)
        media_type = message.get("media_type")
        time_str = message.get("date", datetime.now().strftime("%H:%M"))
        msg_id = message.get("id", "")
        first_name = message.get("first_name", "")
        last_name = message.get("last_name", "")
        chat_id = message.get("chat_id", "")

        separator = "=" * 60

        # Build structured sender info header
        msg_type = "Channel" if is_channel else "Message"
        header_parts = []

        if first_name:
            header_parts.append(f"First Name: {first_name}")
        if last_name:
            header_parts.append(f"Last Name: {last_name}")
        if not first_name and not last_name:
            header_parts.append(f"Name: {sender}")
        if username:
            header_parts.append(f"Username: @{username}")
        header_parts.append(f"Time: {time_str}")
        if chat:
            header_parts.append(f"Chat: {chat}")
        if msg_id:
            header_parts.append(f"Msg ID: {msg_id}")
        if chat_id:
            header_parts.append(f"Chat ID: {chat_id}")
        header_parts.append(f"Type: {msg_type}")

        # Prepare message body
        if text:
            body = text
        elif media_type:
            body = f"[{media_type}]"
        else:
            body = "[Empty message]"

        # Output with plain print() to avoid ANSI rendering issues
        print(f"\n{separator}")
        print(f"  {' | '.join(header_parts)}")
        print(f"{'-' * 60}")
        for line in body.split("\n"):
            print(f"  {line}")
        print(separator)

    async def display_dialogs(self, service, limit: int = 40):
        """Fetch and render the user's active channels and chats."""
        with console.status("[bold green]Fetching channels and chats...[/bold green]"):
            try:
                dialogs = await service.get_dialogs(limit=limit)
                self.cached_dialogs = dialogs
            except Exception as e:
                console.print(f"[bold red]Error fetching chat list:[/bold red] {e}")
                return

        table = Table(
            title=f"Channels & Active Chats ({len(dialogs)} items)",
            box=HEAVY,
            border_style="cyan",
            header_style="bold magenta",
        )

        table.add_column("#", style="dim", justify="center")
        table.add_column("Type", justify="center")
        table.add_column("Name / Title", style="bold white")
        table.add_column("Username (@)", style="cyan")
        table.add_column("Unread", justify="center")
        table.add_column("Last Activity", style="dim green")

        type_badges = {
            "Channel": "Channel",
            "Group": "Group",
            "Bot": "Bot",
            "User": "User",
        }

        for idx, d in enumerate(dialogs, 1):
            type_badge = type_badges.get(d["type"], "User")

            unread = d["unread_count"]
            unread_str = (
                f"[bold white on red] {unread} [/bold white on red]"
                if unread > 0
                else "[dim]0[/dim]"
            )
            if d["pinned"]:
                unread_str += " Pinned"

            username_str = f"@{d['username']}" if d["username"] else "-"

            table.add_row(
                str(idx), type_badge, d["title"],
                username_str, unread_str, d["date"],
            )

        console.print(table)
        console.print(
            "[dim]To view posts from a channel, type [/dim]"
            "[bold green]/view @username[/bold green]"
            "[dim] or [/dim]"
            "[bold green]/view #index[/bold green]\n"
        )

    async def display_channel_messages(self, service, target: str, limit: int = 15):
        """Display posts/messages from a channel or chat."""
        # Resolve numeric index to a channel identifier
        if target.isdigit() and self.cached_dialogs:
            idx = int(target) - 1
            if 0 <= idx < len(self.cached_dialogs):
                d = self.cached_dialogs[idx]
                target = d["username"] if d["username"] else str(d["id"])

        with console.status(f"[bold cyan]Fetching posts from {target}...[/bold cyan]"):
            try:
                messages = await service.get_channel_messages(target, limit=limit)
            except Exception as e:
                console.print(f"[bold red]Error fetching channel posts:[/bold red] {e}")
                return

        console.print(
            f"\n[bold yellow]Recent {len(messages)} posts/messages from "
            f"[cyan]{target}[/cyan]:[/bold yellow]\n"
        )

        for msg in reversed(messages):
            sender = msg["sender"]
            username = f" (@{msg['username']})" if msg["username"] else ""
            date_str = msg["date"]
            views = msg["views"]
            media = msg["media_type"]
            text_content = msg["text"]

            footer_parts = [date_str]
            if views is not None:
                footer_parts.append(f"Views: {views:,}")
            if media:
                footer_parts.append(media)

            subtitle = " | ".join(footer_parts)
            body = text_content if text_content else f"[italic dim]{media or 'Empty message'}[/italic dim]"

            panel = Panel(
                body,
                title=f"[bold green]{sender}{username}[/bold green]",
                subtitle=f"[dim]{subtitle}[/dim]",
                border_style="blue",
                box=ROUNDED,
            )
            console.print(panel)

    async def display_channel_info(self, service, target: str):
        """Display channel metadata card."""
        with console.status(f"[bold cyan]Fetching metadata for {target}...[/bold cyan]"):
            try:
                info = await service.get_channel_info(target)
            except Exception as e:
                console.print(f"[bold red]Error fetching metadata:[/bold red] {e}")
                return

        title = info["title"]
        username = f"@{info['username']}" if info["username"] else "None"
        c_type = info["type"]
        count = (
            f"{info['participants_count']:,}"
            if info["participants_count"] is not None
            else "Unknown"
        )
        about = info["about"] or "No description provided."

        content = (
            f"[bold cyan]Title:[/bold cyan] {title}\n"
            f"[bold yellow]Username:[/bold yellow] {username}\n"
            f"[bold magenta]Type:[/bold magenta] {c_type}\n"
            f"[bold green]Members / Subscribers:[/bold green] {count}\n\n"
            f"[bold white]About / Description:[/bold white]\n[dim]{about}[/dim]"
        )

        panel = Panel(
            content,
            title=f"[bold green]Channel Info: {title}[/bold green]",
            border_style="yellow",
            box=DOUBLE,
        )
        console.print(panel)

    async def run(self, service) -> None:
        """Main interactive command loop."""
        try:
            me = await service.get_me()
            self.set_user_info(me)
        except Exception:
            pass

        render_banner(self.user_info)

        session = PromptSession()

        while True:
            try:
                with patch_stdout():
                    user_input = await session.prompt_async("TelegramCE > ")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold yellow]Exiting...[/bold yellow]")
                break

            command = user_input.strip()
            if not command:
                continue

            cmd_lower = command.lower()

            # /quit or /exit
            if cmd_lower in ("/quit", "/exit", "exit", "quit"):
                console.print("[bold yellow]Goodbye![/bold yellow]")
                break

            # /help
            elif cmd_lower == "/help":
                render_help()

            # /clear
            elif cmd_lower == "/clear":
                console.clear()
                render_banner(self.user_info)

            # /channels or /dialogs
            elif cmd_lower in ("/channels", "/dialogs", "/chats"):
                await self.display_dialogs(service)

            # /view or /read
            elif command.startswith(("/view ", "/read ")):
                parts = command.split(" ", 2)
                if len(parts) < 2:
                    console.print("[bold red]Invalid format.[/bold red] Example: /view @channel_username")
                    continue
                target = parts[1].lstrip("#")
                limit = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 15
                await self.display_channel_messages(service, target, limit)

            # /info
            elif command.startswith("/info "):
                target = command.split(" ", 1)[1]
                await self.display_channel_info(service, target)

            # /send
            elif command.startswith("/send "):
                parts = command.split(" ", 2)
                if len(parts) < 3:
                    console.print("[bold red]Invalid format.[/bold red] Example: /send @username Hello!")
                    continue
                target, text_to_send = parts[1], parts[2]
                with console.status(f"[bold cyan]Sending message to {target}...[/bold cyan]"):
                    try:
                        await service.send_message(target, text_to_send)
                        console.print(f"[bold green]Message sent to [cyan]{target}[/cyan].[/bold green]\n")
                    except Exception as e:
                        console.print(f"[bold red]Failed to send message:[/bold red] {e}\n")

            # /join
            elif command.startswith("/join "):
                target = command.split(" ", 1)[1]
                with console.status(f"[bold cyan]Joining {target}...[/bold cyan]"):
                    try:
                        await service.join_channel(target)
                        console.print(f"[bold green]Joined [cyan]{target}[/cyan].[/bold green]\n")
                    except Exception as e:
                        console.print(f"[bold red]Failed to join:[/bold red] {e}\n")

            # /leave
            elif command.startswith("/leave "):
                target = command.split(" ", 1)[1]
                with console.status(f"[bold cyan]Leaving {target}...[/bold cyan]"):
                    try:
                        await service.leave_channel(target)
                        console.print(f"[bold yellow]Left [cyan]{target}[/cyan].[/bold yellow]\n")
                    except Exception as e:
                        console.print(f"[bold red]Failed to leave:[/bold red] {e}\n")

            # /search
            elif command.startswith("/search "):
                query = command.split(" ", 1)[1].lower()
                if not self.cached_dialogs:
                    self.cached_dialogs = await service.get_dialogs(limit=100)

                filtered = [
                    d for d in self.cached_dialogs
                    if query in d["title"].lower() or query in d["username"].lower()
                ]

                if not filtered:
                    console.print(f"[bold yellow]No results matching '{query}'.[/bold yellow]")
                    continue

                table = Table(
                    title=f"Search results for '{query}'",
                    box=ROUNDED,
                    border_style="yellow",
                )
                table.add_column("Type", justify="center")
                table.add_column("Title", style="bold white")
                table.add_column("Username (@)", style="cyan")

                for d in filtered:
                    table.add_row(
                        d["type"], d["title"],
                        f"@{d['username']}" if d["username"] else "-",
                    )
                console.print(table)

            # Unknown command
            else:
                console.print(
                    "[bold yellow]Unknown command.[/bold yellow] "
                    "Type [bold green]/help[/bold green] for available commands."
                )