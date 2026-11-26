from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.models.base import Base
from database.models.chat_status import ChatStatus, UnreachableReason, one_of


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(one_of("chat_status", ChatStatus), name="ck_users_chat_status"),
        CheckConstraint(
            one_of("unreachable_reason", UnreachableReason, nullable=True),
            name="ck_users_unreachable_reason",
        ),
    )

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
        TIMESTAMP, server_default=func.current_timestamp(), index=True,
    )

    # Reachability. `chat_status` is the bot's membership in this chat in Telegram's own
    # vocabulary (ChatMember.status): member, administrator, restricted, left, kicked.
    # In a private chat, "kicked" means the user blocked the bot.
    chat_status: Mapped[str] = mapped_column(
        String, default=ChatStatus.MEMBER, server_default=ChatStatus.MEMBER, index=True,
    )
    chat_status_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    # Set only when sending fails for a reason Telegram has no member status for:
    # deactivated (account deleted), chat_not_found, migrated (group became a supergroup).
    unreachable_reason: Mapped[str | None] = mapped_column(String)
    unreachable_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    migrated_to_chat_id: Mapped[int | None] = mapped_column(BigInteger)

    # From the person's Telegram profile (null for groups and channels).
    is_premium: Mapped[bool | None] = mapped_column()
    # Their Telegram app language. Not settings.language, which is the language they chose
    # in the bot.
    language_code: Mapped[str | None] = mapped_column(String)

    # Usage
    search_count: Mapped[int] = mapped_column(default=0, server_default="0")
    last_search_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    setting: Mapped[Setting | None] = relationship(back_populates="user")


class Setting(Base):
    __tablename__ = "settings"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), primary_key=True, index=True,
    )
    language: Mapped[str | None] = mapped_column(String, default="english")
    restricted_mode: Mapped[bool | None] = mapped_column(default=True)

    user: Mapped[User] = relationship(back_populates="setting", foreign_keys=[user_id])
