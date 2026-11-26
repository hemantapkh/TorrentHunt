from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.models.base import Base
from database.models.chat import Chat


class Bookmark(Base):
    __tablename__ = "bookmarks"

    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True, index=True,
    )
    hash: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    magnet: Mapped[str] = mapped_column(String)
    seeders: Mapped[str | None] = mapped_column(String)
    leechers: Mapped[str | None] = mapped_column(String)
    size: Mapped[str | None] = mapped_column(String)
    uploaded_on: Mapped[str | None] = mapped_column(String)
    date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(),
    )

    chat: Mapped[Chat] = relationship(backref="bookmarks")
