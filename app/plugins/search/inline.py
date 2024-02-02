from os import environ

from loguru import logger
from plugins.functions.database import get_restricted_mode
from pyrogram import Client, filters, types


@Client.on_inline_query(filters.regex("!"))
async def query_search(Client, inline_query):
    user_lang = await Client.misc.user_lang(inline_query)
    restricted_mode = await get_restricted_mode(inline_query.from_user.id)
    query_list = inline_query.query.split()
    results = []

    # If keyword is not empty
    if len(query_list) > 1:
        keyword = " ".join(query_list[1:])
        site = Client.misc.code_to_site(query_list[0])

        page = int(inline_query.offset) if inline_query.offset else 1
        logger.info(f"Inline searching {keyword} on {site} on page {page}")

        response = await Client.torrent_hunt_api.request(
            route="/api/search",
            params={
                "query": keyword,
                "site": site,
                "page": str(page),
            },
        )

        if response.get("items"):
            pm_text = Client.language.STR("resultsFor", user_lang).format(
                keyword,
            )

            for res in response.get("items"):
                text, markup = Client.struct.content_message(
                    res,
                    language=user_lang,
                    restricted_mode=restricted_mode,
                )
                results.append(
                    types.InlineQueryResultArticle(
                        title=res.get("name"),
                        thumb_url=res.get("thumbnail")
                        or f"https://raw.githubusercontent.com/hemantapkh/torrenthunt/main/images/{site}.jpg",
                        description="💾 {}, 🟢 {}, 🔴 {}, 📅 {}".format(
                            res.get("size"),
                            res.get("seeders"),
                            res.get("leechers"),
                            res.get("uploadDate"),
                        ),
                        input_message_content=types.InputTextMessageContent(
                            message_text=text,
                        ),
                        reply_markup=markup,
                    ),
                )

            next_offset = page + 1

        # No suggestions found
        else:
            pm_text = response.get("error")
            next_offset = None

    # If keyword is empty
    else:
        pm_text = Client.language.STR("keywordToSearch", user_lang)
        next_offset = None

    await Client.answer_inline_query(
        inline_query.id,
        results=results,
        cache_time=10,
        switch_pm_text=pm_text,
        next_offset=str(next_offset) if next_offset else None,
        switch_pm_parameter="inlineQuery",
    )
