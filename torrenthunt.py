'Main app'

import asyncio
from os import environ
from sys import argv

import uvloop
from dotenv import load_dotenv
from loguru import logger
from py1337x import py1337x
from pyrogram import Client, filters

from apis.database import DataBase
from apis.requests import Requests
from apis.torrenthunt import TorrentHunt
from langs.lang import Lang
from plugins.blueprint.schema import Schema
from plugins.functions.filters import Filter
from plugins.functions.init import Init
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
    dsn=environ.get('DATABASE_URL'),
    user=environ.get('DATABASE_USERNAME') or None,
    password=environ.get('DATABASE_PASSWORD') or None,
    database=environ.get('DATABASE_NAME') or None,
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
    environ.get('TORRENTHUNT_API_KEY'),
)
Client.MISC = Misc(bot)
Client.KB = KeyBoard(bot)
Client.LG = Lang('langs/string.json', 'langs/lang.json')
Client.requests = Requests()
Client.py1337x = py1337x()
Client.STRUCT = Schema(bot)
filters.CF = Filter(bot)


async def main():
    async with bot:
        if '--no-init' not in argv:
            logger.info('Initializing requirements for bot')
            bot_init = Init(bot)
            await bot_init.init()

        logger.info('Getting bot information')
        me = await bot.get_me()
        Client.USERNAME = me.username

        # Fetching config from API
        await bot.MISC.fetch_config()

if __name__ == '__main__':
    bot.run(main())
    logger.info(f"Starting {environ.get('BOT_NAME')}")
    asyncio.run(bot.run())
