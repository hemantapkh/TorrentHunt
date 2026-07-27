from localization import Translator
from structlog import get_logger
from telethon import events
from telethon.tl import types as tl_types

from bot.context import ctx
from bot.decorators import setup_handler
from bot.helpers import get_restricted_mode, is_explicit_hidden
from bot.views.torrent_view import render_torrent

logger = get_logger(__name__)

PAGE_SIZE = 10

FALLBACK_THUMB = (
    "https://raw.githubusercontent.com/hemantapkh/torrenthunt/main/images/torrenthunt.jpg"
)


def thumb(url: str) -> tl_types.InputWebDocument:
    return tl_types.InputWebDocument(url=url, size=0, mime_type="image/jpeg", attributes=[])


@setup_handler()
async def inline_search(event: events.InlineQuery.Event, t: Translator) -> None:
    restricted_mode = await get_restricted_mode(event.sender_id)
    query_list = event.text.split()
    results = []
    next_offset = None

    # Optional !site prefix restricts the search to a single source
    if query_list and query_list[0].startswith("!"):
        source = query_list[0][1:]
        keyword = " ".join(query_list[1:])
    else:
        source = None
        keyword = " ".join(query_list)

    if keyword:
        page = int(event.offset) if event.offset else 1
        logger.info("Inline searching", keyword=keyword, source=source or "all", page=page)

        response = await ctx.search.search(keyword, source=source)

        start = (page - 1) * PAGE_SIZE
        items = response.items[start : start + PAGE_SIZE]

        if items:
            pm_text = t.get("resultsFor").format(keyword)

            for torrent in items:
                data = torrent.to_dict()
                view = render_torrent(
                    data,
                    t,
                    explicit_hidden=is_explicit_hidden(data, restricted_mode),
                )
                results.append(
                    event.builder.article(
                        title=torrent.name,
                        description=view.description,
                        text=view.message,
                        buttons=view.buttons,
                        thumb=thumb(FALLBACK_THUMB),
                        link_preview=False,
                    ),
                )

            if start + PAGE_SIZE < len(response.items):
                next_offset = page + 1

        # No results found
        else:
            pm_text = t.get("noResults")

    # If keyword is empty
    else:
        pm_text = t.get("keywordToSearch")

    await event.answer(
        results,
        cache_time=10,
        next_offset=str(next_offset) if next_offset else None,
        switch_pm=pm_text,
        switch_pm_param="inlineQuery",
    )
