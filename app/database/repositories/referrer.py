from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Referrer


class ReferrerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def track_click(self, referrer_id: str) -> bool:
        """Count a click on a tracking id; False if the id is unknown."""
        result = await self.session.execute(
            update(Referrer)
            .where(Referrer.referrer_id == referrer_id)
            .values(clicks=Referrer.clicks + 1),
        )
        return bool(getattr(result, "rowcount", 0))
