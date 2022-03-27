from time import time
from src.objs import *

#: Parse the torrent result
def result(response, userLanguage, resultType, torrentType, page, category=None, week=None, query=None, originalQuery=None):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.one_time_keyboard=True
    markup.row_width = 5
    
    msg = ''
    if response['items']:
        for count, item in enumerate(response['items']):
            #! Show only 20 items per page
            if count >= 20:
                break

            newMsg = f"<b>{((page-1)*20)+count+1}. {item['name'][:100]}</b>\n\n"
            newMsg += f"💾 {item['size']}, 🟢 {item['seeders']}, 🔴 {item['leechers']}\n\n"

            newMsg += f"{language['link'][userLanguage]} /{'getLink' if resultType=='link' else 'getInfo'}_{item['torrentId']}\n\n"

            msg = newMsg + msg

        pageCount = response['pageCount']

        #! Trending, popular and top torrents has more than 20 items in the same page
        if torrentType in ['trending', 'popular', 'top']:
            if response['itemCount'] > 20:
                buttons =  []
                for i in range(1, -(-response['itemCount'] // 20)+1):
                    buttons.append(telebot.types.InlineKeyboardButton('🔘' if i == page else i, callback_data=f"cb_nextPage{time()}:{i}:{torrentType}-{category}-{week}:{query or ''}"))

                markup.add(*buttons)

        #! For other category, create page according to pageCount
        elif pageCount > 1:
            #! FirstPage is the firstPage in a page list. Eg: FirstPage of (1 to 10) is 1, (11 to 20) is 11.
            firstPage = 1
            for i in range(-(-page // 10)-1):
                firstPage += 10
            
            buttons =  []
            for i in range(firstPage, pageCount+1):
                #! Show 10 buttons at once
                if len(buttons) >= 10:
                    break
                
                cb = f"q{str(time())[-3:]}:{i}:{query}" if query else f"cb_nextPage{time()}:{i}:{torrentType}-{category}-{week}:{query or ''}"
                buttons.append(telebot.types.InlineKeyboardButton('🔘' if i == page else i, callback_data=cb))
            
            markup.add(*buttons)
            if pageCount > 10:
                if page <= 10:
                    cb = f"q{str(time())[-3:]}:{firstPage+10}:{query}" if query else f"cb_nextPage{time()}:{firstPage+10}:{torrentType}-{category}-{week}"
                    markup.add(telebot.types.InlineKeyboardButton(language['nextBtn'][userLanguage], callback_data=cb))

                elif 10 < page <= (pageCount - 10):
                    cb1 = f"q{str(time())[-3:]}:{firstPage-10}:{query}" if query else f"cb_nextPage{time()}:{firstPage-10}:{torrentType}-{category}-{week}"
                    cb2 = f"q{str(time())[-3:]}:{firstPage+10}:{query}" if query else f"cb_nextPage{time()}:{firstPage+10}:{torrentType}-{category}-{week}"

                    markup.add(telebot.types.InlineKeyboardButton(language['previousBtn'][userLanguage], callback_data=cb1), telebot.types.InlineKeyboardButton(language['nextBtn'][userLanguage], callback_data=cb2))
                
                else:
                    cb = f"q{str(time())[-3:]}:{firstPage-10}:{query}" if query else f"cb_nextPage{time()}:{firstPage-10}:{torrentType}-{category}-{week}"
                    markup.add(telebot.types.InlineKeyboardButton(language['previousBtn'][userLanguage], callback_data=cb))                      
                        
    if query:
        if not msg:
            query = originalQuery
        markup.add(telebot.types.InlineKeyboardButton(text='1337x', switch_inline_query_current_chat=f"!1337x {query}"), telebot.types.InlineKeyboardButton(text='Pirate', switch_inline_query_current_chat=f"!pb {query}"),) #telebot.types.InlineKeyboardButton(text='Rarbg', switch_inline_query_current_chat=f"!rb {query}"))
        markup.add(telebot.types.InlineKeyboardButton(text='Nyaa', switch_inline_query_current_chat=f"!nyaa {query}"), telebot.types.InlineKeyboardButton(text='Glodis', switch_inline_query_current_chat=f"!gl {query}"), telebot.types.InlineKeyboardButton(text='Tor Lock', switch_inline_query_current_chat=f"!tl {query}"))
        markup.add(telebot.types.InlineKeyboardButton(text='YTS', switch_inline_query_current_chat=f"!yts {query}"), telebot.types.InlineKeyboardButton(text='📚 Libgen', switch_inline_query_current_chat=f"!lg {query}") , telebot.types.InlineKeyboardButton(text='Galaxy', switch_inline_query_current_chat=f"!tg {query}"))
        markup.add(telebot.types.InlineKeyboardButton(text='Zooqle', switch_inline_query_current_chat=f"!zoo {query}"), telebot.types.InlineKeyboardButton(text='Kick Ass', switch_inline_query_current_chat=f"!ka {query}") , telebot.types.InlineKeyboardButton(text='Bit Search', switch_inline_query_current_chat=f"!bs {query}"))
        markup.add(telebot.types.InlineKeyboardButton(text='Glodls', switch_inline_query_current_chat=f"!gl {query}"), telebot.types.InlineKeyboardButton(text='Magnet DL', switch_inline_query_current_chat=f"!mdl {query}") , telebot.types.InlineKeyboardButton(text='Lime Torrent', switch_inline_query_current_chat=f"!lt {query}"))
        markup.add(telebot.types.InlineKeyboardButton(text='Torrent Funk', switch_inline_query_current_chat=f"!tf {query}"), telebot.types.InlineKeyboardButton(text='Torrent Project', switch_inline_query_current_chat=f"!tp {query}"))
    
    
    else:
        if msg:
            markup.add(telebot.types.InlineKeyboardButton(text='🌟 Rate ', url='https://t.me/tlgrmcbot?start=torrenthuntbot-review'), telebot.types.InlineKeyboardButton(text=language['donateBtn'][userLanguage], url='https://buymeacoffee.com/hemantapkh'))
    
    return msg, markup
    