"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.environ.get("TELEGRAM_CE_DATA_DIR", "/app/data")


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    api_id: int
    api_hash: str
    session_path: str
    live_feed: bool = True


def load_config() -> Config:
    """Load and validate Telegram API credentials from the environment."""
    api_id = os.getenv("TELEGRAM_API_ID", "").strip()
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()

    if not api_id or not api_hash:
        raise ConfigError(
            "Telegram credentials are missing.\n"
            "Get your API ID and API hash from https://my.telegram.org,\n"
            "then set TELEGRAM_API_ID and TELEGRAM_API_HASH in your .env file."
        )

    if not api_id.isdigit():
        raise ConfigError("TELEGRAM_API_ID must be a numeric value.")

    os.makedirs(DATA_DIR, exist_ok=True)

    return Config(
        api_id=int(api_id),
        api_hash=api_hash,
        session_path=os.path.join(DATA_DIR, "telegram_ce_session"),
        live_feed=os.getenv("TELEGRAM_CE_LIVE_FEED", "1").strip().lower()
        in ("1", "true", "yes", "on"),
    )
