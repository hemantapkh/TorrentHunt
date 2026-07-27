"""Database engine and session management."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from asyncpg import Connection as asyncpg_connection
from config import APP_DIR, settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from structlog import get_logger

from database.models.base import Base

logger = get_logger(__name__)

connection_string = (
    settings.database_url
    .replace("sqlite://", "sqlite+aiosqlite://")
    .replace("postgres://", "postgresql+asyncpg://")
    .replace("postgresql://", "postgresql+asyncpg://")
)

# Anchor relative sqlite paths to the app directory so the database file
# is the same no matter where the app is launched from
_sqlite_prefix = "sqlite+aiosqlite:///"
if connection_string.startswith(_sqlite_prefix):
    db_path = connection_string.removeprefix(_sqlite_prefix)
    if not db_path.startswith("/"):
        connection_string = _sqlite_prefix + str(APP_DIR / db_path)

connection_args: dict[str, object] = {}
if "postgresql+asyncpg://" in connection_string:
    # https://github.com/sqlalchemy/sqlalchemy/issues/6467#issuecomment-864943824
    class Connection(asyncpg_connection):
        def _get_unique_id(self, prefix: str) -> str:
            return f"__asyncpg_{prefix}_{uuid4()}__"

    connection_args = {
        "connection_class": Connection,
    }

engine = create_async_engine(
    connection_string,
    connect_args=connection_args,
)

# expire_on_commit=False keeps ORM objects usable after the session closes,
# avoiding DetachedInstanceError on objects returned to handlers
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Session scope: commits on success, rolls back on error."""
    async with Session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    logger.info("Creating metadata for database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
