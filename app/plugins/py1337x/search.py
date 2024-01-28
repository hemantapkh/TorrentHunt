from pyrogram import Client, filters


@Client.on_message(
    filters.text
    & ~filters.me
    & ~filters.custom.via_me
    & filters.custom.init
    & ~filters.command("settings"),
)
async def search(Client, message):
    user_lang = await Client.misc.user_lang(message)

    msg = await Client.send_message(
        chat_id=message.chat.id,
        text=Client.language.STR("searchingQuery", user_lang).format(message.text),
        reply_to_message_id=message.id,
    )

    response = Client.py1337x.search(message.text)

    text = Client.struct.search_message(response, user_lang)

    await Client.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg.id,
        text=text,
        reply_markup=Client.keyboard.sites(message.text),
    )
