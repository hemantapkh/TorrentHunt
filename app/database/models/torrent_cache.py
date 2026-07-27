from datetime import datetime

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class TorrentCache(Base):
    __tablename__ = "torrent_cache"

    torrent_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    magnet: Mapped[str] = mapped_column(String)
    info_hash: Mapped[str] = mapped_column(String)
    size: Mapped[str | None] = mapped_column(String)
    seeders: Mapped[int | None] = mapped_column()
    leechers: Mapped[int | None] = mapped_column()
    uploaded_on: Mapped[str | None] = mapped_column(String)
    category: Mapped[str | None] = mapped_column(String)
    provider: Mapped[str | None] = mapped_column(String)
    last_seen: Mapped[datetime | None] = mapped_column(TIMESTAMP, index=True)
