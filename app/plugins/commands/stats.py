import sqlalchemy
from database.models import User
from pyrogram import Client, filters


@Client.on_message(filters.command("stats") & filters.custom.admin)
async def stats(Client, message):
    query = sqlalchemy.select(sqlalchemy.func.count(User.user_id))
    total_users = await Client.DB.execute(query)
    total_users = total_users.scalar_one()

    query = sqlalchemy.select(sqlalchemy.func.count()).where(
        sqlalchemy.func.DATE(User.join_date) == sqlalchemy.func.CURRENT_DATE()
    )
    joined_today = await Client.DB.execute(query)
    joined_today = joined_today.scalar_one()

    await Client.send_message(
        message.chat.id,
        text=Client.language.STR("userStats").format(
            total_users,
            joined_today,
        ),
    )
