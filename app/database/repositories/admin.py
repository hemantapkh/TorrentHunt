from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Admin


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user_id: int) -> None:
        await self.session.merge(Admin(user_id=user_id))

    async def is_admin(self, user_id: int) -> bool:
        result = await self.session.execute(
            select(exists().where(Admin.user_id == user_id)),
        )
        return bool(result.scalar())

    async def ids(self) -> list[int]:
        result = await self.session.execute(select(Admin.user_id))
        return [row.user_id for row in result.all()]
