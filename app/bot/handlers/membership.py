"""Track whether the bot can still reach each chat, from Telegram's own updates.

These handlers never stop propagation, so they don't interfere with the rest of the
handler table. Unknown chats are ignored: membership only matters for chats we store.
"""

from database import get_session
from database.models import ChatStatus, StatusSource, UnreachableReason
from database.repositories import ChatRepository
from structlog import get_logger
from telethon import events, utils
from telethon.tl import types

from bot.context import ctx

logger = get_logger(__name__)


async def _set(chat_id: int, status: ChatStatus) -> None:
    async with get_session() as session:
        await ChatRepository(session).set_status(chat_id, status, StatusSource.TELEGRAM_UPDATE)


async def bot_stopped(update: types.UpdateBotStopped) -> None:
    """A user blocked (stopped=True) or unblocked the bot in their private chat."""
    try:
        await _set(update.user_id, ChatStatus.KICKED if update.stopped else ChatStatus.MEMBER)
    except Exception:
        logger.exception("Couldn't record a block/unblock", user_id=update.user_id)


async def chat_action(event: events.ChatAction.Event) -> None:
    """The bot was added to or removed from a group."""
    try:
        if ctx.me.id not in (event.user_ids or []):
            return
        if event.user_kicked:
            await _set(event.chat_id, ChatStatus.KICKED)
        elif event.user_left:
            await _set(event.chat_id, ChatStatus.LEFT)
        elif event.user_added or event.user_joined:
            # Store the group now (not only once it uses the bot), with who added the bot.
            async with get_session() as session:
                repo = ChatRepository(session)
                await repo.upsert_from_event(event)
                await session.flush()
                if event.user_added and (adder := await event.get_added_by()):
                    await repo.set_added_by(event.chat_id, adder.id)
    except Exception:
        logger.exception("Couldn't record a membership change", chat_id=event.chat_id)


def _channel_status(p: types.TypeChannelParticipant | None) -> ChatStatus:
    if p is None or isinstance(p, types.ChannelParticipantLeft):
        return ChatStatus.LEFT
    if isinstance(p, types.ChannelParticipantBanned):
        # Banned with view_messages taken away = removed; otherwise just limited.
        return ChatStatus.KICKED if p.banned_rights.view_messages else ChatStatus.RESTRICTED
    if isinstance(p, types.ChannelParticipantCreator):
        return ChatStatus.CREATOR
    if isinstance(p, types.ChannelParticipantAdmin):
        return ChatStatus.ADMINISTRATOR
    return ChatStatus.MEMBER


async def channel_participant(update: types.UpdateChannelParticipant) -> None:
    """The bot's membership changed in a supergroup or channel."""
    try:
        if update.user_id != ctx.me.id:
            return
        chat_id = utils.get_peer_id(types.PeerChannel(update.channel_id))
        await _set(chat_id, _channel_status(update.new_participant))
    except Exception:
        logger.exception("Couldn't record a channel membership change")


def is_migration(update: object) -> bool:
    return (
        isinstance(update, types.UpdateNewMessage)
        and isinstance(update.message, types.MessageService)
        and isinstance(update.message.action, types.MessageActionChatMigrateTo)
    )


async def chat_migrated(update: types.UpdateNewMessage) -> None:
    """A basic group was upgraded to a supergroup: same people, new chat id."""
    try:
        message = update.message
        old_id = utils.get_peer_id(message.peer_id)
        new_id = utils.get_peer_id(types.PeerChannel(message.action.channel_id))
        async with get_session() as session:
            await ChatRepository(session).mark_unreachable(
                old_id, UnreachableReason.MIGRATED, StatusSource.TELEGRAM_UPDATE, migrated_to=new_id,
            )
    except Exception:
        logger.exception("Couldn't record a group migration")
