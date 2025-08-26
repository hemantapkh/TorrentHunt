from pyrogram import Client, filters


@Client.on_message(
    filters.text
    & ~filters.me
    & ~filters.custom.via_me
    & filters.custom.init
    & ~filters.command("settings"),
)
async def search(Client: Client, message):
    user_lang = await Client.misc.user_lang(message)

    await Client.send_message(
        chat_id=message.chat.id,
        text=Client.language.STR("selectCategory", user_lang),
        reply_to_message_id=message.id,
        reply_markup=Client.keyboard.categories(message.text),
    )


@Client.on_callback_query(filters.regex(r"cat_"))
async def search_category(Client, callback_query):
    _, category, query = callback_query.data.split("_", 2)
    user_lang = await Client.misc.user_lang(callback_query)

    await Client.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.id,
        text=Client.language.STR("searchingQuery", user_lang).format(query),
    )

    response = await Client.py1337x.search(query, category=category)

    text = Client.struct.search_message(response.to_dict(), user_lang)

    await Client.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.id,
        text=text,
        reply_markup=Client.keyboard.sites(query),
    )
