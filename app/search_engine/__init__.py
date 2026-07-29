"""Provider-agnostic torrent search engine.

The application interacts with providers through `TorrentProvider`
(built via `create_provider`) and the normalized `Torrent`/`SearchResults`
models. Swapping Jackett for Prowlarr, bitmagnet or anything else means
adding a new package under `search_engine/providers` and registering it —
nothing outside this package changes.
"""

from search_engine.base import TorrentProvider
from search_engine.models import CATEGORIES, IndexerList, SearchResults, Torrent
from search_engine.providers import create_provider

__all__ = [
    "CATEGORIES",
    "IndexerList",
    "SearchResults",
    "Torrent",
    "TorrentProvider",
    "create_provider",
]
