"""Refresh every stored chat from Telegram: names, usernames, premium, language and
whether the chat still exists. Meant to be run by hand, e.g. once to fill gaps:

    uv run app/refresh_chats.py --dry-run --limit 1000   # look, change nothing
    uv run app/refresh_chats.py                          # everything
    uv run app/refresh_chats.py --after 123456789        # resume private chats

It logs in with its own throwaway session, so it can run next to the bot.

Status only changes on a definite answer from Telegram: a deleted account, or the bot
removed from a group or channel. Telegram can't say whether someone blocked the bot
without sending them something, so blocks are left to live updates and send errors.
"""

import argparse
import asyncio
import datetime
from collections import Counter

from config import settings
from database.models import (
    REACHABLE,
    Chat,
    ChatStatus,
    ChatType,
    StatusSource,
    UnreachableReason,
)
from database.repositories import ChatRepository
from database.repositories.chat import profile_of
from database.session import Session, engine
from logging_config import configure_logging
from sqlalchemy import select
from structlog import get_logger
from telethon import TelegramClient, errors, functions, types, utils
from telethon.sessions import StringSession

logger = get_logger(__name__)

BATCH = 100  # users per users.getUsers call


async def _rows(session, kinds: tuple[str, ...], after: int | None, limit: int) -> list[Chat]:
    query = select(Chat).where(Chat.type.in_(kinds)).order_by(Chat.id).limit(limit)
    if after is not None:
        query = query.where(Chat.id > after)
    return list((await session.scalars(query)).all())


async def _get_users(client: TelegramClient, ids: list[int]) -> dict[int, object]:
    """Bots may look users up by id alone (access hash 0). If one bad id fails the whole
    batch, fall back to asking one at a time."""
    try:
        found = await client(functions.users.GetUsersRequest([types.InputUser(i, 0) for i in ids]))
        return {u.id: u for u in found}
    except (errors.PeerIdInvalidError, errors.UserIdInvalidError, errors.InputUserDeactivatedError):
        pass
    result: dict[int, object] = {}
    for i in ids:
        try:
            [user] = await client(functions.users.GetUsersRequest([types.InputUser(i, 0)]))
            result[i] = user
        except errors.InputUserDeactivatedError:
            result[i] = types.User(id=i, deleted=True)
        except (errors.PeerIdInvalidError, errors.UserIdInvalidError):
            pass  # counted as not resolved by the caller
    return result


async def refresh_private(client, after: int | None, limit: int | None, dry_run: bool) -> None:
    stats: Counter = Counter()
    while limit is None or stats["checked"] < limit:
        size = BATCH if limit is None else min(BATCH, limit - stats["checked"])
        async with Session() as session:
            rows = await _rows(session, (ChatType.PRIVATE,), after, size)
            if not rows:
                break
            found = await _get_users(client, [r.id for r in rows])
            repo = ChatRepository(session)
            now = datetime.datetime.now(datetime.UTC)
            for row in rows:
                user = found.get(row.id)
                if not isinstance(user, types.User):  # missing or UserEmpty
                    stats["not_resolved"] += 1
                    continue
                if user.deleted:  # keep the last known name
                    if row.unreachable_reason != UnreachableReason.DEACTIVATED:
                        stats["deleted"] += 1
                    await repo.mark_unreachable(
                        row.id, UnreachableReason.DEACTIVATED, StatusSource.LOOKUP,
                    )
                    continue
                if not row.first_name and user.first_name:
                    stats["name_filled"] += 1
                for key, value in profile_of(user).items():
                    setattr(row, key, value)
                row.profile_updated_at = now
                stats["updated"] += 1
            stats["checked"] += len(rows)
            after = rows[-1].id
            await (session.rollback() if dry_run else session.commit())
        if stats["checked"] % 10_000 < BATCH:
            logger.info("Private chats", last_user_id=after, **stats)
    logger.info("Private chats done", last_user_id=after, dry_run=dry_run, **stats)


async def _lookup_group(client, chat_id: int):
    """The chat object for a group or channel, or the error Telegram gave."""
    real_id, peer_type = utils.resolve_id(chat_id)
    try:
        if peer_type is types.PeerChannel:
            request = functions.channels.GetChannelsRequest([types.InputChannel(real_id, 0)])
        else:
            request = functions.messages.GetChatsRequest([real_id])
        return (await client(request)).chats[0]
    except errors.ChannelPrivateError:  # the bot was removed
        return ChatStatus.LEFT
    except (errors.ChannelInvalidError, errors.ChatIdInvalidError, errors.PeerIdInvalidError):
        return None


async def refresh_groups(client, limit: int | None, dry_run: bool) -> None:
    stats: Counter = Counter()
    async with Session() as session:
        rows = await _rows(
            session, (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL), None, limit or 1_000_000,
        )
        repo = ChatRepository(session)
        now = datetime.datetime.now(datetime.UTC)
        for row in rows:
            chat = await _lookup_group(client, row.id)
            stats["checked"] += 1
            if chat is None:
                stats["not_resolved"] += 1
            elif chat is ChatStatus.LEFT or getattr(chat, "left", False):
                stats["left"] += row.status != ChatStatus.LEFT
                await repo.set_status(row.id, ChatStatus.LEFT, StatusSource.LOOKUP)
            elif isinstance(chat, (types.ChatForbidden, types.ChannelForbidden)):
                stats["kicked"] += row.status != ChatStatus.KICKED
                await repo.set_status(row.id, ChatStatus.KICKED, StatusSource.LOOKUP)
            elif isinstance(chat, types.Chat) and isinstance(chat.migrated_to, types.InputChannel):
                stats["migrated"] += row.unreachable_reason != UnreachableReason.MIGRATED
                new_id = utils.get_peer_id(types.PeerChannel(chat.migrated_to.channel_id))
                await repo.mark_unreachable(
                    row.id, UnreachableReason.MIGRATED, StatusSource.LOOKUP, migrated_to=new_id,
                )
            else:
                for key, value in profile_of(chat).items():
                    setattr(row, key, value)
                row.profile_updated_at = now
                if row.status not in REACHABLE:
                    await repo.set_status(row.id, ChatStatus.MEMBER, StatusSource.LOOKUP)
                stats["updated"] += 1
        await (session.rollback() if dry_run else session.commit())
    logger.info("Groups and channels done", dry_run=dry_run, **stats)


async def main(args: argparse.Namespace) -> None:
    client = TelegramClient(
        StringSession(), settings.api_id, settings.api_hash,
        receive_updates=False, flood_sleep_threshold=15 * 60,
    )
    await client.start(bot_token=settings.bot_token)
    try:
        if not args.skip_private:
            await refresh_private(client, args.after, args.limit, args.dry_run)
        if not args.skip_groups:
            await refresh_groups(client, args.limit, args.dry_run)
    finally:
        await client.log_out()  # drop the throwaway session from the bot's sessions
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dry-run", action="store_true", help="look everything up, save nothing")
    parser.add_argument("--limit", type=int, help="stop after this many chats of each kind")
    parser.add_argument("--after", type=int, help="resume private chats after this user id")
    parser.add_argument("--skip-private", action="store_true")
    parser.add_argument("--skip-groups", action="store_true")
    configure_logging(settings.environment)
    asyncio.run(main(parser.parse_args()))
