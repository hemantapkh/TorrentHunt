from database.models import Setting
from pyrogram import Client, filters
from sqlalchemy import select


@Client.on_message(filters.regex("getLink"))
async def results(Client, message):
    user_lang = await Client.MISC.user_lang(message)

    query = select(Setting.restricted_mode).where(Setting.user_id == message.chat.id)
    restricted_mode = await Client.DB.execute(query)
    restricted_mode = restricted_mode.scalar()

    torrent_id = message.text.split("_")[1].split("@")[0]

    msg = await Client.send_message(
        chat_id=message.chat.id,
        text=Client.LG.STR("fetchingTorrentInfo", user_lang),
        reply_to_message_id=message.id,
    )

    response = Client.py1337x.info(torrentId=torrent_id)

    text, markup = Client.STRUCT.content_message(
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
