from datetime import datetime

from telethon import events, functions
from telethon.tl.types import (
    User, Channel, Chat,
    MessageMediaPhoto, MessageMediaDocument,
    MessageMediaPoll, MessageMediaGeo, MessageMediaContact,
)


def _detect_media_type(media) -> str | None:
    """Detect and return a human-readable label for message media."""
    if not media:
        return None
    if isinstance(media, MessageMediaPhoto):
        return "Photo"
    if isinstance(media, MessageMediaDocument):
        doc = getattr(media, "document", None)
        mime = getattr(doc, "mime_type", "") if doc else ""
        if "video" in mime:
            return "Video"
        if "audio" in mime or "ogg" in mime:
            return "Voice/Audio"
        if "image" in mime:
            return "Image"
        return "Document/File"
    if isinstance(media, MessageMediaPoll):
        return "Poll"
    if isinstance(media, MessageMediaGeo):
        return "Location"
    if isinstance(media, MessageMediaContact):
        return "Contact"
    return "Attachment"


class TelegramService:
    """High-level Telegram operations built on top of TelegramConnection."""

    def __init__(self, connection):
        self.client = connection.client

    async def get_me(self):
        """Get current authenticated user info."""
        return await self.client.get_me()

    async def send_message(self, target: str, text: str):
        """Send a text message to a channel, group, or user."""
        return await self.client.send_message(target, text)

    async def get_dialogs(self, limit: int = 50) -> list[dict]:
        """Fetch the user's active dialogs (channels, groups, DMs)."""
        dialogs = await self.client.get_dialogs(limit=limit)
        result = []

        for d in dialogs:
            entity = d.entity

            # Determine entity type
            if isinstance(entity, Channel):
                entity_type = "Channel" if entity.broadcast else "Group"
            elif isinstance(entity, Chat):
                entity_type = "Group"
            elif isinstance(entity, User):
                entity_type = "Bot" if getattr(entity, "bot", False) else "User"
            else:
                entity_type = "User"

            # Last message preview
            last_msg_text = ""
            if d.message:
                last_msg_text = d.message.message or ""
                if not last_msg_text:
                    media_label = _detect_media_type(d.message.media)
                    if media_label:
                        last_msg_text = f"[{media_label}]"

            date_str = d.date.strftime("%Y-%m-%d %H:%M") if d.date else ""

            result.append({
                "id": d.id,
                "title": d.name or "Unknown",
                "username": getattr(entity, "username", "") or "",
                "type": entity_type,
                "unread_count": d.unread_count,
                "pinned": d.pinned,
                "last_message": last_msg_text,
                "date": date_str,
            })

        return result

    async def get_channel_messages(self, target: str, limit: int = 20) -> list[dict]:
        """Fetch recent posts/messages from a channel or chat."""
        messages = await self.client.get_messages(target, limit=limit)
        result = []

        for msg in messages:
            if not msg:
                continue

            sender_name = "Unknown"
            username = ""
            if msg.sender:
                if isinstance(msg.sender, User):
                    sender_name = (
                        f"{msg.sender.first_name or ''} {msg.sender.last_name or ''}".strip()
                        or "User"
                    )
                    username = msg.sender.username or ""
                elif isinstance(msg.sender, (Channel, Chat)):
                    sender_name = getattr(msg.sender, "title", "Channel")
                    username = getattr(msg.sender, "username", "") or ""

            date_str = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else ""

            result.append({
                "id": msg.id,
                "date": date_str,
                "sender": sender_name,
                "username": username,
                "text": msg.message or "",
                "views": getattr(msg, "views", None),
                "media_type": _detect_media_type(msg.media),
                "forwards": getattr(msg, "forwards", None),
            })

        return result

    async def get_channel_info(self, target: str) -> dict:
        """Fetch full channel metadata (title, subscribers, description)."""
        entity = await self.client.get_entity(target)

        full = None
        if isinstance(entity, Channel):
            full = await self.client(functions.channels.GetFullChannelRequest(entity))

        title = getattr(entity, "title", getattr(entity, "first_name", "Chat"))
        username = getattr(entity, "username", "") or ""

        if full:
            participants_count = getattr(full.full_chat, "participants_count", None)
            about = getattr(full.full_chat, "about", "") or ""
        else:
            participants_count = getattr(entity, "participants_count", None)
            about = ""

        if isinstance(entity, Channel) and entity.broadcast:
            entity_type = "Channel"
        elif isinstance(entity, (Channel, Chat)):
            entity_type = "Group"
        else:
            entity_type = "User"

        return {
            "id": entity.id,
            "title": title,
            "username": username,
            "type": entity_type,
            "participants_count": participants_count,
            "about": about,
        }

    async def join_channel(self, target: str):
        """Join a public channel or group."""
        return await self.client(functions.channels.JoinChannelRequest(target))

    async def leave_channel(self, target: str):
        """Leave a channel or group."""
        return await self.client(functions.channels.LeaveChannelRequest(target))

    def register_message_handler(self, callback):
        """Register a callback for live incoming messages."""

        @self.client.on(events.NewMessage)
        async def handler(event):
            sender = await event.get_sender()

            first_name = ""
            last_name = ""
            sender_id = ""

            if isinstance(sender, User):
                first_name = sender.first_name or ""
                last_name = sender.last_name or ""
                sender_name = f"{first_name} {last_name}".strip() or "User"
                username = sender.username or ""
                sender_id = sender.id
            elif isinstance(sender, (Channel, Chat)):
                sender_name = getattr(sender, "title", "Channel")
                username = getattr(sender, "username", "") or ""
                sender_id = sender.id
            else:
                sender_name = "Unknown"
                username = ""

            chat = await event.get_chat()
            chat_title = (
                getattr(chat, "title", None)
                or getattr(chat, "first_name", None)
                or "Private Chat"
            )
            is_channel = isinstance(chat, Channel) and chat.broadcast

            await callback({
                "id": event.id,
                "sender": sender_name,
                "first_name": first_name,
                "last_name": last_name,
                "sender_id": sender_id,
                "username": username,
                "text": event.text or "",
                "chat_id": event.chat_id,
                "chat_title": chat_title,
                "is_channel": is_channel,
                "media_type": _detect_media_type(event.message.media),
                "date": datetime.now().strftime("%H:%M"),
            })