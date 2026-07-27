"""Repositories: all database queries live here.

One module per repository. Each takes a session (from
`database.session.get_session`); the session scope commits, repositories
only flush when they need generated ids.
"""

from database.repositories.admin import AdminRepository
from database.repositories.bookmark import BookmarkRepository
from database.repositories.referrer import ReferrerRepository
from database.repositories.torrent_cache import TorrentCacheRepository
from database.repositories.user import UserRepository

__all__ = [
    "AdminRepository",
    "BookmarkRepository",
    "ReferrerRepository",
    "TorrentCacheRepository",
    "UserRepository",
]
