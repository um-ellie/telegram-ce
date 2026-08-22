"""Application banner and header rendering."""

from .theme import make_console
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

from .theme import ACCENT, ACCENT_2, BOX, TITLE

from .. import __version__

console = make_console()

BANNER_ART = Text()
for i, line in enumerate([
    " ████████╗███████╗██╗     ███████╗██████╗ ██████╗  █████╗ ███╗   ███╗  ██████╗███████╗",
    " ╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║ ██╔════╝██╔════╝",
    "     ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██╔████╔██║ ██║     █████╗  ",
    "     ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║ ██║     ██╔══╝  ",
    "     ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║ ╚██████╗███████╗",
    "     ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═════╝╚══════╝",
]):
    gradient = ["bright_cyan", "bright_blue", "bright_magenta", "bright_blue", "bright_cyan", "cyan"][i]
    BANNER_ART.append(line + "\n", style=f"bold {gradient}")


def render_banner(me: dict | None = None) -> None:
    """Render the startup banner with the signed-in account card."""
    console.print(BANNER_ART, justify="center")
    console.print(
        f"✦ Terminal Edition · v{__version__} · "
        "Type [bold green]/help[/bold green] anytime",
        justify="center",
        style="dim",
    )

    if me:
        name = escape(me["name"])
        username = f"@{escape(me['username'])}" if me["username"] else "no username"
        premium = " ✦ Premium" if me.get("premium") else ""
        body = (
            f"[bold bright_green]● Signed in[/bold bright_green]  "
            f"[bold white]{name}[/bold white]{premium}\n"
            f"[bright_cyan]{username}[/bright_cyan]  [dim]·[/dim]  "
            f"[bright_yellow]{me['phone']}[/bright_yellow]  [dim]·[/dim]  "
            f"[dim]ID {me['id']}[/dim]"
        )
        console.print("")
        console.print(Panel(body, border_style=ACCENT, box=BOX,
                            title=f"[{TITLE}]Telegram CE[/]", subtitle=f"[dim]{username}[/dim]"))
    console.print("")
