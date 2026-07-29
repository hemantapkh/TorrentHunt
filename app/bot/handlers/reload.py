"""Admin command to reload indexer data from the search provider."""

from bot.context import ctx
from bot.decorators import setup_handler
from bot.helpers import load_sites
from localization import Translator
from telethon import events


@setup_handler(admin=True)
async def reload(event: events.NewMessage.Event, t: Translator) -> None:
    """Clear cached provider state and refresh the inline site list."""
    await ctx.search.reload()
    await load_sites()
    await event.respond(t.get("configReloaded"))
