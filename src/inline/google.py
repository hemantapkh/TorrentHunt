from src.objs import *
from src.functions.funs import getSuggestions

async def googleSuggestions(inline_query, userLanguage):
    query = ' '.join(inline_query.query.split()[1:])

    if query:
        results = getSuggestions(query)
        
        if results:
            queryResult = []
            for count, item in enumerate(results):
                queryResult.append(pyrogram.types.InlineQueryResultArticle(id=count, title=item, input_message_content=pyrogram.types.InputTextMessageContent(f'⦿ {item}')))

            await bot.answer_inline_query(inline_query.id, queryResult, is_personal=True, switch_pm_text='Google suggestions', switch_pm_parameter='inlineQuery')
            
        else:
            await bot.answer_inline_query(inline_query.id, [pyrogram.types.InlineQueryResultArticle(id=0, title=language['noResults'][userLanguage], url='https://t.me/h9youtube', hide_url=True, thumb_url='https://raw.githubusercontent.com/hemantapkh/TorrentHunt/main/images/notfound.jpg', input_message_content=pyrogram.types.InputTextMessageContent(language['noResults'][userLanguage], parse_mode='HTML'))], is_personal=True)

    else:
        await bot.answer_inline_query(inline_query.id, results=[], cache_time=0, is_personal=True, switch_pm_text=f'Enter the query to search in Google', switch_pm_parameter='inlineQuery')