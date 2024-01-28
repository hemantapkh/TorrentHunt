"""Initialize the requirements for bot"""

from os import environ

import pyrogram
from loguru import logger


class Init:
    def __init__(self, Client):
        self.Client = Client

    async def init(self):
        await self.add_admins()
        await self.add_commands()

    async def add_admins(self):
        admins = environ.get("BOT_ADMINS")

        if admins:
            logger.info("Adding admins to database")
            for admin in admins.split(","):
                await self.Client.DB.query(
                    "execute",
                    """INSERT INTO ADMINS (user_id) VALUES ($1)
                        ON CONFLICT (user_id) DO NOTHING""",
                    int(admin),
                )

    async def add_commands(self):
        logger.info("Setting bot commands")

        # Commands for private chats
        await self.Client.set_bot_commands(
            commands=default_commands,
            scope=pyrogram.types.BotCommandScopeAllPrivateChats(),
        )

        # Commands for group chats
        await self.Client.set_bot_commands(
            commands=group_commands,
            scope=pyrogram.types.BotCommandScopeAllGroupChats(),
        )

        # Commands for chat admins
        await self.Client.set_bot_commands(
            commands=group_commands_admins,
            scope=pyrogram.types.BotCommandScopeAllChatAdministrators(),
        )

        # Commands for bot admins
        admins = (
            await self.Client.DB.query(
                "fetch",
                "SELECT user_id FROM ADMINS",
            )
            or []
        )

        for admin in admins:
            try:
                await self.Client.set_bot_commands(
                    commands=admin_commands,
                    scope=pyrogram.types.BotCommandScopeChat(
                        chat_id=admin.get("user_id"),
                    ),
                )
            except pyrogram.errors.exceptions.bad_request_400.PeerIdInvalid as err:
                logger.error(f"Error setting commands for admins: {err}")


all_commands = [
    pyrogram.types.BotCommand("start", "💫 Start using bot"),
    pyrogram.types.BotCommand("bookmarks", "🔖 View your bookmarks"),
    pyrogram.types.BotCommand("settings", "⚙️ Change bot settings"),
    pyrogram.types.BotCommand("search", "🔍 Search for torrents"),
    pyrogram.types.BotCommand("stats", "📊 See bot stats"),
]

default_commands = [
    all_commands[0],
    all_commands[1],
    all_commands[2],
]

group_commands = [
    all_commands[3],
]

group_commands_admins = [
    all_commands[3],
    all_commands[2],
]

admin_commands = default_commands + [all_commands[4]]
