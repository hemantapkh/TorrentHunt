from pyrogram import Client, filters


# Turn on or off restricted mode
@Client.on_callback_query(filters.regex('restriction'))
async def restriction(Client, callback):
    restriction = callback.data.split('_')[1]
    user_lang = await Client.MISC.user_lang(callback)

    await Client.DB.query(
        'execute',
        'UPDATE settings SET restricted_mode = $1 WHERE user_id = $2',
        eval(restriction),
        callback.message.chat.id,
    )

    await Client.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=Client.LG.STR(f'restrictedMode{restriction}', user_lang),
    )
