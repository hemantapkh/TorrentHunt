from database.models import Setting
from pyrogram import Client, filters
from sqlalchemy import update


# Turn on or off restricted mode
@Client.on_callback_query(filters.regex("restriction") & filters.custom.chat_admin())
async def restriction(Client, callback):
    restriction = callback.data.split("_")[1]
    user_lang = await Client.misc.user_lang(callback)

    query = (
        update(Setting)
        .where(Setting.user_id == callback.message.chat.id)
        .values(
            restricted_mode=eval(restriction),
        )
    )
    await Client.DB.execute(query)

    await Client.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=Client.language.STR(f"restrictedMode{restriction}", user_lang),
    )
