from pyrogram import Client, filters

from plugins.settings.language import language


@Client.on_message(filters.command('start') & filters.private)
async def message(Client, message):
    params = message.command[-1] if message.command[-1] != 'start' else None

    referrer = None
    if params:
        try:
            # If params is a registered user
            user_id = int(params)
            referrer = user_id if await Client.DB.query(
                'fetchval',
                'SELECT EXISTS (SELECT * FROM users WHERE user_id=$1)',
                user_id,
            ) else None

        except ValueError:
            # If params is a tracking ID
            referrer = params if await Client.DB.query(
                'execute',
                'UPDATE REFERRERS SET clicks=clicks+1 WHERE referrer_id=$1',
                params,
            ) == 'UPDATE 1' else None

    new_user = await Client.DB.set_user(message, referrer)

    if new_user:
        await language(Client, message, called=True)

    else:
        # Send welcome message
        user_lang = await Client.MISC.user_lang(message)
        await Client.send_message(
            chat_id=message.chat.id,
            text=Client.LG.STR('greet', user_lang).format(
                message.from_user.first_name,
            ),
            reply_markup=Client.KB.main(user_lang),
        )
