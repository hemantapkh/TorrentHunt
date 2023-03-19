from pyrogram import Client


@Client.on_message()
async def search(Client, message):
    user_lang = await Client.MISC.user_lang(message)
    response = Client.py1337x.search(message.text)

    text = Client.STRUCT.search_message(response, user_lang)

    await Client.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=Client.KB.sites(message.text),
    )
