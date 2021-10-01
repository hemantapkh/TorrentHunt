from src.objs import *
import requests
from ast import literal_eval
from src.functions.funs import isSubscribed
from src.functions.keyboard import notSubscribedMarkup

# Inline query
@bot.inline_handler(lambda query: len(query.query) >= 1)
def query_text(inline_query):
    userLanguage = dbSql.getSetting(inline_query.from_user.id, 'language')
    if isSubscribed(inline_query, sendMessage=False):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text=language['donateBtn'][userLanguage], url='https://buymeacoffee.com/hemantapkh'))

        site = inline_query.query.split()[0]
        query = ' '.join(inline_query.query.split()[1:])
        
        siteList = {
            '!1337x': '1337x',
            '!pb': 'piratebay',
            '!rb': 'rarbg',
            '!nyaa': 'nyaasi',
            '!yts': 'yts',
            '!ez': 'eztv',
            '!et': 'ettv',
            '!tl': 'torlock',
            '!tg': 'tgx'  
        }
        
        # Default search in 1337x
        site = '!1337x' if site not in siteList else site

        offset = int(inline_query.offset.split(':')[0]) if inline_query.offset else 0
        page = int(inline_query.offset.split(':')[1]) if inline_query.offset else 1

        link = f'http://139.59.211.94:8888/api/{siteList[site]}/{query}/{page}'
        print(offset, page, link)
        results = literal_eval(requests.get(link).text)

        if 'error' not in results:
            try:
                results = sorted(results, key=lambda k: eval(k['Seeders'] if 'Seeders' in k else k['Likes']), reverse=True) 
            except Exception:
                pass

            queryResult = []
            for count, item in enumerate(results[offset:]):
                if count >= 50:
                    break
                queryResult.append(telebot.types.InlineQueryResultArticle(id=count, title=item['Name'], url=item['Url'], hide_url=True, thumb_url='https://transfer.sh/get/YSzMfR/photo_2021-10-01_08-52-48_7013933143080563712.jpg', thumb_width='123', thumb_height='182', description=f"{item['Size'] if 'Size' in item else '-'} size {item['Seeders'] if 'Seeders' in item else '-'} seeders {item['Leechers'] if 'Leechers' in item else '-'} leechers", input_message_content=telebot.types.InputTextMessageContent(queryMessageContent(inline_query.from_user.id, item), parse_mode='HTML'), reply_markup=markup))
            
            nextOffset = offset + 50 if offset+50 < len(results) else 0
            nextPage = page+1 if nextOffset == 0 else page

            bot.answer_inline_query(inline_query.id, queryResult, next_offset=None if (nextPage == page and nextOffset == 15) else f'{nextOffset}:{nextPage}', is_personal=True, cache_time=0)
        
        else:
            bot.answer_inline_query(inline_query.id, [telebot.types.InlineQueryResultArticle(id=0, title=language['noResults'][userLanguage], url='https://t.me/h9youtube', hide_url=True, thumb_url='https://image.freepik.com/free-vector/error-404-found-glitch-effect_8024-4.jpg', input_message_content=telebot.types.InputTextMessageContent(language['noResults'][userLanguage], parse_mode='HTML'))], is_personal=True, cache_time=0)
    
    else:
        reply = telebot.types.InlineQueryResultArticle(id=1, title=language['notSubscribedCallback'][userLanguage], description=language['clickForMoreDetails'][userLanguage], thumb_url='https://raw.githubusercontent.com/hemantapkh/TorrentHunt/main/images/H9Logo.jpg', input_message_content=telebot.types.InputTextMessageContent(language['notSubscribed'][userLanguage], parse_mode='HTML'), reply_markup=notSubscribedMarkup(userLanguage))
        bot.answer_inline_query(inline_query.id, [reply], is_personal=True, cache_time=0)
     
def queryMessageContent(userId, item):
    userLanguage = dbSql.getSetting(userId, 'language')
    
    msg = f"<b>✨ {item['Name']}</b>\n\n{language['size'][userLanguage]}{item['Size'] if 'Size' in item else '-'}\n{language['seeders'][userLanguage]}{item['Seeders'] if 'Seeders' in item else '-'}\n{language['leechers'][userLanguage]}{item['Leechers'] if 'Leechers' in item else '-'}\n{language['uploadedOn'][userLanguage]}{item['DateUploaded'] if 'DateUploaded' in item else '-'}\n\n<b>Magnet Link: </b>{'<code>'+item['Magnet']+'</code>' if 'Magnet' in item else language['errorFetchingLink'][userLanguage].replace('.','')}"
    return msg