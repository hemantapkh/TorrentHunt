from pyrogram import Client, filters


@Client.on_message(~filters.me & ~filters.CF.via_me & filters.CF.init)
async def search(Client, message):
    user_lang = await Client.MISC.user_lang(message)

    msg = await Client.send_message(
        chat_id=message.chat.id,
        text=Client.LG.STR('searchingQuery', user_lang).format(message.text),
        reply_to_message_id=message.id,
    )

    response = Client.py1337x.search(message.text)

    text = Client.STRUCT.search_message(response, user_lang)

    await Client.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg.id,
        text=text,
        reply_markup=Client.KB.sites(message.text),
    )
