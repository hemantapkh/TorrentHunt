from pyrogram import Client, filters, types


@Client.on_message(filters.CF.cmd('settings'))
async def settings(Client, message):
    user_lang = await Client.MISC.user_lang(message)

    restriction_mode = await Client.DB.query(
        'fetchval',
        'SELECT restricted_mode FROM settings WHERE user_id=$1',
        message.chat.id,
    )

    if restriction_mode:
        res_button_text = Client.LG.BTN('turnOffRestrictedMode', user_lang)

    else:
        res_button_text = Client.LG.BTN('turnOnRestrictedMode', user_lang)

    buttons = [
        [
            types.InlineKeyboardButton(
                text=Client.LG.BTN('languageSetting', user_lang),
                callback_data='language',
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=res_button_text,
                callback_data=f'restriction_{restriction_mode}',
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
