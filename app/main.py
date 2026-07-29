import asyncio
from os import path
from sys import argv
from typing import cast

import sentry_sdk
import uvloop
from bot.commands import set_command_menus
from bot.context import ctx
from bot.handlers import register_handlers
from bot.helpers import load_sites, message_admins
from config import APP_DIR, settings  # noqa: I001
from database import get_session, init_db
from database.repositories import AdminRepository
from localization import LanguageService
from logging_config import configure_logging
from models.explicit_detector.explicit_detector import ExplicitDetector
from search_engine import create_provider
from services.jobs import start_background_jobs
from services.search import SearchService
from services.torrent_store import DatabaseTorrentStore
from structlog import get_logger
from telethon import TelegramClient
from telethon.tl.types import User

configure_logging(settings.environment)
logger = get_logger(__name__)

# Initializing sentry for error tracking
sentry_sdk.init(dsn=settings.sentry_dsn or None, environment=settings.environment)

# Installing UVloop for better performance
logger.info("Installing uvloop")
uvloop.install()

logger.info("Creating bot instance")
workdir = settings.workdir or APP_DIR
bot = TelegramClient(
    session=path.join(workdir, "torrenthunt.session"),
    api_id=settings.api_id,
    api_hash=settings.api_hash,
)
bot.parse_mode = "html"

# Wiring the application context
logger.info("Initializing application context")
ctx.language_service = LanguageService(APP_DIR / "localization")
ctx.explicit_detector = ExplicitDetector()

logger.info("Initializing torrent search service")
torrent_store = DatabaseTorrentStore(retention_days=settings.torrent_cache_days)
provider_kwargs = {
    "message_search_tag": settings.message_search_tag,
    "inline_search_tag": settings.inline_search_tag,
}
if settings.torrent_provider == "prowlarr":
    provider_kwargs.update({
        "base_url": settings.prowlarr_url,
        "api_key": settings.prowlarr_api_key,
        "indexer": settings.prowlarr_indexer,
        "timeout": settings.prowlarr_timeout,
    })
else:
    provider_kwargs.update({
        "base_url": settings.jackett_url,
        "api_key": settings.jackett_api_key,
        "indexer": settings.jackett_indexer,
        "timeout": settings.jackett_timeout,
    })

ctx.search = SearchService(
    provider=create_provider(
        settings.torrent_provider,
        **provider_kwargs
    ),
    store=torrent_store,
)


async def seed_admins() -> None:
    """Store the configured admin ids in the database."""
    if not settings.bot_admins:
        return

    logger.info("Adding admins to database")
    async with get_session() as session:
        for user_id in settings.bot_admins.split(","):
            try:
                await AdminRepository(session).add(int(user_id))
            except ValueError:
                logger.warning("Invalid admin user id", user_id=user_id)


async def main() -> None:
    # Telethon's start() returns a coroutine when a loop is running
    await bot.start(bot_token=settings.bot_token)  # ty: ignore[invalid-await]

    await init_db()

    if "--no-init" not in argv:
        await seed_admins()
        await set_command_menus(bot)

    logger.info("Getting bot information")
    ctx.me = cast(User, await bot.get_me())

    logger.info("Registering handlers")
    register_handlers(bot)

    await load_sites()
    await message_admins(bot, "botRestarted")

    logger.info("Starting background jobs")
    jobs = start_background_jobs(
        [
            ("torrent-cache-cleanup", settings.cleanup_interval_minutes * 60, torrent_store.prune),
        ],
    )

    logger.info(f"Starting {settings.bot_name}")
    try:
        await bot.run_until_disconnected()
    finally:
        for job in jobs:
            job.cancel()


if __name__ == "__main__":
    asyncio.run(main())
