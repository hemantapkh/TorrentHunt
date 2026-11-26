"""Learn from failed sends whether a chat can still be reached.

Telethon raises typed errors, so this matches on exception classes, not error text.
"""

from database import get_session
from database.models import ChatStatus, StatusSource, UnreachableReason
from database.repositories import UserRepository
from structlog import get_logger
from telethon import errors

logger = get_logger(__name__)

_STATUS: dict[type[Exception], ChatStatus] = {
    errors.UserIsBlockedError: ChatStatus.KICKED,  # the user blocked the bot
    errors.ChannelPrivateError: ChatStatus.LEFT,  # bot no longer in the group/channel
}
_REASON: dict[type[Exception], UnreachableReason] = {
    errors.InputUserDeactivatedError: UnreachableReason.DEACTIVATED,  # account deleted
    errors.PeerIdInvalidError: UnreachableReason.CHAT_NOT_FOUND,
    errors.ChatIdInvalidError: UnreachableReason.CHAT_NOT_FOUND,
    errors.ChannelInvalidError: UnreachableReason.CHAT_NOT_FOUND,
}

UNREACHABLE_ERRORS = tuple(_STATUS) + tuple(_REASON)


async def record_send_failure(chat_id: int | None, exc: BaseException) -> bool:
    """Store what a failed send tells us. Returns True if the error was one of ours."""
    if chat_id is None:
        return False
    status = next((s for cls, s in _STATUS.items() if isinstance(exc, cls)), None)
    reason = next((r for cls, r in _REASON.items() if isinstance(exc, cls)), None)
    if status is None and reason is None:
        return False
    async with get_session() as session:
        repo = UserRepository(session)
        if status is not None:
            await repo.set_chat_status(chat_id, status, StatusSource.SEND_ERROR)
        else:
            await repo.mark_unreachable(chat_id, reason, StatusSource.SEND_ERROR)
    logger.info("Chat is unreachable", chat_id=chat_id, error=type(exc).__name__)
    return True
