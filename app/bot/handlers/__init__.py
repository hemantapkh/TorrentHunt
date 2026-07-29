"""Explicit handler registration table.

The entire routing map lives here, in one place. Order matters for
NewMessage and InlineQuery handlers: `setup_handler` raises StopPropagation
after a handler runs, so specific handlers must be registered before
catch-alls (the text search and the unfiltered inline search).
"""

from telethon import events

from bot.handlers import bookmarks, inline, reload, search, settings, start, stats
from bot.helpers import match_command, search_guard


def register_handlers(client):
    # Commands — must be registered before the catch-all text search
    client.add_event_handler(
        start.start,
        events.NewMessage(incoming=True, pattern=r"^/start"),
    )
    client.add_event_handler(
        stats.stats,
        events.NewMessage(incoming=True, pattern=r"^/stats"),
    )
    client.add_event_handler(
        reload.reload,
        events.NewMessage(incoming=True, pattern=r"^/reload"),
    )
    client.add_event_handler(
        settings.settings_menu,
        events.NewMessage(incoming=True, func=lambda e: match_command(e, "settings")),
    )
    client.add_event_handler(
        bookmarks.bookmarks_menu,
        events.NewMessage(incoming=True, func=lambda e: e.is_private and match_command(e, "bookmarks")),
    )
    client.add_event_handler(
        search.group_search,
        events.NewMessage(incoming=True, func=lambda e: not e.is_private and match_command(e, "search")),
    )
    client.add_event_handler(
        search.get_link,
        events.NewMessage(incoming=True, pattern=r"^/getLink_"),
    )

    # Catch-all text search — always last among NewMessage handlers
    client.add_event_handler(
        search.text_search,
        events.NewMessage(incoming=True, func=search_guard),
    )

    # Callbacks — search
    client.add_event_handler(
        search.results_page,
        events.CallbackQuery(pattern=rb"^res_"),
    )
    client.add_event_handler(
        search.page_picker,
        events.CallbackQuery(pattern=rb"^pages_"),
    )
    client.add_event_handler(
        search.site_picker,
        events.CallbackQuery(pattern=rb"^sites_"),
    )
    client.add_event_handler(
        search.sort_picker,
        events.CallbackQuery(pattern=rb"^sort_"),
    )
    client.add_event_handler(
        search.category_picker,
        events.CallbackQuery(pattern=rb"^cats_"),
    )
    client.add_event_handler(
        search.open_torrent,
        events.CallbackQuery(pattern=rb"^get_"),
    )
    client.add_event_handler(
        search.noop,
        events.CallbackQuery(pattern=rb"^noop$"),
    )

    # Callbacks — settings
    client.add_event_handler(
        settings.language_menu,
        events.CallbackQuery(pattern=rb"^language$"),
    )
    client.add_event_handler(
        settings.set_language,
        events.CallbackQuery(pattern=rb"^setLanguage"),
    )
    client.add_event_handler(
        settings.restriction,
        events.CallbackQuery(pattern=rb"^restriction_"),
    )

    # Callbacks — bookmarks
    client.add_event_handler(
        bookmarks.add_bookmark,
        events.CallbackQuery(pattern=rb"^addToBookmark_"),
    )
    client.add_event_handler(
        bookmarks.remove_bookmark,
        events.CallbackQuery(pattern=rb"^removeFromBookmark_"),
    )

    # Inline queries — bookmarks first, then the catch-all torrent search
    client.add_event_handler(
        bookmarks.bookmarks_inline,
        events.InlineQuery(pattern=r"^#bookmarks"),
    )
    client.add_event_handler(
        inline.inline_search,
        events.InlineQuery(),
    )
