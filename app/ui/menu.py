"""An arrow-key navigable menu rendered with rich, driven by raw tty input.

Falls back to plain numbered input when stdin is not an interactive tty
(e.g. piped input or unsupported terminals), so it never blocks the app.
"""

import os
import select
import sys
from io import StringIO

from rich.console import Console
from rich.panel import Panel

from .theme import ACCENT, ACCENT_2, DIM, TITLE, make_console

console = make_console()


def _read_key() -> str:
    """Read a single keypress (with ANSI arrow decoding) from a raw tty.

    Uses os.read on the fd directly: buffered sys.stdin would slurp the whole
    arrow-key sequence into userspace, making select() miss the follow-up bytes.
    """
    fd = sys.stdin.fileno()
    ch = os.read(fd, 1).decode(errors="ignore")
    if ch == "\x03":  # Ctrl+C in raw mode
        raise KeyboardInterrupt
    if ch == "":
        raise EOFError
    if ch == "\x1b":
        # distinguish a lone ESC from an arrow-key sequence
        ready, _, _ = select.select([fd], [], [], 0.05)
        if not ready:
            return "esc"
        if os.read(fd, 1).decode(errors="ignore") == "[":
            code = os.read(fd, 1).decode(errors="ignore")
            return {"A": "up", "B": "down"}.get(code, "other")
        return "other"
    if ch in ("\r", "\n"):
        return "enter"
    if ch.isdigit():
        return ch
    if ch in ("j", "k"):  # vim-style navigation
        return "down" if ch == "j" else "up"
    return "other"


class InteractiveMenu:
    """A sleek scrollable menu: ↑/↓ (or j/k) to move, Enter to select, Esc to cancel."""

    def __init__(self, title: str, items: list[tuple[str, str]]):
        """
        items: list of (label, hint) tuples; the chosen index is returned.
        """
        self.title = title
        self.items = items

    def _build_panel(self, selected: int) -> Panel:
        lines = []
        for i, (label, hint) in enumerate(self.items):
            if i == selected:
                lines.append(
                    f"[bold white on bright_blue] ❯ {label} [/bold white on bright_blue]"
                    f" [dim]{hint}[/dim]"
                )
            else:
                lines.append(f"[dim]   {label}[/dim]  [dim]{hint}[/dim]")
        footer = (
            f"[{DIM}]↑/↓ move[/]  [bold green]⏎ select[/] "
            f"[{DIM}]1-{len(self.items)} quick-pick[/]  [bold red]esc cancel[/]"
        )
        return Panel(
            "\n".join(lines),
            title=f"[{TITLE}]{self.title}[/]",
            subtitle=footer,
            border_style=ACCENT,
        )

    def _render_str(self, selected: int) -> str:
        """Render the menu into a real string with newlines — str(Panel) would
        just produce the object repr, which is what once printed garbage."""
        buf = StringIO()
        renderer = Console(file=buf, width=console.width, no_color=console.no_color)
        renderer.print(self._build_panel(selected))
        return buf.getvalue()

    def select(self) -> int | None:
        """Show the menu and return the selected index, or None if cancelled."""
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return self._fallback()

        import termios
        import tty

        selected = 0
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                rendered = self._render_str(selected)
                n_lines = rendered.count("\n")
                sys.stdout.write(rendered)
                sys.stdout.flush()

                key = _read_key()

                # jump back to the top of the menu and erase it before acting
                sys.stdout.write(f"\r\x1b[{n_lines}A\x1b[J")
                sys.stdout.flush()

                if key == "up":
                    selected = (selected - 1) % len(self.items)
                elif key == "down":
                    selected = (selected + 1) % len(self.items)
                elif key == "enter":
                    return selected
                elif key == "esc":
                    return None
                elif key.isdigit() and 1 <= int(key) <= len(self.items):
                    return int(key) - 1
                # any other key: fall through and redraw
        except (KeyboardInterrupt, EOFError):
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            sys.stdout.flush()

    def _fallback(self) -> int | None:
        console.print(Panel(
            "\n".join(f"  [bold bright_cyan]{i}[/].  {label}  [dim]{hint}[/dim]"
                      for i, (label, hint) in enumerate(self.items, 1)),
            title=f"[{TITLE}]{self.title}[/]",
            border_style=ACCENT_2,
        ))
        try:
            raw = input(f"Choose 1-{len(self.items)} (blank to cancel): ").strip()
        except (EOFError, KeyboardInterrupt):
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(self.items):
            return int(raw) - 1
        return None
