"""Bring the database schema up to date. Runs before the bot starts (see Dockerfile).

    python app/migrate.py

Databases created before Alembic was introduced already have the baseline tables but no
migration history; those are stamped at the baseline first, so only newer migrations run.
"""

import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config
from config import settings
from database.session import engine
from logging_config import configure_logging
from sqlalchemy import inspect
from structlog import get_logger

# The schema as it was when Alembic was introduced (see migrations/versions/*baseline*).
BASELINE_REVISION = "d55a310ce8e8"
APP_DIR = Path(__file__).resolve().parent

logger = get_logger(__name__)


async def _existing_tables() -> set[str]:
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
    await engine.dispose()  # don't carry connections over to the bot's event loop
    return set(tables)


def migrate() -> None:
    config = Config(str(APP_DIR / "alembic.ini"))
    tables = asyncio.run(_existing_tables())
    if "users" in tables and "alembic_version" not in tables:
        logger.info("Existing database without migration history: stamping the baseline")
        command.stamp(config, BASELINE_REVISION)
    logger.info("Applying database migrations")
    command.upgrade(config, "head")


if __name__ == "__main__":
    configure_logging(settings.environment)
    migrate()
