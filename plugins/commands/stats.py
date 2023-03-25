from pyrogram import Client, filters


@Client.on_message(filters.command('stats') & filters.CF.admin)
async def stats(Client, message):
    total_users = await Client.DB.query(
        'fetchval',
        'SELECT COUNT(*) FROM USERS;',
    )

    joined_today = await Client.DB.query(
        'fetchval',
        'SELECT COUNT(*) FROM USERS WHERE DATE(join_date)=CURRENT_DATE',
    )

    await Client.send_message(
        message.chat.id,
        text=Client.LG.STR('userStats').format(
            total_users,
            joined_today,
        ),
    )
