"""Jackett search provider (https://github.com/Jackett/Jackett).

A thin adapter over Jackett's results API: builds requests, hands each
result to the parser, and returns normalized models.
"""


from structlog import get_logger

from search_engine.base import TorrentProvider
from search_engine.models import Indexer, IndexerList, SearchResults
from search_engine.providers.jackett.constants import CATEGORY_MAP, RESULTS_ENDPOINT
from search_engine.providers.jackett.parser import parse_torrent
from search_engine.transport import HttpProvider

logger = get_logger(__name__)


class JackettProvider(HttpProvider, TorrentProvider):
    name = "jackett"

    def __init__(
        self,
        base_url: str = "http://localhost:9117",
        api_key: str = "",
        indexer: str = "all",
        timeout: float = 40,
        message_search_tag: str = "",
        inline_search_tag: str = "",
    ):
        super().__init__(base_url=base_url, timeout=timeout)
        self.api_key = api_key
        # "all" aggregates every indexer configured in Jackett; pass a
        # single indexer id to query just that one
        self.indexer = indexer or "all"
        self.message_search_tag = message_search_tag
        self.inline_search_tag = inline_search_tag

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

        params = [("apikey", self.api_key), ("Query", query)]
        for torznab_category in CATEGORY_MAP.get(category or "", []):
            params.append(("Category[]", str(torznab_category)))

        indexer_id = source or self.indexer
        if indexer_id.lower() == "all" and self.message_search_tag:
            indexer_id = f"tag:{self.message_search_tag}"
            
        url = self.base_url + RESULTS_ENDPOINT.format(indexer=indexer_id)

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                payload = await response.json()
        except Exception as err:
            logger.error("Jackett search failed", query=query, error=str(err))
            return results

        for item in payload.get("Results") or []:
            torrent = parse_torrent(item, provider=self.name)
            if torrent:
                results.items.append(torrent)

        results.items.sort(key=lambda torrent: torrent.seeders, reverse=True)

        return results

    async def sources(self) -> IndexerList:
        indexer_id = self.indexer
        if indexer_id.lower() == "all" and self.inline_search_tag:
            indexer_id = f"tag:{self.inline_search_tag}"
            
        # Jackett's indexer listing endpoint needs cookie auth, but an
        # empty-query search reports every configured indexer it queried
        url = self.base_url + RESULTS_ENDPOINT.format(indexer=indexer_id)
        params = [("apikey", self.api_key), ("Query", "")]

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                payload = await response.json()
        except Exception as err:
            logger.error("Jackett indexer listing failed", error=str(err))
            return IndexerList()

        return IndexerList(
            items=[
                Indexer(id=indexer["ID"], name=indexer.get("Name") or indexer["ID"])
                for indexer in payload.get("Indexers") or []
                if indexer.get("ID")
            ]
        )

    async def reload(self) -> None:
        pass
