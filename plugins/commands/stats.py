from pyrogram import Client, filters


@Client.on_message(filters.command('stats') & filters.CF.admin)
async def stats(Client, message):
    totalUsers = await Client.DB.query(
        'fetchval',
        'SELECT COUNT(*) FROM USERS;',
    )

    joinedToday = await Client.DB.query(
        'fetchval',
        'SELECT COUNT(*) FROM USERS WHERE DATE(join_date)=CURRENT_DATE',
    )

    await Client.send_message(
        message.chat.id,
        text=Client.LG.STR('userStats').format(
            totalUsers,
            joinedToday,
        ),
    )
