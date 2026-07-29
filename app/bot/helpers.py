"""Shared helpers used by decorators and handlers."""

import re
from typing import Any

from database import get_session
from database.repositories import AdminRepository, UserRepository
from localization import Translator
from structlog import get_logger
from telethon import TelegramClient, events

from bot.context import ctx
from bot.views.shared_view import main_keyboard

logger = get_logger(__name__)


async def resolve_translator(event: Any) -> Translator:
    """Resolve the translator for an update.

    Language settings are keyed per chat: private chats use the user id,
    groups the chat id. Inline queries have no chat, so the sender id is
    used.
    """
    if isinstance(event, events.InlineQuery.Event):
        user_id = event.sender_id
    else:
        user_id = event.chat_id

    async with get_session() as session:
        language = await UserRepository(session).get_language(user_id)

    return ctx.language_service.get_translator(language or "english")


async def get_restricted_mode(user_id: int) -> bool | None:
    async with get_session() as session:
        return await UserRepository(session).get_restricted_mode(user_id)


def is_explicit_hidden(data: dict[str, Any], restricted_mode: bool | None) -> bool:
    """Whether restricted mode hides this torrent."""
    title = data.get("name") or data.get("title")

    return bool(restricted_mode and title and ctx.explicit_detector.predict(title))


async def is_admin(user_id: int) -> bool:
    async with get_session() as session:
        return await AdminRepository(session).is_admin(user_id)


async def is_chat_admin(event: Any, t: Translator, alert: bool = True) -> bool:
    """Allow private chats and group admins; alert other group members."""
    if event.is_private:
        return True

    try:
        permissions = await event.client.get_permissions(event.chat_id, event.sender_id)
        if permissions.is_admin:
            return True
    except Exception as err:
        logger.warning("Error checking chat admin rights", error=str(err))

    if alert:
        text = t.get("noPermission")
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer(text, alert=True)
        else:
            await event.reply(text)

    return False


def match_command(event: events.NewMessage.Event, word: str) -> bool:
    """Match a slash command or a reply-keyboard button in any language.

    Slash commands ("/settings", "/settings@bot") match on the first word.
    Reply-keyboard buttons send their full localized label as plain text,
    so the whole text is matched against every translation of `<word>Cmd`.
    Matching spans all languages, not just the user's current one, so a
    stale keyboard from before a language switch keeps working.
    """
    text = (event.raw_text or "").strip()
    if not text:
        return False

    if text.startswith("/"):
        first_word = re.sub(r"^/([^@\s]+).*", r"\1", text, flags=re.S)
        return first_word == word

    return text == word or text in ctx.language_service.translations(f"{word}Cmd")


def search_guard(event: events.NewMessage.Event) -> bool:
    """Predicate for the catch-all text search handler."""
    text = event.raw_text or ""

    # Commands never fall through to search
    if not text or text.startswith("/"):
        return False

    # Skip messages produced by this bot's own inline results
    return not (event.message.via_bot_id and ctx.me and event.message.via_bot_id == ctx.me.id)


async def message_admins(client: TelegramClient, text_key: str) -> None:
    """Send a translated message to every bot admin."""
    async with get_session() as session:
        admin_ids = await AdminRepository(session).ids()

    for admin_id in admin_ids:
        try:
            async with get_session() as session:
                language = await UserRepository(session).get_language(admin_id)

            t = ctx.language_service.get_translator(language or "english")

            await client.send_message(admin_id, t.get(text_key), buttons=main_keyboard(t))
        except Exception as err:
            logger.warning("Error sending message to admin", admin_id=admin_id, error=str(err))


async def load_sites() -> None:
    """Fetch the sites available for inline search from the search provider."""
    sources = await ctx.search.sources()

    ctx.sites = {
        source.id: {"website": source.name} for source in sources.items
    }

    logger.info(
        "Loaded inline search sites",
        count=len(ctx.sites),
        provider=ctx.search.provider.name,
    )
