from contextlib import suppress

from database import get_session
from database.repositories import ReferrerRepository, UserRepository
from localization import Translator
from telethon import events

from bot.decorators import setup_handler
from bot.handlers.search import send_torrent
from bot.handlers.settings import send_language_menu


@setup_handler()
async def start(event: events.NewMessage.Event, t: Translator) -> None:
    parts = event.raw_text.split()
    params = parts[-1] if len(parts) > 1 else None

    # Deep link from a search result title: deliver the torrent and drop
    # the /start command message so the chat stays clean
    if params and params.startswith("get_"):
        async with get_session() as session:
            await UserRepository(session).upsert_from_event(event)

        await send_torrent(event, t, params[4:])

        # Deleting fails without delete rights (e.g. some group setups)
        with suppress(Exception):
            await event.delete()

        return

    referrer = None
    if params:
        try:
            # If params is a registered user
            user_id = int(params)
            async with get_session() as session:
                referrer = user_id if await UserRepository(session).exists(user_id) else None

        except ValueError:
            # If params is a valid tracking ID
            async with get_session() as session:
                clicked = await ReferrerRepository(session).track_click(params)
            referrer = params if clicked else None

    async with get_session() as session:
        await UserRepository(session).upsert_from_event(event, referrer)

    await send_language_menu(event, t, welcome=True)
