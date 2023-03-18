from pyrogram import Client, filters, types


@Client.on_message(filters.CF.cmd('settings'))
async def settings(Client, message):
    user_lang = await Client.MISC.user_lang(message)

    buttons = [
        [
            types.InlineKeyboardButton(
                text=Client.LG.BTN('languageSetting', user_lang),
                callback_data='language',
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=Client.LG.BTN('turnOnRestrictedMode', user_lang),
                callback_data='restricted_mode',
            ),
        ],
    ]

    await Client.send_message(
        chat_id=message.chat.id,
        text=Client.LG.STR('settings', user_lang).format(
            Client.LG.CMD('settings', user_lang),
        ),
        reply_markup=types.InlineKeyboardMarkup(buttons),
    )
