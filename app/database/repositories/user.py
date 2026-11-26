import datetime
from typing import Any

import sqlalchemy
from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.tl import types as tl_types

from database.models import (
    REACHABLE,
    ChatStatus,
    ChatStatusChange,
    Setting,
    StatusSource,
    UnreachableReason,
    User,
)

# Activity that isn't a search refreshes last_active at most this often per chat.
TOUCH_INTERVAL = datetime.timedelta(minutes=5)


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def _utcnow_naive() -> datetime.datetime:
    # join_date / last_active are TIMESTAMP WITHOUT TIME ZONE: store UTC there.
    return _utcnow().replace(tzinfo=None)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ---- tracking -------------------------------------------------------------------

    async def upsert_from_event(
        self, event: Any, referrer: int | str | None = None, searched: bool = False,
    ) -> None:
        """Create or refresh the chat (and default settings) for an update.

        The referrer is first-touch: it's stored once and never overwritten, so the
        link that brought someone in stays attributed to them."""
        chat = await event.get_chat()
        profile: dict[str, Any] = {}

        if isinstance(chat, tl_types.User):
            user_type = "PRIVATE"
            names = {"username": chat.username, "first_name": chat.first_name, "last_name": chat.last_name}
            profile = {
                k: v
                for k, v in {"is_premium": chat.premium, "language_code": chat.lang_code}.items()
                if v is not None
            }
        elif isinstance(chat, tl_types.Chat):
            user_type = "GROUP"
            names = {"username": None, "first_name": chat.title, "last_name": None}
        else:  # Channel: either a supergroup or a broadcast channel
            user_type = "SUPERGROUP" if getattr(chat, "megagroup", False) else "CHANNEL"
            names = {"username": getattr(chat, "username", None), "first_name": chat.title, "last_name": None}

        user = await self.session.get(User, event.chat_id)
        if user is None:
            user = User(
                user_id=event.chat_id,
                user_type=user_type,
                referrer=str(referrer) if referrer else None,
                last_active=_utcnow_naive(),
                **names,
                **profile,
            )
            self.session.add(user)
            self.session.add(Setting(user_id=event.chat_id))
        else:
            user.user_type = user_type
            for key, value in {**names, **profile}.items():
                setattr(user, key, value)
            if referrer and not user.referrer:
                user.referrer = str(referrer)
            user.last_active = _utcnow_naive()
            self._reactivate(user)

        if searched:
            self._count_search(user)

    async def touch(self, chat_id: int | None, searched: bool = False) -> None:
        """Record activity for a chat we already know (callbacks, commands, inline).

        Never creates a chat: someone using the bot inline, for instance, hasn't started
        it and can't be messaged."""
        if chat_id is None:
            return
        user = await self.session.get(User, chat_id)
        if user is None:
            return
        now = _utcnow_naive()
        if searched or user.last_active is None or now - user.last_active >= TOUCH_INTERVAL:
            user.last_active = now
        self._reactivate(user)
        if searched:
            self._count_search(user)

    @staticmethod
    def _count_search(user: User) -> None:
        user.search_count = (user.search_count or 0) + 1
        user.last_search_at = _utcnow()

    def _reactivate(self, user: User) -> None:
        """The chat used the bot, so the bot can reach it again."""
        if user.chat_status not in REACHABLE:
            self._change(user, ChatStatus.MEMBER, StatusSource.USER_ACTIVITY)
        if user.unreachable_reason:
            user.unreachable_reason = None
            user.unreachable_at = None
            user.migrated_to_chat_id = None

    # ---- reachability -----------------------------------------------------------------

    async def set_chat_status(self, chat_id: int, status: ChatStatus, source: StatusSource) -> None:
        """Telegram reported the bot's membership in a chat. Known chats only."""
        user = await self.session.get(User, chat_id)
        if user is None:
            return
        if user.chat_status != status:
            self._change(user, status, source)
        if status in REACHABLE and user.unreachable_reason:
            user.unreachable_reason = user.unreachable_at = user.migrated_to_chat_id = None

    async def mark_unreachable(
        self,
        chat_id: int,
        reason: UnreachableReason,
        source: StatusSource,
        migrated_to: int | None = None,
    ) -> None:
        """Sending failed for a reason Telegram has no member status for."""
        user = await self.session.get(User, chat_id)
        if user is None or user.unreachable_reason == reason:
            return
        user.unreachable_reason = reason
        user.unreachable_at = _utcnow()
        user.migrated_to_chat_id = migrated_to
        self.session.add(ChatStatusChange(user_id=chat_id, status=reason, source=source))

    def _change(self, user: User, status: ChatStatus, source: StatusSource) -> None:
        user.chat_status = status
        user.chat_status_at = _utcnow()
        self.session.add(ChatStatusChange(user_id=user.user_id, status=status, source=source))

    # ---- unchanged ---------------------------------------------------------------------

    async def exists(self, user_id: int) -> bool:
        result = await self.session.execute(
            select(exists().where(User.user_id == user_id)),
        )
        return bool(result.scalar())

    async def get_language(self, user_id: int) -> str | None:
        result = await self.session.execute(
            select(Setting.language).where(Setting.user_id == user_id),
        )
        return result.scalar()

    async def set_language(self, user_id: int, language: str) -> None:
        await self.session.merge(Setting(user_id=user_id, language=language))

    async def get_restricted_mode(self, user_id: int) -> bool | None:
        result = await self.session.execute(
            select(Setting.restricted_mode).where(Setting.user_id == user_id),
        )
        return result.scalar()

    async def set_restricted_mode(self, user_id: int, value: bool) -> None:
        await self.session.execute(
            update(Setting)
            .where(Setting.user_id == user_id)
            .values(restricted_mode=value),
        )

    async def count(self) -> int:
        result = await self.session.execute(
            select(sqlalchemy.func.count(User.user_id)),
        )
        return result.scalar_one()

    async def count_joined_today(self) -> int:
        result = await self.session.execute(
            select(sqlalchemy.func.count()).where(
                sqlalchemy.func.DATE(User.join_date) == sqlalchemy.func.CURRENT_DATE()
            ),
        )
        return result.scalar_one()
