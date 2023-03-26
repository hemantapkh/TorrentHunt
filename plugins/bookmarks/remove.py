from pyrogram import Client, filters


@Client.on_callback_query(filters.regex('removeFromBookmark'))
async def add_bookmark(Client, callback):
    hash = callback.data.split('_')[1]
    user_lang = await Client.MISC.user_lang(callback)

    await Client.DB.query(
        'execute',
        'DELETE FROM bookmarks WHERE user_id=$1 AND hash=$2',
        callback.from_user.id,
        hash,
    )

    await Client.answer_callback_query(
        callback.id,
        text=Client.LG.STR('wishlistRemoved', user_lang),
    )
