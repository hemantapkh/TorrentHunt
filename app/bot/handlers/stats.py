from database import get_session
from database.repositories import UserRepository
from localization import Translator
from telethon import events

from bot.decorators import setup_handler


@setup_handler(admin=True)
async def stats(event: events.NewMessage.Event, t: Translator) -> None:
    async with get_session() as session:
        users = UserRepository(session)
        total_users = await users.count()
        joined_today = await users.count_joined_today()

    await event.respond(t.get("userStats").format(total_users, joined_today))
