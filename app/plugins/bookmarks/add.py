from database.models import Bookmark
from pyrogram import Client, filters
from sqlalchemy import and_, exists, insert, select


@Client.on_callback_query(filters.regex("addToBookmark"))
async def add_bookmark(Client, callback):
    hash = callback.data.split("_")[1]
    user_lang = await Client.misc.user_lang(callback)

    # If item is already on bookmarks
    query = select(exists(Bookmark)).where(
        and_(
            Bookmark.user_id == callback.from_user.id,
            Bookmark.hash == hash,
        )
    )
    bookmark_exists = await Client.DB.execute(query)

    if bookmark_exists.scalar():
        pass

    else:
        info = [item for item in callback.message.text.splitlines() if item != ""]

        title = info[0][2:]
        size, seeders, leechers, uploaded_on, magnet_link = (
            "".join(x.split(": ")[1:]).strip() for x in info[1:]
        )

        query = insert(Bookmark).values(
            user_id=callback.from_user.id,
            hash=hash,
            title=title,
            magnet=magnet_link,
            seeders=seeders,
            leechers=leechers,
            size=size,
            uploaded_on=uploaded_on,
        )

        await Client.DB.execute(query)

    await Client.answer_callback_query(
        callback.id,
        text=Client.language.STR("wishlistAdded", user_lang),
    )
