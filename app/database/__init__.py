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

    async def set_user(self, message, referrer=None) -> bool:
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
        )

        # TODO: Implement this in a better way with single query
        async with Session() as session:
            try:
                session.add(user)
                settings = Setting(user_id=message.chat.id)
                session.add(settings)

                await session.commit()

                return True

            except sqlalchemy.exc.IntegrityError:
                await session.rollback()

                query = (
                    sqlalchemy.update(User)
                    .where(User.user_id == user.user_id)
                    .values(
                        user_type=user.user_type,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        last_active=datetime.datetime.now(),
                    )
                )

                await session.execute(query)
                await session.commit()

                return False
