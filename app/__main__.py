"""Application entry point: `python -m app`."""

import asyncio

from .app import App
from .config import ConfigError, load_config
from .telegram import LoginAborted, TelegramConnection, TelegramService
from .ui.theme import make_console

console = make_console()


async def main() -> None:
    try:
        config = load_config()
    except ConfigError as e:
        console.print(f"[bold red]Configuration error:[/bold red]\n{e}")
        return

    connection = TelegramConnection(config.api_id, config.api_hash, config.session_path)
    try:
        try:
            await connection.start()
        except LoginAborted as e:
            console.print(f"[bold yellow]Login cancelled:[/bold yellow] {e}")
            return
        except Exception as e:
            console.print(f"[bold red]Login failed:[/bold red] {e}")
            return

        service = TelegramService(connection)
        app = App(service, live_feed=config.live_feed)
        if config.live_feed:
            # skip the NewMessage handler entirely when the feed is off —
            # it would otherwise fetch sender/chat for every incoming message
            service.register_message_handler(app.on_live_message)
        await app.run()
    finally:
        await connection.stop()
        console.print("[dim]Disconnected.🔴[/dim]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication terminated.")
