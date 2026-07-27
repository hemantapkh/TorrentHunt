"""Search service: the app's single entry point for torrent search.

Composes the configured provider (a pure adapter: query -> normalized
results) with the torrent store (persistence that keeps result ids
resolvable later, powering deep links and /getLink). Handlers talk to
this service, never to a provider directly.
"""

from search_engine import SearchResults, Torrent, TorrentProvider

from services.torrent_store import DatabaseTorrentStore


class SearchService:
    def __init__(self, provider: TorrentProvider, store: DatabaseTorrentStore):
        self.provider = provider
        self.store = store

    async def search(
        self,
        query: str,
        category: str | None = None,
        page: int = 1,
        source: str | None = None,
    ) -> SearchResults:
        results = await self.provider.search(
            query, category=category, page=page, source=source,
        )

        await self.store.save(results.items)

        return results

    async def get_torrent(self, torrent_id: str) -> Torrent | None:
        return await self.store.get(torrent_id)

    async def sources(self) -> dict[str, str]:
        return await self.provider.sources()

    async def close(self) -> None:
        await self.provider.close()
