"Main app"

import asyncio
from os import environ
from sys import argv

import uvloop
import sentry_sdk
from loguru import logger
from pyrogram import Client, filters

from apis.requests import Requests
from apis.torrenthunt import TorrentHunt
from database import DataBase
from database.models import init_models
from init import exec_dir
from langs.lang import Lang
from models.explicit_detector.explicit_detector import ExplicitDetector
from plugins.blueprint.schema import Schema
from plugins.functions.filters import Filter
from plugins.functions.init import Init
from plugins.functions.keyboards import KeyBoard
from plugins.functions.misc import Misc
from py1337x import AsyncPy1337x
from pyrogram import Client, filters

# Initializing sentry for error tracking
sentry_sdk.init(
    dsn=environ.get("SENTRY_DSN"),
    environment=environ.get("ENVIRONMENT") or "local"
)

# Installing UVloop for better performance
logger.info("Installing uvloop")
uvloop.install()

logger.info("Creating database instance")
Client.DB = DataBase()

logger.info("Creating bot instance")
bot = Client(
    name=environ.get("BOT_NAME") or "Torrent Hunt",
    api_id=environ.get("API_ID"),
    api_hash=environ.get("API_HASH"),
    bot_token=environ.get("BOT_TOKEN"),
    plugins=dict(root="plugins"),
    workdir=environ.get("WORKDIR") or exec_dir,
)

# Loading required instances in the Client
Client.torrent_hunt_api = TorrentHunt(
    environ.get("TORRENTHUNT_API_KEY"),
)
Client.sites = {}
Client.misc = Misc(bot)
Client.keyboard = KeyBoard(bot)
Client.language = Lang("langs/string.json", "langs/lang.json")
Client.requests = Requests()
Client.py1337x = AsyncPy1337x()
Client.struct = Schema(bot)
filters.custom = Filter(bot)
Client.explicit_detector = ExplicitDetector()

    
async def main():
    async with bot:
        await init_models()
        if "--no-init" not in argv:
            logger.info("Initializing requirements for bot")
            bot_init = Init(bot)
            await bot_init.init()

        logger.info("Getting bot information")
        me = await bot.get_me()
        Client.USERNAME = me.username

        # Fetching config from API
        await bot.misc.fetch_config()


if __name__ == "__main__":
    bot.run(main())
    logger.info(f"Starting {environ.get('BOT_NAME')}")
    asyncio.run(bot.run())
