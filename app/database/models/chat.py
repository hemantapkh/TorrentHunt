"""The chats this bot knows, in the schema shared by all bots (see Orbit), plus this bot's
own per-chat tables, keyed by chat_id."""

from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    Computed,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.models.base import Base
from database.models.chat_status import (
    REACHABLE,
    ChatStatus,
    ChatType,
    UnreachableReason,
    one_of,
)

# The database computes chats.is_reachable with this; nothing in the app writes it.
IS_REACHABLE_SQL = (
    f"status IN ({', '.join(f"'{s.value}'" for s in REACHABLE)}) AND unreachable_reason IS NULL"
)


class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = (
        CheckConstraint(one_of("type", ChatType), name="ck_chats_type"),
        CheckConstraint(one_of("status", ChatStatus), name="ck_chats_status"),
        CheckConstraint(
            one_of("unreachable_reason", UnreachableReason, nullable=True),
            name="ck_chats_unreachable_reason",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)  # chat id
    type: Mapped[str] = mapped_column(String, index=True)

    # Profile, as Telegram last showed it. Names for people, title for groups and channels.
    first_name: Mapped[str | None] = mapped_column(String)
    last_name: Mapped[str | None] = mapped_column(String)
    title: Mapped[str | None] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String)
    # Their Telegram app language. Not settings.language, the language chosen in the bot.
    language_code: Mapped[str | None] = mapped_column(String)
    is_premium: Mapped[bool | None] = mapped_column(Boolean)
    member_count: Mapped[int | None] = mapped_column()  # groups and channels
    added_by_user_id: Mapped[int | None] = mapped_column(BigInteger)  # who added the bot
    profile_updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    # Reachability. `status` is the bot's membership in Telegram's own vocabulary
    # (ChatMember.status); in a private chat, "kicked" means the user blocked the bot.
    status: Mapped[str] = mapped_column(
        String, default=ChatStatus.MEMBER, server_default=ChatStatus.MEMBER, index=True,
    )
    status_changed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    # Set when Telegram can't deliver for a reason it has no member status for:
    # deactivated (account deleted), chat_not_found, migrated (group became a supergroup).
    unreachable_reason: Mapped[str | None] = mapped_column(String)
    unreachable_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    migrated_to_chat_id: Mapped[int | None] = mapped_column(BigInteger)
    # Whether a message can be delivered: filter broadcasts on this.
    is_reachable: Mapped[bool] = mapped_column(
        Boolean, Computed(IS_REACHABLE_SQL, persisted=True), index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.current_timestamp(), index=True,
    )
    last_active_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), index=True)

    setting: Mapped[Setting | None] = relationship(back_populates="chat")


class Setting(Base):
    """Preferences chosen in this bot."""

    __tablename__ = "settings"

    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True,
    )
    language: Mapped[str | None] = mapped_column(String, default="english")
    restricted_mode: Mapped[bool | None] = mapped_column(default=True)

    chat: Mapped[Chat] = relationship(back_populates="setting", foreign_keys=[chat_id])


class SearchStat(Base):
    """How much a chat searches. TorrentHunt only."""

    __tablename__ = "search_stats"

    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True,
    )
    search_count: Mapped[int] = mapped_column(default=0, server_default="0")
    last_search_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


class Referral(Base):
    """Where a chat came from: a referrer link or the user who shared the bot. First touch:
    set once and never overwritten."""

    __tablename__ = "referrals"

    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True,
    )
    referrer: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.current_timestamp(),
    )
