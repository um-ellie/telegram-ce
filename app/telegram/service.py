"""High-level Telegram operations exposed to the UI layer."""

from collections import Counter
from datetime import datetime, timezone

from telethon import events, functions
from telethon.tl.types import (
    Channel, Chat, User,
    MessageMediaPhoto, MessageMediaDocument,
    MessageMediaPoll, MessageMediaGeo, MessageMediaContact,
    MessageMediaWebPage,
)

MEDIA_ICONS = {
    "Photo": "🖼️",
    "Video": "🎬",
    "Voice/Audio": "🎧",
    "Image": "🖼️",
    "Document/File": "📄",
    "Poll": "📊",
    "Location": "📍",
    "Contact": "👤",
    "Web Link": "🔗",
    "Attachment": "📎",
}


def detect_media_type(media) -> str | None:
    """Return a human-readable label for message media."""
    if not media:
        return None
    if isinstance(media, MessageMediaPhoto):
        return "Photo"
    if isinstance(media, MessageMediaDocument):
        doc = getattr(media, "document", None)
        mime = getattr(doc, "mime_type", "") or ""
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
    if isinstance(media, MessageMediaWebPage):
        return "Web Link"
    return "Attachment"


def media_icon(media_type: str | None) -> str:
    if not media_type:
        return ""
    return MEDIA_ICONS.get(media_type, "📎")


def _entity_type(entity) -> str:
    if isinstance(entity, Channel):
        return "Channel" if entity.broadcast else "Group"
    if isinstance(entity, Chat):
        return "Group"
    if isinstance(entity, User):
        return "Bot" if getattr(entity, "bot", False) else "User"
    return "User"


def _sender_display(sender) -> tuple[str, str]:
    """Return (display_name, username) for a sender entity."""
    if sender is None:
        return "Unknown", ""
    if isinstance(sender, User):
        name = f"{sender.first_name or ''} {sender.last_name or ''}".strip() or "User"
        return name, sender.username or ""
    if isinstance(sender, (Channel, Chat)):
        return getattr(sender, "title", "Chat"), getattr(sender, "username", "") or ""
    return "Unknown", ""


def _localize(date) -> datetime | None:
    """Assume naive timestamps are UTC, then convert to the local timezone."""
    if date is None:
        return None
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    return date.astimezone()


def _fmt_date(date) -> str:
    d = _localize(date)
    return d.strftime("%Y-%m-%d %H:%M") if d else ""


def _fmt_time(date) -> str:
    d = _localize(date)
    return d.strftime("%H:%M") if d else ""


class TelegramService:
    """Every Telegram operation the UI needs, returned as plain dicts."""

    def __init__(self, connection):
        self.client = connection.client

    # ── account ────────────────────────────────────────────────────────────

    async def me_info(self) -> dict:
        me = await self.client.get_me()
        return {
            "id": me.id,
            "name": f"{me.first_name or ''} {me.last_name or ''}".strip() or "User",
            "username": me.username or "",
            "phone": f"+{me.phone}" if me.phone else "Hidden",
            "premium": bool(getattr(me, "premium", False)),
        }

    async def stats(self) -> dict:
        """Aggregate account statistics across all dialogs."""
        dialogs = await self.client.get_dialogs(limit=None)
        counts = Counter(_entity_type(d.entity) for d in dialogs)
        return {
            "total": len(dialogs),
            "channels": counts["Channel"],
            "groups": counts["Group"],
            "users": counts["User"],
            "bots": counts["Bot"],
            "unread": sum(d.unread_count for d in dialogs),
            "pinned": sum(1 for d in dialogs if d.pinned),
        }

    # ── dialogs ────────────────────────────────────────────────────────────

    async def get_dialogs(self, limit: int = 50) -> list[dict]:
        dialogs = await self.client.get_dialogs(limit=limit)
        return [
            {
                "id": d.id,
                "title": d.name or "Unknown",
                "username": getattr(d.entity, "username", "") or "",
                "type": _entity_type(d.entity),
                "unread_count": d.unread_count,
                "pinned": d.pinned,
                "date": _fmt_date(d.date),
            }
            for d in dialogs
        ]

    async def mark_read(self, target: str | int) -> None:
        await self.client.send_read_acknowledge(target)

    # ── messages ───────────────────────────────────────────────────────────

    async def get_messages(self, target: str | int, limit: int = 20) -> list[dict]:
        messages = await self.client.get_messages(target, limit=limit)
        result = []
        for msg in messages:
            if not msg:
                continue
            sender, username = _sender_display(msg.sender)
            result.append({
                "id": msg.id,
                "date": _fmt_date(msg.date),
                "time": _fmt_time(msg.date),
                "sender": sender,
                "username": username,
                "text": msg.message or "",
                "views": getattr(msg, "views", None),
                "forwards": getattr(msg, "forwards", None),
                "media_type": detect_media_type(msg.media),
                "out": bool(msg.out),
            })
        return result

    async def send_message(self, target: str | int, text: str):
        return await self.client.send_message(target, text)

    # ── entities ───────────────────────────────────────────────────────────

    async def entity_info(self, target: str | int) -> dict:
        entity = await self.client.get_entity(target)

        full = None
        if isinstance(entity, Channel):
            full = await self.client(functions.channels.GetFullChannelRequest(entity))

        title = getattr(entity, "title", None) or getattr(entity, "first_name", "Chat")
        username = getattr(entity, "username", "") or ""

        if full:
            participants = getattr(full.full_chat, "participants_count", None)
            about = getattr(full.full_chat, "about", "") or ""
        else:
            participants = getattr(entity, "participants_count", None)
            about = ""

        return {
            "id": entity.id,
            "title": title,
            "username": username,
            "type": _entity_type(entity),
            "participants_count": participants,
            "about": about,
            "verified": bool(getattr(entity, "verified", False)),
        }

    async def join_channel(self, target: str | int):
        return await self.client(functions.channels.JoinChannelRequest(target))

    async def leave_channel(self, target: str | int):
        return await self.client(functions.channels.LeaveChannelRequest(target))

    # ── search ─────────────────────────────────────────────────────────────

    async def search_dialogs(self, query: str) -> list[dict]:
        query = query.lower()
        dialogs = await self.get_dialogs(limit=None)
        return [
            d for d in dialogs
            if query in d["title"].lower() or query in d["username"].lower()
        ]

    # ── live feed ──────────────────────────────────────────────────────────

    def register_message_handler(self, callback):
        """Forward every incoming message to `callback` as a plain dict.

        The handler never raises: a broken message or a rendering hiccup must
        not disturb the running interactive session.
        """
        @self.client.on(events.NewMessage)
        async def handler(event):
            try:
                sender = await event.get_sender()
                sender_name, username = _sender_display(sender)

                chat = await event.get_chat()
                chat_title = (
                    getattr(chat, "title", None)
                    or getattr(chat, "first_name", None)
                    or "Private Chat"
                )

                await callback({
                    "id": event.id,
                    "sender": sender_name,
                    "username": username,
                    "text": event.text or "",
                    "chat_title": chat_title,
                    "chat_id": event.chat_id,
                    "is_channel": isinstance(chat, Channel) and chat.broadcast,
                    "media_type": detect_media_type(event.message.media),
                    "time": datetime.now().strftime("%H:%M"),
                })
            except Exception:
                pass  # better to drop one live message than to break the session
