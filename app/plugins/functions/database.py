from database.models import Setting
from pyrogram import Client
from sqlalchemy import select


async def get_restricted_mode(user_id: int):
    query = select(Setting.restricted_mode).where(Setting.user_id == user_id)
    restricted_mode = await Client.DB.execute(query)

    return restricted_mode.scalar()


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d
