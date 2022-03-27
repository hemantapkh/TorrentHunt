import re
import requests
import validators
from src.objs import *
from ast import literal_eval
from src.functions.funs import isSubscribed
from src.inline.google import googleSuggestions
from src.functions.keyboard import notSubscribedMarkup

siteList = {
    '!1337x': '1337x',
    '!pb': 'piratebay',
    #'!rb': 'rarbg',
    '!nyaa': 'nyaasi',
    '!yts': 'yts',
    #'!ez': 'eztv',
    #'!et': 'ettv',
    '!tl': 'torlock',
    '!tg': 'tgx',
    '!zoo': 'zoogle',
    '!ka': 'kickass',
    '!bs': 'bitsearch',
    '!gl': 'glodls',
    '!mdl': 'magnetdl',
    '!lt': 'limetorrent',
    '!tf': 'torrentfunk',
    '!tp': 'torrentproject',
    '!gl': 'glodls',
    '!lg': 'libgen',
}

siteName = {
    "1337x" : "1337x",
    "piratebay" : "The Pirate Bay",
    "nyaasi": "Nyaa.si",
    "yts": "YTS",
    "eztv": "Ez Tv",
    "ettv": "Et Tv",
    "torlock": "Torlock",
    "rarbg": "RARBG",
    "tgx": "Torrent Galaxy",
    'zooqle': 'Zooqle',
    'kickass': 'Kick Ass',
    'bitsearch': 'Bit Search',
    'glodls': 'Glodls',
    'magnetdl': 'magnetDL',
    'limetorrent': 'Lime Torrents',
    'torrentfunk': 'Torrent Funk',
    'torrentproject': 'Torrent Project',
    'libgen': 'Libgen'
}

#: Inline query
@bot.inline_handler(lambda query: len(query.query) >= 0)
def inlineSearch(inline_query):
    if dbSql.isRegistered(inline_query.from_user.id):
        userLanguage = dbSql.getSetting(inline_query.from_user.id, 'language')
        
        if isSubscribed(inline_query, sendMessage=False):
            site = dbSql.getSetting(inline_query.from_user.id, 'defaultSite')

            if len(inline_query.query) == 0:
                bot.answer_inline_query(inline_query.id, results=[], cache_time=0, is_personal=True, switch_pm_text=f'Enter the query to search in {siteName[site]}', switch_pm_parameter='inlineQuery')
            
            elif inline_query.query.split()[0] == '!google':
                googleSuggestions(inline_query, userLanguage)
            
            else:
                if inline_query.query.split()[0] in siteList:
                    site = siteList[inline_query.query.split()[0]]
                    query = ' '.join(inline_query.query.split()[1:])
                
                else:
                    query = inline_query.query
                
                if query:
                    offset = int(inline_query.offset.split(':')[0]) if inline_query.offset else 0
                    page = int(inline_query.offset.split(':')[1]) if inline_query.offset else 1

                    link = f"{config['apiLink']}/api/v1/search?site={site}&query={query}&limit=20&page={page}"
                    results = requests.get(link).json()
                    
                    if 'error' not in results:
                        try:
                            results = sorted(results, key=lambda k: eval(k['Seeders'] if 'Seeders' in k else k['Likes']), reverse=True) 
                        
                        except Exception:
                            pass

                        queryResult = []
                        for count, item in enumerate(results['data'][offset:]):
                            if count >= 50:
                                break

                            thumbnail = item['poster'] if 'poster' in item and item['poster'] not in ['','https://img.picturegalaxy.org/static/noposter.jpg'] else f'https://raw.githubusercontent.com/hemantapkh/TorrentHunt/main/images/{site}.jpg'
                            
                            if botId == '1700458114' and 'Magnet' in item:
                                markup = telebot.types.InlineKeyboardMarkup()
                                magnetKey = 'Db_'+dbSql.setMagnet(item['Magnet'])
                                markup.add(telebot.types.InlineKeyboardButton(text=language['addToSeedr'][userLanguage], url=f't.me/torrentseedrbot?start=addTorrent{magnetKey}'))
                            
                            else:
                                markup = telebot.types.InlineKeyboardMarkup()
                                markup.add(telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='t.me/h9youtube'), telebot.types.InlineKeyboardButton(text=language['joinDiscussionBtn'][userLanguage], url='t.me/h9discussion'))
                            
                            queryResult.append(telebot.types.InlineQueryResultArticle(id=count, title=item['name'], url=item['url'] if validators.url(item['url']) else None, hide_url=True, thumb_url=thumbnail, thumb_width='123', thumb_height='182', description=f"{language['size'][userLanguage] + item['size'] if 'size' in item else ''} {', '+language['seeders'][userLanguage] + item['seeders'] if 'seeders' in item and item['seeders'] != '-' else ''} {', '+language['leechers'][userLanguage] + item['leechers'] if 'leechers' in item else ''}", input_message_content=telebot.types.InputTextMessageContent(queryMessageContent(inline_query.from_user.id, item, site), parse_mode='HTML'), reply_markup=markup))
                        
                        nextOffset = offset + 50 if offset+50 < len(results) else 0
                        nextPage = page+1 if nextOffset == 0 else page

                        bot.answer_inline_query(inline_query.id, queryResult, next_offset=None if (nextPage == page and nextOffset == 15) else f'{nextOffset}:{nextPage}', is_personal=True, cache_time=0, switch_pm_text=f'"{query}" on {siteName[site]}', switch_pm_parameter='inlineQuery')

                    else:
                        if page == 1:
                            bot.answer_inline_query(inline_query.id, [telebot.types.InlineQueryResultArticle(id=0, title=language['noResults'][userLanguage], url='https://t.me/h9youtube', hide_url=True, thumb_url='https://raw.githubusercontent.com/hemantapkh/TorrentHunt/main/images/notfound.jpg', description=results['error'], input_message_content=telebot.types.InputTextMessageContent(language['noResults'][userLanguage], parse_mode='HTML'))], is_personal=True)

                else:
                    bot.answer_inline_query(inline_query.id, results=[], cache_time=0, is_personal=True, switch_pm_text=f'Enter the query to search in {siteName[site]}', switch_pm_parameter='inlineQuery')
        else:
            reply = telebot.types.InlineQueryResultArticle(id=1, title=language['notSubscribedCallback'][userLanguage], description=language['clickForMoreDetails'][userLanguage], thumb_url='https://raw.githubusercontent.com/hemantapkh/TorrentHunt/main/images/H9Logo.jpg', input_message_content=telebot.types.InputTextMessageContent(language['notSubscribed'][userLanguage], parse_mode='HTML'), reply_markup=notSubscribedMarkup(userLanguage))
            bot.answer_inline_query(inline_query.id, [reply], is_personal=True, cache_time=0)

    else:
        bot.answer_inline_query(inline_query.id, results=[], cache_time=0, is_personal=True, switch_pm_text='✨ Click here to setup your account first', switch_pm_parameter='inlineQuery')

#: Query message content     
def queryMessageContent(userId, item, torrentSite):
    userLanguage = dbSql.getSetting(userId, 'language')
    
    msg  = f"<b>✨ {item['name']}</b>\n\n"

    msg += f"{language['size'][userLanguage]}{item['size'] if 'size' in item else '-'}\n"
    msg += f"{language['seeders'][userLanguage]}{item['seeders'] if 'seeders' in item else '-'}\n"
    msg += f"{language['leechers'][userLanguage]}{item['leechers'] if 'leechers' in item else '-'}\n"
    msg += f"{language['uploadedOn'][userLanguage]}{item['date'] if 'date' in item else '-'}\n\n"

    msg += f"<b>Magnet Link: </b>{'<code>'+item['magnet']+'</code>' if 'magnet' in item else language['errorFetchingLink'][userLanguage].replace('.','')}\n\n🔥<b>via @TorrentHuntBot</b>"

    return msg