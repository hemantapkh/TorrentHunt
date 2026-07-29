"""Translate Prowlarr API responses into the normalized models."""

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
    """Normalize one Prowlarr result; None if it is unusable."""
    name = item.get("title")
    
    magnet = item.get("magnetUrl")
    if not magnet and str(item.get("guid", "")).startswith("magnet:"):
        magnet = item.get("guid")
        
    info_hash = item.get("infoHash")

    if not info_hash and magnet:
        info_hash = extract_info_hash(magnet)

    if not magnet and info_hash:
        magnet = build_magnet(info_hash, name or "")

    # Results without a magnet link and info hash are unusable for the bot
    if not name or not magnet or not info_hash:
        return None

    seeders = int(item.get("seeders") or 0)
    leechers = int(item.get("leechers") or 0)

    published = parse_date(item.get("publishDate"))
    
    category = None
    categories = item.get("categories") or []
    if categories:
        category = categories[0].get("name")

    return Torrent(
        torrent_id=make_torrent_id(info_hash),
        name=name,
        magnet=magnet,
        info_hash=info_hash.lower(),
        size=humanize_size(item.get("size")),
        size_bytes=int(item.get("size") or 0),
        seeders=seeders,
        leechers=leechers,
        uploaded_on=published.strftime("%b %d, %Y") if published else None,
        uploaded_at=published.timestamp() if published else 0,
        category=category,
        provider=provider,
    )
