from database.models import Bookmark
from pyrogram import Client, filters
from sqlalchemy import delete


@Client.on_callback_query(filters.regex("removeFromBookmark"))
async def add_bookmark(Client, callback):
    hash = callback.data.split("_")[1]
    user_lang = await Client.misc.user_lang(callback)

    query = (
        delete(Bookmark)
        .where(Bookmark.user_id == callback.from_user.id)
        .where(Bookmark.hash == hash)
    )
    await Client.DB.execute(query)

    await Client.answer_callback_query(
        callback.id,
        text=Client.language.STR("wishlistRemoved", user_lang),
    )
