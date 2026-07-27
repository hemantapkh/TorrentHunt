import datetime
from typing import Any

import sqlalchemy
from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.tl import types as tl_types

from database.models import Setting, User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_from_event(self, event: Any, referrer: int | str | None = None) -> None:
        """Create or refresh the user (and default settings) for an update."""
        chat = await event.get_chat()

        if isinstance(chat, tl_types.User):
            user_type = "PRIVATE"
            username = chat.username
            first_name = chat.first_name
            last_name = chat.last_name

        elif isinstance(chat, tl_types.Chat):
            user_type = "GROUP"
            username = None
            first_name = chat.title
            last_name = None

        else:  # Channel: either a supergroup or a broadcast channel
            user_type = "SUPERGROUP" if getattr(chat, "megagroup", False) else "CHANNEL"
            username = getattr(chat, "username", None)
            first_name = chat.title
            last_name = None

        await self.session.merge(
            User(
                user_id=event.chat_id,
                user_type=user_type,
                username=username,
                first_name=first_name,
                last_name=last_name,
                referrer=str(referrer) if referrer else None,
                last_active=datetime.datetime.now(),
            ),
        )
        await self.session.merge(Setting(user_id=event.chat_id))

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
