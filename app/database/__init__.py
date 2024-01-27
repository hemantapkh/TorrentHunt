"""API to connect to the database server"""

from database.models import Session


class DataBase:
    def __init__(self):
        self.session = Session

    async def _query(self, method, *args, **kwargs):
        async with self.session() as session:
            return await getattr(session, method)(*args, **kwargs)

    def __getattr__(self, method):
        async def wrapper(*args, **kwargs):
            return await self._query(method, *args, **kwargs)

        return wrapper
