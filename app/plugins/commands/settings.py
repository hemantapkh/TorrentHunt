import sqlalchemy
from database.models import Setting
from pyrogram import Client, filters, types


@Client.on_message(filters.CF.cmd("settings") & filters.CF.chat_admin())
async def settings(Client, message):
    user_lang = await Client.MISC.user_lang(message)

    query = sqlalchemy.select(Setting.restricted_mode).where(
        Setting.user_id == message.chat.id
    )
    restriction_mode = await Client.DB.execute(query)
    restriction_mode = restriction_mode.scalar_one()

    if restriction_mode:
        res_button_text = Client.LG.BTN("turnOffRestrictedMode", user_lang)

    else:
        res_button_text = Client.LG.BTN("turnOnRestrictedMode", user_lang)

    buttons = [
        [
            types.InlineKeyboardButton(
                text=Client.LG.BTN("languageSetting", user_lang),
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
        text=Client.LG.STR("settings", user_lang).format(
            Client.LG.CMD("settings", user_lang),
        ),
        reply_markup=types.InlineKeyboardMarkup(buttons),
        reply_to_message_id=message.id,
    )
