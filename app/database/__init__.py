"""API to connect to the database server"""

import datetime

import sqlalchemy
from database.models import Session, Setting, User


class DataBase:
    def __init__(self):
        self.session = Session

    async def _query(self, method, *args, **kwargs):
        async with self.session() as session:
            auto_commmit = kwargs.pop("auto_commit", True)
            result = await getattr(session, method)(*args, **kwargs)
            if auto_commmit:
                await session.commit()
            return result

    def __getattr__(self, method):
        def wrapper(*args, **kwargs):
            return self._query(method, *args, **kwargs)

        return wrapper

    async def set_user(self, message, referrer=None):
        # If chat type if group/channel
        if message.chat.type.name != "PRIVATE":
            message.chat.first_name = message.chat.title
            message.chat.last_name = None

        user = User(
            user_id=message.chat.id,
            user_type=message.chat.type.name,
            username=message.chat.username,
            first_name=message.chat.first_name,
            last_name=message.chat.last_name,
            referrer=str(referrer) if referrer else None,
            last_active=datetime.datetime.now(),
        )

        settings = Setting(user_id=message.chat.id)

        async with Session() as session:
            await session.merge(user)
            await session.merge(settings)

            await session.commit()
