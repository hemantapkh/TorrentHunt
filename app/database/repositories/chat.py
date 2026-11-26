import datetime
from typing import Any

import sqlalchemy
from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.tl import types as tl_types

from database.models import (
    REACHABLE,
    Chat,
    ChatStatus,
    ChatStatusChange,
    ChatType,
    Referral,
    SearchStat,
    Setting,
    StatusSource,
    UnreachableReason,
)

# Activity that isn't a search refreshes last_active_at at most this often per chat.
TOUCH_INTERVAL = datetime.timedelta(minutes=5)


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def _aware(t: datetime.datetime | None) -> datetime.datetime | None:
    # SQLite returns naive datetimes; they're stored as UTC.
    return t.replace(tzinfo=datetime.UTC) if t is not None and t.tzinfo is None else t


def profile_of(entity: Any) -> dict[str, Any]:
    """The chats columns Telegram's view of a user, group or channel fills in."""
    if isinstance(entity, tl_types.User):
        profile = {
            "type": ChatType.PRIVATE,
            "first_name": entity.first_name,
            "last_name": entity.last_name,
            "username": entity.username,
            "is_premium": bool(entity.premium),
        }
        if entity.lang_code:  # only sent sometimes; don't wipe a known value
            profile["language_code"] = entity.lang_code
        return profile
    if isinstance(entity, tl_types.Chat):
        return {"type": ChatType.GROUP, "title": entity.title, "member_count": entity.participants_count}
    profile = {  # Channel: a supergroup or a broadcast channel
        "type": ChatType.SUPERGROUP if getattr(entity, "megagroup", False) else ChatType.CHANNEL,
        "title": entity.title,
        "username": getattr(entity, "username", None),
    }
    if getattr(entity, "participants_count", None) is not None:
        profile["member_count"] = entity.participants_count
    return profile


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ---- tracking -------------------------------------------------------------------

    async def upsert_from_event(
        self, event: Any, referrer: int | str | None = None, searched: bool = False,
    ) -> None:
        """Create or refresh the chat (and default settings) for an update.

        The referrer is first-touch: it's stored once and never overwritten, so the
        link that brought someone in stays attributed to them."""
        entity = await event.get_chat()
        now = _utcnow()
        chat = await self.session.get(Chat, event.chat_id)
        if chat is None:
            chat = Chat(id=event.chat_id, status=ChatStatus.MEMBER, created_at=now)
            self.session.add(chat)
            self.session.add(Setting(chat_id=event.chat_id))
        for key, value in profile_of(entity).items():
            setattr(chat, key, value)
        chat.profile_updated_at = now
        chat.last_active_at = now
        self._reactivate(chat)
        if referrer and await self.session.get(Referral, event.chat_id) is None:
            self.session.add(Referral(chat_id=event.chat_id, referrer=str(referrer)))
        if searched:
            await self._count_search(event.chat_id)

    async def touch(self, chat_id: int | None, searched: bool = False) -> None:
        """Record activity for a chat we already know (callbacks, commands, inline).

        Never creates a chat: someone using the bot inline, for instance, hasn't started
        it and can't be messaged."""
        if chat_id is None:
            return
        chat = await self.session.get(Chat, chat_id)
        if chat is None:
            return
        now = _utcnow()
        last = _aware(chat.last_active_at)
        if searched or last is None or now - last >= TOUCH_INTERVAL:
            chat.last_active_at = now
        self._reactivate(chat)
        if searched:
            await self._count_search(chat_id)

    async def _count_search(self, chat_id: int) -> None:
        stat = await self.session.get(SearchStat, chat_id)
        if stat is None:
            stat = SearchStat(chat_id=chat_id, search_count=0)
            self.session.add(stat)
        stat.search_count = (stat.search_count or 0) + 1
        stat.last_search_at = _utcnow()

    def _reactivate(self, chat: Chat) -> None:
        """The chat used the bot, so the bot can reach it again."""
        if chat.status not in REACHABLE:
            self._change(chat, ChatStatus.MEMBER, StatusSource.USER_ACTIVITY)
        if chat.unreachable_reason:
            chat.unreachable_reason = chat.unreachable_at = chat.migrated_to_chat_id = None

    # ---- reachability -----------------------------------------------------------------

    async def set_status(self, chat_id: int, status: ChatStatus, source: StatusSource) -> None:
        """Telegram reported the bot's membership in a chat. Known chats only."""
        chat = await self.session.get(Chat, chat_id)
        if chat is None:
            return
        if chat.status != status:
            self._change(chat, status, source)
        if status in REACHABLE and chat.unreachable_reason:
            chat.unreachable_reason = chat.unreachable_at = chat.migrated_to_chat_id = None

    async def set_added_by(self, chat_id: int, user_id: int | None) -> None:
        """Who added the bot to a group. Known chats only."""
        chat = await self.session.get(Chat, chat_id)
        if chat is not None and user_id:
            chat.added_by_user_id = user_id

    async def mark_unreachable(
        self,
        chat_id: int,
        reason: UnreachableReason,
        source: StatusSource,
        migrated_to: int | None = None,
    ) -> None:
        """Telegram can't deliver for a reason it has no member status for."""
        chat = await self.session.get(Chat, chat_id)
        if chat is None or chat.unreachable_reason == reason:
            return
        chat.unreachable_reason = reason
        chat.unreachable_at = _utcnow()
        chat.migrated_to_chat_id = migrated_to
        self.session.add(ChatStatusChange(chat_id=chat_id, status=reason, source=source))

    def _change(self, chat: Chat, status: ChatStatus, source: StatusSource) -> None:
        chat.status = status
        chat.status_changed_at = _utcnow()
        self.session.add(ChatStatusChange(chat_id=chat.id, status=status, source=source))

    # ---- settings and counts ------------------------------------------------------------

    async def exists(self, chat_id: int) -> bool:
        result = await self.session.execute(select(exists().where(Chat.id == chat_id)))
        return bool(result.scalar())

    async def get_language(self, chat_id: int) -> str | None:
        result = await self.session.execute(
            select(Setting.language).where(Setting.chat_id == chat_id),
        )
        return result.scalar()

    async def set_language(self, chat_id: int, language: str) -> None:
        await self.session.merge(Setting(chat_id=chat_id, language=language))

    async def get_restricted_mode(self, chat_id: int) -> bool | None:
        result = await self.session.execute(
            select(Setting.restricted_mode).where(Setting.chat_id == chat_id),
        )
        return result.scalar()

    async def set_restricted_mode(self, chat_id: int, value: bool) -> None:
        await self.session.execute(
            update(Setting).where(Setting.chat_id == chat_id).values(restricted_mode=value),
        )

    async def count(self) -> int:
        result = await self.session.execute(select(sqlalchemy.func.count(Chat.id)))
        return result.scalar_one()

    async def count_joined_today(self) -> int:
        midnight = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            select(sqlalchemy.func.count()).where(Chat.created_at >= midnight),
        )
        return result.scalar_one()
