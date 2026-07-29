"""Provider registry and factory.

To add a new backend (Prowlarr, bitmagnet, ...): implement `TorrentProvider`
in a new package here and register the class in `PROVIDERS`. Nothing else in
the application needs to change — the entry point selects the provider and
passes its configuration as keyword arguments.
"""

from search_engine.base import TorrentProvider
from search_engine.providers.jackett import JackettProvider
from search_engine.providers.prowlarr.provider import ProwlarrProvider

PROVIDERS: dict[str, type[TorrentProvider]] = {
    JackettProvider.name: JackettProvider,
    ProwlarrProvider.name: ProwlarrProvider,
}


def create_provider(name: str = "jackett", **provider_config) -> TorrentProvider:
    name = (name or "jackett").strip().lower()

    if name not in PROVIDERS:
        available = ", ".join(sorted(PROVIDERS))
        raise ValueError(f"Unknown torrent provider {name!r}. Available: {available}")

    return PROVIDERS[name](**provider_config)
