from os import environ

from pyrogram import Client, filters


# Show language options
@Client.on_callback_query(filters.regex('language'))
async def language(Client, callback, called=False):
    user_lang = await Client.MISC.user_lang(callback)

    if called:
        await Client.send_message(
            chat_id=callback.chat.id,
            text=Client.LG.STR('chooseLanguage', user_lang),
            reply_markup=Client.KB.language(welcome=True),
        )

    else:
        await Client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=Client.LG.STR('chooseLanguage', user_lang),
            reply_markup=Client.KB.language(),
        )


@Client.on_callback_query(filters.regex('setLanguage'))
async def set_language(Client, callback):
    new_user = callback.data.startswith('setLanguageNew')
    language = callback.data.split('_')[1]

    query = '''
    INSERT INTO settings (language, user_id) VALUES ($1, $2)
    ON CONFLICT (user_id) DO UPDATE SET language = $1;
    '''

    await Client.DB.query(
        'execute',
        query,
        language,
        callback.message.chat.id,
    )

    await Client.delete_messages(
        chat_id=callback.message.chat.id,
        message_ids=callback.message.id,
    )

    # Send welcome message if New user
    if new_user:
        await Client.send_message(
            chat_id=callback.message.chat.id,
            text=Client.LG.STR('greet', language).format(
                callback.from_user.first_name,
            ),
            reply_markup=Client.KB.main(language, callback.message),
        )

        # Send ads on start if configured
        if environ.get('START_ADS'):
            await Client.forward_messages(
                chat_id=callback.message.chat.id,
                from_chat_id=environ.get('START_ADS_CHANNEL'),
                message_ids=int(environ.get('START_ADS_MESSAGE')),
            )

    # Send language selected message if not new user
    else:
        await Client.send_message(
            chat_id=callback.message.chat.id,
            text=Client.LG.STR('languageSelected', language),
            reply_markup=Client.KB.main(language, callback.message),
        )
