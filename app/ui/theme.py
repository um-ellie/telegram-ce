"""Central color palette and box styles so the whole app looks coherent."""

import os

from rich.console import Console
from rich.box import ROUNDED, DOUBLE, HEAVY


def make_console() -> Console:
    """Shared console factory — TELEGRAM_CE_PLAIN=1 disables all colors for
    terminals that render ANSI escape codes as literal garbage."""
    plain = os.getenv("TELEGRAM_CE_PLAIN", "0").strip().lower() in ("1", "true", "yes", "on")
    return Console(no_color=plain)

# Palette
ACCENT = "bright_cyan"
ACCENT_2 = "bright_magenta"
SUCCESS = "bright_green"
WARN = "bright_yellow"
DANGER = "bright_red"
DIM = "dim"
TITLE = "bold bright_white"

BOX = ROUNDED
BOX_HEAVY = HEAVY
BOX_DOUBLE = DOUBLE

TYPE_STYLES = {
    "Channel": "bold bright_cyan",
    "Group": "bold bright_green",
    "User": "bold bright_blue",
    "Bot": "bold bright_magenta",
}
