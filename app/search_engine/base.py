"""Base interface every torrent search provider must implement."""

from abc import ABC, abstractmethod

from search_engine.models import SearchResults


class TorrentProvider(ABC):
    """A pure adapter over a search backend.

    Providers translate a query into normalized `SearchResults` — nothing
    more. Persistence, caching and resolution of results by id are
    application concerns (see `services.search`).
    """

    name = "base"

    @abstractmethod
    async def search(
        self,
        query: str,
        category: str | None = None,
        page: int = 1,
        source: str | None = None,
    ) -> SearchResults:
        """Search the backend and return normalized results.

        `category` is one of `search_engine.models.CATEGORIES` or None.
        `source` restricts the search to one of the ids returned by
        `sources`; None searches everything.
        Must not raise on backend failures: log and return empty results.
        """

    async def sources(self) -> dict[str, str]:
        """Return the backend's individually searchable sources.

        Maps a source id (usable as `search(source=...)`) to a display
        name, e.g. Jackett/Prowlarr indexers. Backends without such a
        concept return an empty dict.
        """
        return {}

    async def close(self) -> None:
        """Release any underlying resources (HTTP sessions etc.)."""
