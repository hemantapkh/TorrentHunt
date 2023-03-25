from pyrogram import Client, filters


@Client.on_callback_query(filters.regex('addToBookmark'))
async def add_bookmark(Client, callback):
    hash = callback.data.split('_')[1]
    user_lang = await Client.MISC.user_lang(callback)

    # If item is already on bookmarks
    if await Client.DB.query(
        'fetchval',
        'SELECT EXISTS (SELECT * FROM bookmarks WHERE user_id=$1 AND hash=$2)',
        callback.from_user.id,
        hash,
    ):
        pass

    else:
        info = [
            item for item in callback.message.text.splitlines()
            if item != ''
        ]

        title = info[0][2:]
        size, seeders, leechers, uploaded_on, magnet_link = (
            ''.join(x.split(': ')[1:]).strip() for x in info[1:]
        )

        query = '''
        INSERT INTO bookmarks
        (user_id, hash, title, magnet, seeders, leechers, size, uploaded_on)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        '''

        await Client.DB.query(
            'execute',
            query,
            callback.from_user.id,
            hash,
            title,
            magnet_link,
            seeders,
            leechers,
            size,
            uploaded_on,
        )

    await Client.answer_callback_query(
        callback.id,
        text=Client.LG.STR('wishlistAdded', user_lang),
    )
