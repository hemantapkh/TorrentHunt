from pyrogram import Client, filters


# Show language options
@Client.on_callback_query(filters.regex('language'))
async def language(Client, callback):
    await Client.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=callback.message.text,
        reply_markup=Client.KB.language(),
    )

# Set language


@Client.on_callback_query(filters.regex('setLanguage'))
async def set_language(Client, callback):
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

    await Client.send_message(
        chat_id=callback.message.chat.id,
        text=Client.LG.STR('languageSelected', language),
        reply_markup=Client.KB.main(language),
    )
