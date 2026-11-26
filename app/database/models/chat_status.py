from datetime import datetime
from enum import StrEnum

from sqlalchemy import TIMESTAMP, BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.models.base import Base


class ChatStatus(StrEnum):
    """Telegram's ChatMember.status values, for the bot's membership in a chat."""

    CREATOR = "creator"
    ADMINISTRATOR = "administrator"
    MEMBER = "member"
    RESTRICTED = "restricted"
    LEFT = "left"
    KICKED = "kicked"  # in a private chat: the user blocked the bot


REACHABLE = (ChatStatus.CREATOR, ChatStatus.ADMINISTRATOR, ChatStatus.MEMBER, ChatStatus.RESTRICTED)


class UnreachableReason(StrEnum):
    """Why sending failed when Telegram has no member status for it."""

    DEACTIVATED = "deactivated"  # the person deleted their Telegram account
    CHAT_NOT_FOUND = "chat_not_found"
    MIGRATED = "migrated"  # a group was upgraded to a supergroup (new chat id)


class StatusSource(StrEnum):
    TELEGRAM_UPDATE = "telegram_update"  # Telegram told us (bot stopped, removed, added...)
    SEND_ERROR = "send_error"  # a message to this chat failed
    USER_ACTIVITY = "user_activity"  # the chat used the bot again


class ChatStatusChange(Base):
    """Append-only history: one row each time a chat's reachability changes.

    users.chat_status / unreachable_reason hold the current state; this keeps every
    change so churn (blocks, unblocks, removals) can be counted over time."""

    __tablename__ = "chat_status_changes"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer(), "sqlite"), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), index=True,
    )
    status: Mapped[str] = mapped_column(String)  # a ChatStatus or UnreachableReason value
    source: Mapped[str] = mapped_column(String)  # a StatusSource value
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.current_timestamp(), index=True,
    )
