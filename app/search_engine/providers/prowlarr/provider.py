"""Prowlarr search provider.

A thin adapter over Prowlarr's results API: builds requests, hands each
result to the parser, and returns normalized models.
"""

from structlog import get_logger

from search_engine.base import TorrentProvider
from search_engine.models import Indexer, IndexerList, SearchResults
from search_engine.providers.prowlarr.constants import CATEGORY_MAP, INDEXERS_ENDPOINT, RESULTS_ENDPOINT
from search_engine.providers.prowlarr.parser import parse_torrent
from search_engine.transport import HttpProvider

logger = get_logger(__name__)


class ProwlarrProvider(HttpProvider, TorrentProvider):
    name = "prowlarr"

    def __init__(
        self,
        base_url: str = "http://localhost:9696",
        api_key: str = "",
        indexer: str = "all",
        timeout: float = 40,
    ):
        super().__init__(base_url=base_url, timeout=timeout)
        self.api_key = api_key
        # "all" searches every indexer; pass a single indexer id or name to query just that one
        self.indexer = indexer or "all"
        self._indexers: list[dict] | None = None

    async def _get_indexers(self) -> list[dict]:
        if self._indexers is not None:
            return self._indexers

        url = self.base_url + INDEXERS_ENDPOINT
        headers = {"X-Api-Key": self.api_key}

        try:
            async with self.session.get(url, headers=headers) as response:
                response.raise_for_status()
                self._indexers = await response.json()
        except Exception as err:
            logger.error("Prowlarr indexer listing failed", error=str(err))
            self._indexers = []

        return self._indexers

    async def search(
        self,
        query: str,
        category: str | None = None,
        page: int = 1,
        source: str | None = None,
    ) -> SearchResults:
        results = SearchResults(
            query=query,
            category=category,
            page=page,
            provider=self.name,
        )

        params: list[tuple[str, str]] = [("query", query)]
        
        indexer_id = source or self.indexer
        if indexer_id and indexer_id.lower() != "all":
            indexers = await self._get_indexers()
            mapped = False
            for idx in indexers:
                def_name = idx.get("definitionName", "").lower()
                idx_id = str(idx.get("id"))
                if indexer_id.lower() in (def_name, idx_id):
                    params.append(("indexerIds", idx_id))
                    mapped = True
            
            if not mapped:
                params.append(("indexerIds", str(indexer_id)))

        for torznab_category in CATEGORY_MAP.get(category or "", []):
            params.append(("categories", str(torznab_category)))

        url = self.base_url + RESULTS_ENDPOINT
        headers = {"X-Api-Key": self.api_key}

        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                payload = await response.json()
        except Exception as err:
            logger.error("Prowlarr search failed", query=query, error=str(err))
            return results

        for item in payload or []:
            torrent = parse_torrent(item, provider=self.name)
            if torrent:
                results.items.append(torrent)

        results.items.sort(key=lambda torrent: torrent.seeders, reverse=True)

        return results

    async def sources(self) -> IndexerList:
        indexers = await self._get_indexers()
        return IndexerList(
            items=[
                Indexer(
                    id=indexer.get("definitionName", str(indexer["id"])).lower(),
                    name=indexer.get("name") or str(indexer["id"])
                )
                for indexer in indexers
                if indexer.get("id") and indexer.get("enable")
            ]
        )
