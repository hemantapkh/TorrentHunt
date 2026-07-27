from sqlalchemy import and_, delete, exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Bookmark


class BookmarkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, user_id: int, hash: str) -> bool:
        result = await self.session.execute(
            select(exists(Bookmark)).where(
                and_(Bookmark.user_id == user_id, Bookmark.hash == hash),
            ),
        )
        return bool(result.scalar())

    async def add(self, user_id: int, hash: str, **fields: str) -> None:
        await self.session.execute(
            insert(Bookmark).values(user_id=user_id, hash=hash, **fields),
        )

    async def remove(self, user_id: int, hash: str) -> None:
        await self.session.execute(
            delete(Bookmark)
            .where(Bookmark.user_id == user_id)
            .where(Bookmark.hash == hash),
        )

    async def list_page(self, user_id: int, offset: int, limit: int = 50) -> list[Bookmark]:
        result = await self.session.execute(
            select(Bookmark)
            .where(Bookmark.user_id == user_id)
            .order_by(Bookmark.date.desc())
            .offset(offset * limit)
            .limit(limit),
        )
        return list(result.scalars().all())
