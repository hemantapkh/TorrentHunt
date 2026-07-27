from config import settings
from database import get_session
from database.repositories import UserRepository
from localization import Translator
from telethon import TelegramClient, events

from bot.context import ctx
from bot.decorators import setup_handler
from bot.helpers import get_restricted_mode
from bot.views.settings_view import (
    render_greet,
    render_language_selected,
    render_restriction_changed,
    render_settings_menu,
)
from bot.views.shared_view import render_language_menu


async def send_language_menu(event: events.NewMessage.Event, t: Translator, welcome: bool = False) -> None:
    """Prompt for a language; shared by /start and the settings callback."""
    view = render_language_menu(t, ctx.language_service.config, welcome=welcome)

    await event.respond(view.message, buttons=view.buttons, reply_to=event.id)


@setup_handler(chat_admin=True)
async def settings_menu(event: events.NewMessage.Event, t: Translator) -> None:
    restriction_mode = await get_restricted_mode(event.chat_id)

    view = render_settings_menu(t, restriction_mode)

    await event.respond(view.message, buttons=view.buttons, reply_to=event.id)


# Show language options
@setup_handler(chat_admin=True)
async def language_menu(event: events.CallbackQuery.Event, t: Translator) -> None:
    view = render_language_menu(t, ctx.language_service.config)

    await event.edit(view.message, buttons=view.buttons)


@setup_handler(chat_admin=True)
async def set_language(event: events.CallbackQuery.Event, client: TelegramClient) -> None:
    data = event.data.decode()
    new_user = data.startswith("setLanguageNew")
    language = data.split("_")[1]

    async with get_session() as session:
        await UserRepository(session).set_language(event.chat_id, language)

    await event.delete()

    # Translator for the newly chosen language
    t = ctx.language_service.get_translator(language)

    # Send welcome message if New user
    if new_user:
        sender = await event.get_sender()

        view = render_greet(
            t,
            sender.first_name if sender else "",
            private=event.is_private,
        )
        await client.send_message(event.chat_id, view.message or "", buttons=view.buttons)

        # Send ads on start if configured
        if settings.start_ads:
            await client.forward_messages(
                event.chat_id,
                int(settings.start_ads_message),
                settings.start_ads_channel,
            )

    # Send language selected message if not new user
    else:
        view = render_language_selected(t, private=event.is_private)
        await client.send_message(event.chat_id, view.message or "", buttons=view.buttons)


# Turn on or off restricted mode
@setup_handler(chat_admin=True)
async def restriction(event: events.CallbackQuery.Event, t: Translator) -> None:
    restriction_value = event.data.decode().split("_")[1]

    async with get_session() as session:
        await UserRepository(session).set_restricted_mode(
            event.chat_id,
            restriction_value == "True",
        )

    view = render_restriction_changed(t, restriction_value)
    await event.edit(view.message)
