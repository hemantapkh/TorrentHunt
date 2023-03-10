'Main app'

import asyncio
from os import environ, path

import uvloop
from dotenv import load_dotenv
from loguru import logger
from pyrogram import Client

from apis.database import DataBase

# Installing UVloop for better performance
logger.info('Installing uvloop')
uvloop.install()

# Loading variables from .env file
logger.info('Loading variables from .env file')
load_dotenv()

# Configure logger to write logs to file and console
logger.add(
    f"{environ['WORKDIR']}/logs",
    backtrace=True,
    rotation='10 MB',
)

# Finding the absolute path of the config file
scriptPath = path.abspath(__file__)
dirPath = path.dirname(scriptPath)

logger.info('Creating database instance')
Client.DB = DataBase(
    user=environ.get('DATABASE_USERNAME'),
    password=environ.get('DATABASE_PASSWORD'),
    database=environ.get('DATABASE_URL'),
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

if __name__ == '__main__':
    logger.info(f"Starting {environ.get('BOT_NAME')}")
    asyncio.run(bot.run())
