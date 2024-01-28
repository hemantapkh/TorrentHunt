from pyrogram import Client, filters, types


@Client.on_message(filters.private & filters.custom.cmd("bookmarks"))
async def bookmarks(Client, message):
    user_lang = await Client.misc.user_lang(message)

    await Client.send_message(
        chat_id=message.chat.id,
        text=Client.language.STR("bookmarks", user_lang),
        reply_to_message_id=message.id,
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text=Client.language.CMD("bookmarks", user_lang),
                        switch_inline_query_current_chat="#bookmarks",
                    ),
                ],
            ]
        ),
    )
