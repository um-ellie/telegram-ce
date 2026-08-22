"""Reusable rich renderers: dialogs table, message panels, info cards, stats."""

import textwrap

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .theme import ACCENT, ACCENT_2, BOX, BOX_DOUBLE, BOX_HEAVY, DANGER, DIM, SUCCESS, TYPE_STYLES, WARN, make_console

from ..telegram.service import media_icon

console = make_console()

# message bodies never stretch past this, even on very wide terminals
MAX_BODY_WIDTH = 56


def wrap_body(text: str, width: int = MAX_BODY_WIDTH) -> str:
    """Wrap a message body to a fixed, terminal-friendly width."""
    width = max(24, min(width, MAX_BODY_WIDTH))
    return "\n".join(
        textwrap.wrap(text, width=width, break_long_words=True, break_on_hyphens=False)
        or [""]
    )


def error(msg: str) -> None:
    console.print(f"[{DANGER}]✘ {msg}[/{DANGER}]")


def ok(msg: str) -> None:
    console.print(f"[{SUCCESS}]✔ {msg}[/{SUCCESS}]")


def warn(msg: str) -> None:
    console.print(f"[{WARN}]⚠ {msg}[/{WARN}]")


def busy(msg: str):
    return console.status(f"[{ACCENT}]{msg}[/{ACCENT}]", spinner="dots12")


def render_dialogs(dialogs: list[dict]) -> None:
    table = Table(
        title=f"📋  Chats & Channels  ·  {len(dialogs)}",
        box=BOX_HEAVY,
        border_style=ACCENT,
        header_style=f"bold {ACCENT_2}",
        title_style="bold bright_white",
    )
    table.add_column("#", style=DIM, justify="center", width=3)
    table.add_column("Type", justify="center", width=8)
    table.add_column("Name / Title", style="bold white", overflow="ellipsis", max_width=38)
    table.add_column("Username", style=ACCENT, overflow="ellipsis", max_width=22)
    table.add_column("Unread", justify="center", width=7)
    table.add_column("Last Activity", style="dim green", width=16)

    for idx, d in enumerate(dialogs, 1):
        badge = TYPE_STYLES.get(d["type"], "white")
        type_cell = f"[{badge}]{d['type']}[/{badge}]"

        unread = d["unread_count"]
        unread_cell = (
            f"[bold white on bright_red] {unread} [/bold white on bright_red]"
            if unread > 0 else f"[{DIM}]·[/]"
        )

        name = ("📌 " if d["pinned"] else "") + escape(d["title"])
        username = f"@{escape(d['username'])}" if d["username"] else f"[{DIM}]—[/{DIM}]"

        table.add_row(str(idx), type_cell, name, username, unread_cell, d["date"])

    console.print(table)
    console.print(
        f"[{DIM}]Open one with[/] [bold green]/view #index[/] "
        f"[{DIM}]or[/] [bold green]/view @username[/]\n"
    )


def render_messages(target: str | int, messages: list[dict]) -> None:
    console.print(
        Panel(
            f"[bold bright_white]📜  {len(messages)} recent messages[/]"
            f"[{DIM}]  ·  oldest → newest[/]",
            border_style=ACCENT_2, box=BOX,
            expand=False, width=min(78, console.width),
        )
    )
    for msg in reversed(messages):
        sender = escape(msg["sender"])
        at = f" [dim](@{escape(msg['username'])})[/dim]" if msg["username"] else ""
        icon = media_icon(msg["media_type"])

        footer = [msg["time"] or msg["date"]]
        if msg["views"] is not None:
            footer.append(f"👁 {msg['views']:,}")
        if msg["forwards"]:
            footer.append(f"↻ {msg['forwards']:,}")
        if msg["media_type"]:
            footer.append(f"{icon} {msg['media_type']}")

        if msg["text"]:
            body = Text(wrap_body(msg["text"]))
        else:
            body = Text(
                f"{icon or '📎'} {msg['media_type'] or 'Empty message'}",
                style="italic dim",
            )
        style = SUCCESS if msg["out"] else ACCENT

        title = f"{sender}{at}" + ("  [dim]· you[/dim]" if msg["out"] else "")
        console.print(Panel(
            body,
            title=f"[bold {style}]{title}[/bold {style}]",
            subtitle=f"[dim]{' | '.join(footer)}[/dim]",
            border_style=style,
            box=BOX,
            expand=False,
            width=min(MAX_BODY_WIDTH + 6, console.width),
        ))
    console.print(f"[{DIM}]Reply with[/] [bold green]/send {escape(str(target))} <message>[/]\n")


def render_entity_info(info: dict) -> None:
    title = escape(info["title"])
    username = f"@{escape(info['username'])}" if info["username"] else "—"
    count = f"{info['participants_count']:,}" if info["participants_count"] else "Unknown"
    verified = "  ✔️ verified" if info["verified"] else ""

    content = (
        f"[bold bright_cyan]Title[/]      {title}{verified}\n"
        f"[bold bright_yellow]Username[/]   {username}\n"
        f"[bold bright_magenta]Type[/]       {info['type']}\n"
        f"[bold bright_green]Members[/]    {count}\n"
        f"[bold bright_blue]ID[/]          [dim]{info['id']}[/dim]\n\n"
        f"[bold white]About[/]\n[dim]{escape(info['about'] or 'No description provided.')}[/dim]"
    )
    console.print(Panel(
        content,
        title=f"[bold bright_green]ℹ  {title}[/]",
        border_style=WARN,
        box=BOX_DOUBLE,
    ))


def render_stats(stats: dict) -> None:
    table = Table(box=BOX, border_style=ACCENT_2, show_header=False, pad_edge=False)
    table.add_column("Metric", style="bold white", min_width=16)
    table.add_column("Value", style=ACCENT, justify="right")

    rows = [
        ("📡 Channels", stats["channels"]),
        ("👥 Groups", stats["groups"]),
        ("👤 Direct Chats", stats["users"]),
        ("🤖 Bots", stats["bots"]),
        ("📌 Pinned", stats["pinned"]),
        ("✉️ Unread", stats["unread"]),
    ]
    for label, value in rows:
        table.add_row(label, f"{value:,}")

    console.print(Panel(
        table,
        title=f"[bold bright_white]📊  Account Overview  ·  {stats['total']:,} chats total[/]",
        border_style=ACCENT, box=BOX_HEAVY,
    ))


def render_live_message(msg: dict) -> None:
    """Render an incoming live message: compact, wrapped, never full-width."""
    icon = media_icon(msg["media_type"])
    tag = "📢" if msg["is_channel"] else "💬"

    if msg["text"]:
        body = Text(wrap_body(msg["text"]))
    else:
        body = Text(
            f"{icon or '📎'} {msg['media_type'] or 'Attachment'}", style="dim"
        )

    # header by chat type: channels post as themselves; in DMs (positive peer
    # id) the chat and the sender are the same person, so show it once
    chat, sender = escape(msg["chat_title"].strip()), escape(msg["sender"].strip())
    at = f" [dim]@{escape(msg['username'])}[/dim]" if msg["username"] else ""
    is_dm = (msg.get("chat_id") or 0) > 0
    if msg["is_channel"] or not sender or is_dm or chat.lower() == sender.lower():
        header = f"{tag} {sender or chat}{at}"
    else:
        header = f"{tag} {chat} [dim]·[/] {sender}{at}"

    console.print(Panel(
        body,
        title=f"[bold bright_magenta]{header}[/bold bright_magenta]",
        subtitle=f"[dim]{msg['time']}[/dim]",
        border_style=ACCENT_2,
        box=BOX,
        expand=False,
        width=min(MAX_BODY_WIDTH + 6, console.width),
    ))
    console.print()
