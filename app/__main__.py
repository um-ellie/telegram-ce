"""Application entry point: `python -m app`."""

import asyncio

from .ui.theme import make_console

from .config import ConfigError, load_config
from .telegram import LoginAborted, TelegramConnection, TelegramService
from .app import App

console = make_console()


async def main() -> None:
    try:
        config = load_config()
    except ConfigError as e:
        console.print(f"[bold red]Configuration error:[/bold red]\n{e}")
        return

    connection = TelegramConnection(config.api_id, config.api_hash, config.session_path)
    try:
        await connection.start()
    except LoginAborted as e:
        console.print(f"[bold yellow]Login cancelled:[/bold yellow] {e}")
        await connection.stop()
        return
    except Exception as e:
        console.print(f"[bold red]Login failed:[/bold red] {e}")
        await connection.stop()
        return

    service = TelegramService(connection)
    app = App(service, live_feed=config.live_feed)
    service.register_message_handler(app.on_live_message)

    try:
        await app.run()
    finally:
        await connection.stop()
        console.print("[dim]Disconnected.🔴[/dim]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication terminated.")
