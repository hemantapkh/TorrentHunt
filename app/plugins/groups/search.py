from pyrogram import Client, filters, types


@Client.on_message(filters.group & filters.command("search") & filters.CF.init)
async def search(Client, message):
    user_lang = await Client.MISC.user_lang(message)
    await Client.send_message(
        chat_id=message.chat.id,
        text=Client.LG.STR("queryToSearch", user_lang),
        reply_to_message_id=message.id,
        reply_markup=types.ForceReply(selective=True),
    )
