from datetime import datetime
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TorrentCache


class TorrentCacheRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, torrent: Any, last_seen: datetime) -> None:
        await self.session.merge(
            TorrentCache(
                torrent_id=torrent.torrent_id,
                name=torrent.name,
                magnet=torrent.magnet,
                info_hash=torrent.info_hash,
                size=torrent.size,
                seeders=torrent.seeders,
                leechers=torrent.leechers,
                uploaded_on=torrent.uploaded_on,
                category=torrent.category,
                provider=torrent.provider,
                last_seen=last_seen,
            ),
        )

    async def prune(self, cutoff: datetime) -> int:
        result = await self.session.execute(
            delete(TorrentCache).where(TorrentCache.last_seen < cutoff),
        )
        return getattr(result, "rowcount", 0)

    async def get(self, torrent_id: str) -> TorrentCache | None:
        result = await self.session.execute(
            select(TorrentCache).where(TorrentCache.torrent_id == torrent_id),
        )
        return result.scalar_one_or_none()
