from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()

engine = create_async_engine("sqlite+aiosqlite:///test.db")
Session = sessionmaker(bind=engine, class_=AsyncSession)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    user_type = Column(String, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    referrer = Column(String)
    join_date = Column(TIMESTAMP, server_default=func.current_timestamp())
    last_active = Column(TIMESTAMP, server_default=func.current_timestamp())

    setting = relationship("Setting", uselist=False, back_populates="User")


class Setting(Base):
    __tablename__ = "settings"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    language = Column(String, default="english")
    restricted_mode = Column(Boolean, default=True)

    user = relationship("User", back_populates="Setting", foreign_keys=[user_id])


class Bookmark(Base):
    __tablename__ = "bookmarks"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    hash = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    magnet = Column(String, nullable=False)
    seeders = Column(String)
    leechers = Column(String)
    size = Column(String)
    uploaded_on = Column(String)
    date = Column(TIMESTAMP, server_default=func.current_timestamp())

    user = relationship("User", backref="Bookmark")


class Admin(Base):
    __tablename__ = "admins"

    user_id = Column(Integer, primary_key=True)
    date = Column(TIMESTAMP, server_default=func.current_timestamp())


class Referrer(Base):
    __tablename__ = "referrers"

    referrer_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    clicks = Column(Integer, nullable=False, default=0)
    date = Column(TIMESTAMP, server_default=func.current_timestamp())


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
