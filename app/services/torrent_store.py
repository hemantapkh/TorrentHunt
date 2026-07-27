"""Database-backed store for torrent search results.

Persisting results keeps deep links in chat history resolvable across bot
restarts. Used by `services.search.SearchService`; owns its session scopes
because it is called outside any handler session.

Rows not seen in any search for TORRENT_CACHE_DAYS are removed by `prune`,
which runs as a periodic background job (see `services.jobs`).
"""

from datetime import UTC, datetime, timedelta

from database.repositories.torrent_cache import TorrentCacheRepository
from database.session import get_session
from search_engine import Torrent
from structlog import get_logger

logger = get_logger(__name__)


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class DatabaseTorrentStore:
    def __init__(self, retention_days: float = 90):
        self.retention = timedelta(days=retention_days)

    async def save(self, torrents: list[Torrent]) -> None:
        now = _utcnow()

        async with get_session() as session:
            cache = TorrentCacheRepository(session)

            for torrent in torrents:
                await cache.upsert(torrent, last_seen=now)

    async def prune(self) -> None:
        """Remove cached torrents not seen within the retention window."""
        async with get_session() as session:
            removed = await TorrentCacheRepository(session).prune(
                cutoff=_utcnow() - self.retention,
            )

        logger.info("Pruned torrent cache", removed=removed)

    async def get(self, torrent_id: str) -> Torrent | None:
        async with get_session() as session:
            row = await TorrentCacheRepository(session).get(torrent_id)

        if not row:
            return None

        return Torrent(
            torrent_id=row.torrent_id,
            name=row.name,
            magnet=row.magnet,
            info_hash=row.info_hash,
            size=row.size,
            seeders=row.seeders or 0,
            leechers=row.leechers or 0,
            uploaded_on=row.uploaded_on,
            category=row.category,
            provider=row.provider,
        )
