from plugins.functions.database import get_restricted_mode
from pyrogram import Client, filters, types


@Client.on_message(filters.custom.cmd("settings") & filters.custom.chat_admin())
async def settings(Client, message):
    user_lang = await Client.misc.user_lang(message)

    restriction_mode = await get_restricted_mode(message.chat.id)

    if restriction_mode:
        res_button_text = Client.language.BTN("turnOffRestrictedMode", user_lang)

    else:
        res_button_text = Client.language.BTN("turnOnRestrictedMode", user_lang)

    buttons = [
        [
            types.InlineKeyboardButton(
                text=Client.language.BTN("languageSetting", user_lang),
                callback_data="language",
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=res_button_text,
                callback_data=f"restriction_{not restriction_mode}",
            ),
        ],
    ]

    await Client.send_message(
        chat_id=message.chat.id,
        text=Client.language.STR("settings", user_lang).format(
            Client.language.CMD("settings", user_lang),
        ),
        reply_markup=types.InlineKeyboardMarkup(buttons),
        reply_to_message_id=message.id,
    )
