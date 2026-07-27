"""Views for the bookmarks flow."""

from localization import Translator
from telethon import Button

from bot.views import ViewResponse


def render_bookmarks_menu(t: Translator) -> ViewResponse:
    """Entry point into the inline bookmark list."""
    return ViewResponse(
        message=t.get("bookmarks"),
        buttons=[
            [
                Button.switch_inline(
                    t.get("bookmarksCmd"),
                    query="#bookmarks",
                    same_peer=True,
                ),
            ],
        ],
    )
