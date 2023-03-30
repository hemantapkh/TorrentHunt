from loguru import logger
from pyrogram import Client, filters, types


@Client.on_inline_query(filters.regex('!'))
async def query_search(Client, inline_query):
    user_lang = await Client.MISC.user_lang(inline_query)
    query_list = inline_query.query.split()
    results = []

    # If keyword is not empty
    if len(query_list) > 1:
        keyword = ' '.join(query_list[1:])
        site = Client.MISC.code_to_site(query_list[0])
        if not inline_query.offset:
            results = inline_ads()
            await Client.answer_inline_query(
                inline_query.id,
                results=results,
                cache_time=0,
                is_personal=True,
                switch_pm_text=Client.LG.STR(
                    'searchingInline', user_lang,
                ).format(keyword),
                next_offset=str(1),
                switch_pm_parameter='inlineQuery',
            )
            return

        page = int(inline_query.offset) if inline_query.offset else 1
        logger.info(f'Inline searching {keyword} on {site} on page {page}')

        response = await Client.TH.request(
            route='/search',
            params={
                'query': keyword,
                'site': site,
                'page': str(page),
            },
        )

        if response.get('items'):
            pm_text = Client.LG.STR('resultsFor', user_lang).format(
                keyword,
            )

            for res in response.get('items'):
                results.append(
                    types.InlineQueryResultArticle(
                        title=res.get('name'),
                        thumb_url=res.get('poster') or
                        f'https://raw.githubusercontent.com/hemantapkh/torrenthunt/main/images/{site}.jpg',
                        description='💾 {}, 🟢 {}, 🔴 {}, 📅 {}'.format(
                            res.get('size'),
                            res.get('seeders'),
                            res.get('leechers'),
                            res.get('uploadDate'),
                        ),
                        input_message_content=types.InputTextMessageContent(
                            message_text=Client.STRUCT.content_message(
                                res, 'english',
                            )[0],
                        ),
                        reply_markup=Client.KB.torrent_info(
                            user_lang,
                            res.get('infoHash'),
                        ),
                    ),
                )

            next_offset = page + 1

        # No suggestions found
        else:
            pm_text = response.get('error')
            next_offset = None

    # If keyword is empty
    else:
        pm_text = Client.LG.STR('keywordToSearch', user_lang)
        next_offset = None

    await Client.answer_inline_query(
        inline_query.id,
        results=results,
        cache_time=10,
        switch_pm_text=pm_text,
        next_offset=str(next_offset) if next_offset else None,
        switch_pm_parameter='inlineQuery',
    )


# Inline ads
def inline_ads():
    return [
        types.InlineQueryResultArticle(
            title='[ADS] Media Downloader Bot',
            description='The ultimate media downloader bot on Telegram.\n👆 SCROLL UP TO SEE THE RESULTS👆',
            thumb_url='https://i.ibb.co/dQZNmB2/videodownloader-512-7395df698c5e.png',
            input_message_content=types.InputTextMessageContent(
                message_text=ads_text,
            ),
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(
                            text='👉 Click To Use 👈',
                            url='https://t.me/vmateBot?start=torrentHuntInlineAds',
                        ),
                    ],
                ],
            ),
        ),
    ]


ads_text = '''
<b>vmate - The media downloader Bot</b>

Introducing VMate - the ultimate media downloader bot that makes downloading videos from your favorite social media platforms a breeze!
With VMate, you can easily download media from Facebook, YouTube, TikTok, and many others in just a few second.
'''
