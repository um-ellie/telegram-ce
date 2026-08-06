import asyncio
import sys

# Ensure src directory is on the import path
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))

from config import get_config
from telegram.client import TelegramConnection
from telegram.service import TelegramService


async def main():
    """Application entry point."""
    try:
        api_id, api_hash = get_config()
    except (RuntimeError, ValueError) as e:
        print(f"Configuration error: {e}")
        return

    connection = TelegramConnection(api_id, api_hash)
    await connection.start()

    service = TelegramService(connection)


    service.register_message_handler(ui.show_message)

    try:
        await ui.run(service)
    finally:
        await connection.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication terminated.")