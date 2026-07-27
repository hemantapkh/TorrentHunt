from contextlib import suppress

from localization import Translator
from telethon import TelegramClient, errors, events

from bot.context import ctx
from bot.decorators import setup_handler
from bot.helpers import get_restricted_mode, is_explicit_hidden
from bot.views.callbacks import SearchState
from bot.views.search_view import (
    page_count,
    render_category_picker,
    render_group_search_prompt,
    render_page_picker,
    render_search_results,
    render_searching,
    render_site_picker,
    render_sort_picker,
)
from bot.views.torrent_view import render_torrent


async def render_results(
    client: TelegramClient,
    chat_id: int,
    message_id: int,
    state: SearchState,
    t: Translator,
) -> None:
    """Search and render one page of results into an existing message."""
    response = await ctx.search.search(state.query, category=state.category)

    view = render_search_results(
        response.to_dict(),
        t,
        state,
        username=ctx.me.username or "",
        sites=ctx.sites,
    )

    with suppress(errors.MessageNotModifiedError):
        await client.edit_message(
            chat_id,
            message_id,
            view.message or "",
            buttons=view.buttons,
            link_preview=False,
        )


async def send_torrent(
    event: events.NewMessage.Event | events.CallbackQuery.Event,
    t: Translator,
    torrent_id: str,
    reply_to: int | None = None,
    edit_message: int | None = None,
) -> None:
    """Resolve a torrent and deliver its magnet message."""
    restricted_mode = await get_restricted_mode(event.sender_id)

    torrent = await ctx.search.get_torrent(torrent_id)
    data = torrent.to_dict() if torrent else {}

    view = render_torrent(
        data,
        t,
        explicit_hidden=is_explicit_hidden(data, restricted_mode),
    )

    if edit_message:
        await event.client.edit_message(
            event.chat_id, edit_message, view.message, buttons=view.buttons,
        )
    else:
        await event.respond(view.message, buttons=view.buttons, reply_to=reply_to)


@setup_handler(track_user=True)
async def text_search(event: events.NewMessage.Event, client: TelegramClient, t: Translator) -> None:
    # Truncate to the max length that fits in the keyboard's callback data
    query = event.raw_text[:46]

    view = render_searching(query, t)
    message = await event.respond(view.message, reply_to=event.id)

    await render_results(
        client,
        chat_id=event.chat_id,
        message_id=message.id,
        state=SearchState(query=query),
        t=t,
    )


@setup_handler()
async def results_page(event: events.CallbackQuery.Event, client: TelegramClient, t: Translator) -> None:
    await render_results(
        client,
        chat_id=event.chat_id,
        message_id=event.message_id,
        state=SearchState.unpack(event.data),
        t=t,
    )

    await event.answer()


@setup_handler()
async def page_picker(event: events.CallbackQuery.Event, t: Translator) -> None:
    state = SearchState.unpack(event.data)

    response = await ctx.search.search(state.query, category=state.category)

    view = render_page_picker(state, page_count(len(response.items)), t)
    await event.edit(buttons=view.buttons)


@setup_handler()
async def sort_picker(event: events.CallbackQuery.Event, t: Translator) -> None:
    view = render_sort_picker(SearchState.unpack(event.data), t)
    await event.edit(buttons=view.buttons)


@setup_handler()
async def category_picker(event: events.CallbackQuery.Event, t: Translator) -> None:
    view = render_category_picker(SearchState.unpack(event.data), t)
    await event.edit(buttons=view.buttons)


@setup_handler()
async def site_picker(event: events.CallbackQuery.Event, t: Translator) -> None:
    view = render_site_picker(SearchState.unpack(event.data), ctx.sites, t)
    await event.edit(buttons=view.buttons)


@setup_handler()
async def noop(event: events.CallbackQuery.Event) -> None:
    await event.answer()


@setup_handler()
async def open_torrent(event: events.CallbackQuery.Event, t: Translator) -> None:
    torrent_id = event.data.decode().split("_")[1]

    await send_torrent(event, t, torrent_id, reply_to=event.message_id)
    await event.answer()


@setup_handler()
async def get_link(event: events.NewMessage.Event, t: Translator) -> None:
    torrent_id = event.raw_text.split("_")[1].split("@")[0]

    message = await event.respond(t.get("fetchingTorrentInfo"), reply_to=event.id)
    await send_torrent(event, t, torrent_id, edit_message=message.id)


@setup_handler(track_user=True)
async def group_search(event: events.NewMessage.Event, t: Translator) -> None:
    view = render_group_search_prompt(t)

    await event.respond(view.message, buttons=view.buttons, reply_to=event.id)
