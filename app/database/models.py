from os import environ
from uuid import uuid4

from asyncpg import Connection as asyncpg_connection
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

logger.info("Loading variables from .env file")
load_dotenv()

connection_string = (
    environ.get("DATABASE_URL", "")
    .replace("sqlite://", "sqlite+aiosqlite://")
    .replace("postgres://", "postgresql+asyncpg://")
    .replace("postgresql://", "postgresql+asyncpg://")
)

connection_args = {}
if "postgresql+asyncpg://" in connection_string:
    # https://github.com/sqlalchemy/sqlalchemy/issues/6467#issuecomment-864943824
    class Connection(asyncpg_connection):
        def _get_unique_id(self, prefix: str) -> str:
            return f"__asyncpg_{prefix}_{uuid4()}__"

    connection_args = {
        "connection_class": Connection,
    }

Base = declarative_base()

engine = create_async_engine(
    connection_string,
    connect_args=connection_args,
)
Session = sessionmaker(bind=engine, class_=AsyncSession)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, index=True)
    user_type = Column(String, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    referrer = Column(String)
    join_date = Column(TIMESTAMP, server_default=func.current_timestamp(), index=True)
    last_active = Column(TIMESTAMP, server_default=func.current_timestamp())

    setting = relationship("Setting", uselist=False, back_populates="user")


class Setting(Base):
    __tablename__ = "settings"

    user_id = Column(
        BigInteger, ForeignKey("users.user_id"), primary_key=True, index=True
    )
    language = Column(String, default="english")
    restricted_mode = Column(Boolean, default=True)

    user = relationship("User", back_populates="setting", foreign_keys=[user_id])


class Bookmark(Base):
    __tablename__ = "bookmarks"

    user_id = Column(
        BigInteger, ForeignKey("users.user_id"), primary_key=True, index=True
    )
    hash = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    magnet = Column(String, nullable=False)
    seeders = Column(String)
    leechers = Column(String)
    size = Column(String)
    uploaded_on = Column(String)
    date = Column(TIMESTAMP, server_default=func.current_timestamp())

    user = relationship("User", backref="bookmark")


class Admin(Base):
    __tablename__ = "admins"

    user_id = Column(BigInteger, primary_key=True, index=True)
    date = Column(TIMESTAMP, server_default=func.current_timestamp())


class Referrer(Base):
    __tablename__ = "referrers"

    referrer_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    clicks = Column(Integer, nullable=False, default=0)
    date = Column(TIMESTAMP, server_default=func.current_timestamp())


async def init_models():
    logger.info("Creating metadata for database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
