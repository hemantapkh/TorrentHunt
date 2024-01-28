from plugins.functions.database import get_restricted_mode
from pyrogram import Client, filters


@Client.on_message(filters.regex("getLink"))
async def results(Client, message):
    user_lang = await Client.misc.user_lang(message)
    restricted_mode = await get_restricted_mode(message.chat.id)
    torrent_id = message.text.split("_")[1].split("@")[0]

    msg = await Client.send_message(
        chat_id=message.chat.id,
        text=Client.language.STR("fetchingTorrentInfo", user_lang),
        reply_to_message_id=message.id,
    )

    response = Client.py1337x.info(torrentId=torrent_id)

    text, markup = Client.struct.content_message(
        response,
        language=user_lang,
        restricted_mode=restricted_mode,
    )

    await Client.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg.id,
        text=text,
        reply_markup=markup,
    )
