from os import environ

from database.models import Setting
from pyrogram import Client, filters


# Show language options
@Client.on_callback_query(filters.regex("language") & filters.custom.chat_admin())
async def language(Client, callback, called=False):
    user_lang = await Client.misc.user_lang(callback)

    if called:
        await Client.send_message(
            chat_id=callback.chat.id,
            text=Client.language.STR("chooseLanguage", user_lang),
            reply_markup=Client.keyboard.language(welcome=True),
            reply_to_message_id=callback.id,
        )

    else:
        await Client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=Client.language.STR("chooseLanguage", user_lang),
            reply_markup=Client.keyboard.language(),
        )


@Client.on_callback_query(filters.regex("setLanguage") & filters.custom.chat_admin())
async def set_language(Client, callback):
    new_user = callback.data.startswith("setLanguageNew")
    language = callback.data.split("_")[1]

    setting = Setting(user_id=callback.message.chat.id, language=language)
    await Client.DB.merge(setting)

    await Client.delete_messages(
        chat_id=callback.message.chat.id,
        message_ids=callback.message.id,
    )

    # Send welcome message if New user
    if new_user:
        await Client.send_message(
            chat_id=callback.message.chat.id,
            text=Client.language.STR("greet", language).format(
                callback.from_user.first_name,
            ),
            reply_markup=Client.keyboard.main(language, callback.message),
        )

        # Send ads on start if configured
        if environ.get("START_ADS"):
            await Client.forward_messages(
                chat_id=callback.message.chat.id,
                from_chat_id=environ.get("START_ADS_CHANNEL"),
                message_ids=int(environ.get("START_ADS_MESSAGE")),
            )

    # Send language selected message if not new user
    else:
        await Client.send_message(
            chat_id=callback.message.chat.id,
            text=Client.language.STR("languageSelected", language),
            reply_markup=Client.keyboard.main(language, callback.message),
        )
