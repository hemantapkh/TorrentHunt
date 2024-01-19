from pyrogram import Client, filters, types


@Client.on_inline_query(filters.regex('#bookmarks'))
async def query_search(Client, inline_query):
    user_lang = await Client.MISC.user_lang(inline_query)
    restricted_mode = await Client.DB.query(
        'fetchval',
        'SELECT restricted_mode FROM settings WHERE user_id = $1',
        inline_query.from_user.id,
    )
    results = []

    offset = int(inline_query.offset) if inline_query.offset else 0

    response = await Client.DB.query(
        'fetch',
        'SELECT * FROM bookmarks WHERE user_id=$1 ORDER BY date DESC LIMIT 50 OFFSET $2',
        inline_query.from_user.id,
        offset * 50,
    )

    if response:
        for res in response:
            input_message_content, reply_markup = Client.STRUCT.content_message(
                res, user_lang, restricted_mode, bookmarked=True,
            )
            input_message_content = types.InputTextMessageContent(
                input_message_content,
            )
            results.append(
                types.InlineQueryResultArticle(
                    title=res.get('title'),
                    thumb_url='https://i.ibb.co/vYb4cY4/pngtree-bookmark-icon-vector-illustration-in-flat-style-for-any-purpose-png-image-975552.jpg',
                    description='💾 {}, 🟢 {}, 🔴 {}, 📅 {}'.format(
                        res.get('size'),
                        res.get('seeders'),
                        res.get('leechers'),
                        res.get('uploaded_on'),
                    ),
                    input_message_content=input_message_content,
                    reply_markup=reply_markup,
                ),
            )

        next_offset = offset + 1

    # No result found
    else:
        next_offset = None

    await Client.answer_inline_query(
        inline_query.id,
        results=results,
        cache_time=10,
        next_offset=str(next_offset) if next_offset else None,
        switch_pm_parameter='inlineQuery',
    )
