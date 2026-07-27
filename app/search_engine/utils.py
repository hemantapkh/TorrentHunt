"""Shared helpers for building providers."""

import hashlib
import re
from datetime import datetime
from typing import Any
from urllib.parse import quote

INFO_HASH_RE = re.compile(r"btih:([a-fA-F0-9]{40}|[A-Za-z2-7]{32})")


def make_torrent_id(*parts: object) -> str:
    """Build a short, stable id from unique fields.

    The id is plain hex, so it stays safe inside Telegram commands and
    callback data. Deterministic: the same torrent maps to the same id
    across searches and restarts.
    """
    digest = hashlib.sha1("|".join(str(part) for part in parts).encode())
    return digest.hexdigest()[:16]


def extract_info_hash(magnet: str) -> str | None:
    """Pull the btih info hash out of a magnet link."""
    match = INFO_HASH_RE.search(magnet)
    return match.group(1) if match else None


def build_magnet(info_hash: str, name: str = "") -> str:
    """Build a magnet link from an info hash."""
    return f"magnet:?xt=urn:btih:{info_hash}&dn={quote(name)}"


def humanize_size(num_bytes: Any) -> str | None:
    """Bytes -> human readable size (e.g. 2.1 GB)."""
    try:
        size = float(num_bytes)
    except (TypeError, ValueError):
        return None

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024

    return None


def parse_date(value: Any) -> datetime | None:
    """Parse an ISO-8601 date, tolerating a trailing Z."""
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
