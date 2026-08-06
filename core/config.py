import os

from dotenv import load_dotenv

# Load .env file if present (use for local test and development)
load_dotenv()


def get_config() -> tuple[int, str]:
    """Load and validate Telegram API credentials from environment variables."""
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        raise RuntimeError(
            "Telegram credentials are missing. "
            "Set TELEGRAM_API_ID and TELEGRAM_API_HASH in your .env file."
        )

    try:
        return int(api_id), api_hash
    except ValueError:
        raise ValueError("TELEGRAM_API_ID must be a numeric value.")