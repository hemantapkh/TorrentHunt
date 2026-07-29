"""Prowlarr search provider.

A thin adapter over Prowlarr's results API: builds requests, hands each
result to the parser, and returns normalized models.
"""

from structlog import get_logger

from search_engine.base import TorrentProvider
from search_engine.models import Indexer, IndexerList, SearchResults
from search_engine.providers.prowlarr.constants import (
    CATEGORY_MAP,
    INDEXERS_ENDPOINT,
    RESULTS_ENDPOINT,
    TAGS_ENDPOINT,
)
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
        message_search_tag: str = "",
        inline_search_tag: str = "",
    ):
        super().__init__(base_url=base_url, timeout=timeout)
        self.api_key = api_key
        # "all" searches every indexer; pass a single indexer id or name
        # to query just that one
        self.indexer = indexer or "all"
        self.message_search_tag = message_search_tag
        self.inline_search_tag = inline_search_tag
        self._indexers: list[dict] | None = None
        self._tags_map: dict[str, int] | None = None

    # ------------------------------------------------------------------
    # Internal caching helpers
    # ------------------------------------------------------------------

    async def _get_tags(self) -> dict[str, int]:
        """Fetch and cache the tag-label → tag-id mapping."""
        if self._tags_map is not None:
            return self._tags_map

        url = self.base_url + TAGS_ENDPOINT
        headers = {"X-Api-Key": self.api_key}
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.ok:
                    tags = await response.json()
                    self._tags_map = {
                        tag["label"].lower(): tag["id"] for tag in tags
                    }
                else:
                    self._tags_map = {}
        except Exception as err:
            logger.error("Prowlarr tag listing failed", error=str(err))
            self._tags_map = {}

        return self._tags_map

    async def _get_indexers(self) -> list[dict]:
        """Fetch and cache the full indexer list."""
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

    async def _indexer_ids_for_tag(self, tag_name: str) -> list[int]:
        """Return numeric indexer IDs that carry the given tag."""
        tags_map = await self._get_tags()
        tag_id = tags_map.get(tag_name.lower())
        if tag_id is None:
            logger.warning("Tag not found in Prowlarr", tag=tag_name)
            return []

        indexers = await self._get_indexers()
        return [
            idx["id"]
            for idx in indexers
            if idx.get("enable") and tag_id in idx.get("tags", [])
        ]

    async def _resolve_indexer_id(self, name: str) -> list[str]:
        """Resolve a human-readable indexer name to numeric ID(s)."""
        indexers = await self._get_indexers()
        ids = [
            str(idx["id"])
            for idx in indexers
            if name.lower()
            in (idx.get("definitionName", "").lower(), str(idx.get("id")))
        ]
        return ids or [name]

    # ------------------------------------------------------------------
    # TorrentProvider interface
    # ------------------------------------------------------------------

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
            for resolved_id in await self._resolve_indexer_id(indexer_id):
                params.append(("indexerIds", resolved_id))
        elif self.message_search_tag:
            ids = await self._indexer_ids_for_tag(self.message_search_tag)
            if not ids:
                logger.warning(
                    "No indexers matched message search tag",
                    tag=self.message_search_tag,
                )
                return results
            for idx_id in ids:
                params.append(("indexerIds", str(idx_id)))

        for torznab_category in CATEGORY_MAP.get(category or "", []):
            params.append(("categories", str(torznab_category)))

        url = self.base_url + RESULTS_ENDPOINT
        headers = {"X-Api-Key": self.api_key}

        try:
            async with self.session.get(
                url, params=params, headers=headers
            ) as response:
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

        if self.inline_search_tag:
            allowed_ids = set(
                await self._indexer_ids_for_tag(self.inline_search_tag)
            )
            indexers = [
                idx for idx in indexers if idx.get("id") in allowed_ids
            ]

        return IndexerList(
            items=[
                Indexer(
                    id=indexer.get("definitionName", str(indexer["id"])).lower(),
                    name=indexer.get("name") or str(indexer["id"]),
                )
                for indexer in indexers
                if indexer.get("id") and indexer.get("enable")
            ]
        )

    async def reload(self) -> None:
        self._indexers = None
        self._tags_map = None
