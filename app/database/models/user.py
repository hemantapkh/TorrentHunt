from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.models.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_type: Mapped[str] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String)
    first_name: Mapped[str | None] = mapped_column(String)
    last_name: Mapped[str | None] = mapped_column(String)
    referrer: Mapped[str | None] = mapped_column(String)
    join_date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), index=True,
    )
    last_active: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(),
    )

    setting: Mapped[Setting | None] = relationship(back_populates="user")


class Setting(Base):
    __tablename__ = "settings"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), primary_key=True, index=True,
    )
    language: Mapped[str | None] = mapped_column(String, default="english")
    restricted_mode: Mapped[bool | None] = mapped_column(default=True)

    user: Mapped[User] = relationship(back_populates="setting", foreign_keys=[user_id])
