'Main app'

import asyncio
from os import environ

import uvloop
from dotenv import load_dotenv
from loguru import logger
from py1337x import py1337x
from pyrogram import Client, filters, types

from apis.database import DataBase
from apis.requests import Requests
from apis.torrenthunt import TorrentHunt
from langs.lang import Lang
from plugins.blueprint.schema import Schema
from plugins.functions.filters import Filter
from plugins.functions.keyboards import KeyBoard
from plugins.functions.misc import Misc

# Installing UVloop for better performance
logger.info('Installing uvloop')
uvloop.install()

# Loading variables from .env file
logger.info('Loading variables from .env file')
load_dotenv()

# Configure logger to write logs to file and console
logger.add(
    f"{environ.get('WORKDIR')}/logs/logs",
    backtrace=True,
    rotation='10 MB',
)

logger.info('Creating database instance')
Client.DB = DataBase(
    dsn=environ.get('DATABASE_DSN'),
    user=environ.get('DATABASE_USERNAME'),
    password=environ.get('DATABASE_PASSWORD'),
    database=environ.get('DATABASE_NAME'),
)

logger.info('Creating bot instance')
bot = Client(
    name=environ.get('BOT_NAME'),
    api_id=environ.get('API_ID'),
    api_hash=environ.get('API_HASH'),
    bot_token=environ.get('BOT_TOKEN'),
    plugins=dict(root='plugins'),
    workdir=environ.get('WORKDIR'),
)

# Loading required instances in the Client
Client.TH = TorrentHunt(
    environ.get('TORRENTHUNT_API_URL'),
    environ.get('TORRENTHUNT_API_KEY'),
)
Client.MISC = Misc(bot)
Client.KB = KeyBoard(bot)
Client.LG = Lang('langs/string.json', 'langs/lang.json')
Client.requests = Requests()
Client.py1337x = py1337x()
Client.STRUCT = Schema(bot)
filters.CF = Filter(bot)

commands = [
    types.BotCommand('start', '💫 Start using bot'),
    types.BotCommand('settings', '⚙️ Change bot settings'),
]

group_commands = [
    types.BotCommand('search', '🔍 Search for torrents'),
]

group_commands_admins = [
    types.BotCommand('search', '🔍 Search for torrents'),
    types.BotCommand('settings', '⚙️ Change bot settings'),
]


async def main():
    async with bot:
        logger.info('Getting bot information')
        me = await bot.get_me()
        Client.USERNAME = me.username

        logger.info('Setting bot commands')

        await bot.set_bot_commands(
            commands=[],
            scope=types.BotCommandScopeDefault(),
        )

        await bot.set_bot_commands(
            commands=group_commands,
            scope=types.BotCommandScopeAllGroupChats(),
        )

        await bot.set_bot_commands(
            commands=group_commands_admins,
            scope=types.BotCommandScopeAllChatAdministrators(),
        )

        await bot.set_bot_commands(
            commands=commands,
            scope=types.BotCommandScopeAllPrivateChats(),
        )

        # Initializing bot
        await bot.MISC.init_bot()

if __name__ == '__main__':
    logger.info(f"Starting {environ.get('BOT_NAME')}")
    bot.run(main())
    asyncio.run(bot.run())
