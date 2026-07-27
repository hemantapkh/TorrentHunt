"""Translate Jackett API responses into the normalized models."""

from typing import Any

from search_engine.models import Torrent
from search_engine.utils import (
    build_magnet,
    extract_info_hash,
    humanize_size,
    make_torrent_id,
    parse_date,
)


def parse_torrent(item: dict[str, Any], provider: str) -> Torrent | None:
    """Normalize one Jackett result; None if it is unusable."""
    name = item.get("Title")
    magnet = item.get("MagnetUri")
    info_hash = item.get("InfoHash")

    if not info_hash and magnet:
        info_hash = extract_info_hash(magnet)

    if not magnet and info_hash:
        magnet = build_magnet(info_hash, name or "")

    # Bookmarks, the Seedr integration and the result message all rely on
    # a magnet link and its info hash, so results without them (private
    # trackers serving only .torrent files) are unusable for the bot
    if not name or not magnet or not info_hash:
        return None

    seeders = int(item.get("Seeders") or 0)
    # Depending on the indexer, Jackett reports Peers either as
    # seeders + leechers or as leechers alone
    peers = int(item.get("Peers") or 0)
    leechers = peers - seeders if peers >= seeders else peers

    published = parse_date(item.get("PublishDate"))

    return Torrent(
        torrent_id=make_torrent_id(info_hash),
        name=name,
        magnet=magnet,
        info_hash=info_hash.lower(),
        size=humanize_size(item.get("Size")),
        size_bytes=int(item.get("Size") or 0),
        seeders=seeders,
        leechers=leechers,
        uploaded_on=published.strftime("%b %d, %Y") if published else None,
        uploaded_at=published.timestamp() if published else 0,
        category=item.get("CategoryDesc"),
        provider=provider,
    )
