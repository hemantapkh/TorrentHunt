"""View for a single torrent: the magnet message and its buttons."""

from html import escape
from typing import Any

from localization import Translator
from telethon import Button

from bot.views import ViewResponse

# The magnet message. The bookmark handler parses the rendered message's
# plain text back into fields (bot/handlers/bookmarks.py) — keep the line
# structure stable when restyling.
content_template = """{magnet_icon} <b>{title}</b>
<blockquote>{size_str}: {size}
{seeders_str}: {seeders}
{leechers_str}: {leechers}
{uploaded_on_str}: {uploaded_on}</blockquote>
<b>{magnet_link_str}: </b><code>{magnet}</code>
"""


def render_torrent(
    data: dict[str, Any],
    t: Translator,
    explicit_hidden: bool = False,
    bookmarked: bool = False,
) -> ViewResponse:
    title = data.get("name") or data.get("title")

    # Unresolvable torrent (expired id, bad data)
    if not title:
        return ViewResponse(message=t.get("errorFetchingLink"))

    # Summary line for inline results
    description = "{} {}, {} {}, {} {}, {} {}".format(
        t.get("storageIcon"),
        data.get("size"),
        t.get("seedersIcon"),
        data.get("seeders"),
        t.get("leechersIcon"),
        data.get("leechers"),
        t.get("dateIcon"),
        data.get("uploaded_on"),
    )

    # Hidden by restricted mode
    if explicit_hidden:
        return ViewResponse(message=t.get("cantView"), description=description)

    message = content_template.format(
        magnet_icon=t.get("magnetIcon"),
        title=escape(title),
        size=data.get("size"),
        seeders=data.get("seeders"),
        leechers=data.get("leechers"),
        uploaded_on=data.get("date_uploaded") or data.get("uploadDate") or data.get("uploaded_on"),
        magnet=escape(data.get("magnet_link") or data.get("magnetLink") or data.get("magnet") or ""),
        size_str=t.get("size"),
        seeders_str=t.get("seeders"),
        leechers_str=t.get("leechers"),
        uploaded_on_str=t.get("uploadedOn"),
        magnet_link_str=t.get("link"),
    )

    hash = data.get("info_hash") or data.get("infoHash") or data.get("hash")

    if bookmarked:
        bookmark_button = Button.inline(
            t.get("removeFromBookmarkBtn"),
            f"removeFromBookmark_{hash}".encode(),
        )
    else:
        bookmark_button = Button.inline(
            t.get("addToBookmarkBtn"),
            f"addToBookmark_{hash}".encode(),
        )

    buttons = [
        [bookmark_button],
        [
            Button.url(
                t.get("addToSeedrBtn"),
                f"https://t.me/torrentseedrbot?start=addTorrent_{hash}",
            ),
        ],
    ]

    return ViewResponse(message=message, buttons=buttons, description=description)
