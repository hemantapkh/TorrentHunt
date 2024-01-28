from database.models import Bookmark
from plugins.functions.database import get_restricted_mode, row2dict
from pyrogram import Client, filters, types
from sqlalchemy import select


@Client.on_inline_query(filters.regex("#bookmarks"))
async def query_search(Client, inline_query):
    user_lang = await Client.misc.user_lang(inline_query)
    restricted_mode = await get_restricted_mode(inline_query.from_user.id)
    results = []

    offset = int(inline_query.offset) if inline_query.offset else 0

    query = (
        select(Bookmark)
        .where(Bookmark.user_id == inline_query.from_user.id)
        .order_by(Bookmark.date.desc())
        .offset(offset * 50)
        .limit(50)
    )
    rows = await Client.DB.execute(query, auto_commit=False)
    rows = [res[0] for res in rows.fetchall()]

    if rows:
        for row in rows:
            res = row2dict(row)
            input_message_content, reply_markup = Client.struct.content_message(
                res,
                user_lang,
                restricted_mode,
                bookmarked=True,
            )
            input_message_content = types.InputTextMessageContent(
                input_message_content,
            )
            results.append(
                types.InlineQueryResultArticle(
                    title=row.title,
                    thumb_url="https://i.ibb.co/vYb4cY4/pngtree-bookmark-icon-vector-illustration-in-flat-style-for-any-purpose-png-image-975552.jpg",
                    description="💾 {}, 🟢 {}, 🔴 {}, 📅 {}".format(
                        row.size,
                        row.seeders,
                        row.leechers,
                        row.uploaded_on,
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
        switch_pm_parameter="inlineQuery",
    )
