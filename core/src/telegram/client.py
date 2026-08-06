import os

from telethon import TelegramClient


class TelegramConnection:
    """Manages the Telethon client connection lifecycle."""

    # Session file is stored in the persistent data volume
    _SESSION_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "..", "data",
    )

    def __init__(self, api_id: int, api_hash: str):
        session_dir = os.path.abspath(self._SESSION_DIR)
        os.makedirs(session_dir, exist_ok=True)
        session_path = os.path.join(session_dir, "my_account")

        self.client = TelegramClient(session_path, api_id, api_hash)

    async def start(self):
        """Connect and authenticate with Telegram."""
        await self.client.start()

    async def stop(self):
        """Disconnect from Telegram."""
        await self.client.disconnect()