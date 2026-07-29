"""Normalized data models shared by every torrent search provider."""

from dataclasses import asdict, dataclass, field
from typing import Any

# Canonical category keys used across the application (keyboards, callbacks).
# Every provider is responsible for mapping these to its own category scheme.
CATEGORIES: tuple[str, ...] = (
    "movies",
    "tv",
    "games",
    "music",
    "apps",
    "anime",
    "documentaries",
    "others",
)


@dataclass
class Torrent:
    """A single torrent, in the same shape regardless of the backend."""

    torrent_id: str
    name: str
    magnet: str
    info_hash: str
    size: str | None = None
    size_bytes: int = 0
    seeders: int = 0
    leechers: int = 0
    uploaded_on: str | None = None
    uploaded_at: float = 0  # epoch timestamp, for sorting
    category: str | None = None
    provider: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SearchResults:
    """A normalized set of search results."""

    items: list[Torrent] = field(default_factory=list)
    query: str = ""
    category: str | None = None
    page: int = 1
    provider: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": [item.to_dict() for item in self.items],
            "query": self.query,
            "category": self.category,
            "page": self.page,
            "provider": self.provider,
        }


@dataclass
class Indexer:
    """A search backend indexer/source."""

    id: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class IndexerList:
    """A list of available indexers."""

    items: list[Indexer] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"items": [item.to_dict() for item in self.items]}
