from time import time
from src.objs import *

#: Parse the torrent result
def result(response, userLanguage, torrentType, page, category=None, week=None, query=None):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.one_time_keyboard=True
    markup.row_width = 5
    
    msg = ''
    if response['items']:
        response['items'].reverse()
        for count, item in enumerate(response['items']):
            #! Show only 20 items per page
            if count >= 20:
                break

            msg += f"<b>{((page)*20)-count}. {item['name']}</b>\n\n"
            msg += f"💾 {item['size']}, 🟢 {item['seeders']}, 🔴 {item['leechers']}\n\n"

            msg += f"{language['link'][userLanguage]} /getLink_{item['torrentId']}\n"
            msg += f"{language['moreInfo'][userLanguage]} /getInfo_{item['torrentId']}\n\n"

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
        markup.add(telebot.types.InlineKeyboardButton(text='⚡️ 1337x 🔎', switch_inline_query_current_chat=f"!1337x {query}"), telebot.types.InlineKeyboardButton(text='🚀 Pirate 🔎', switch_inline_query_current_chat=f"!pb {query}"), telebot.types.InlineKeyboardButton(text='⚠️ Rarbg 🔎', switch_inline_query_current_chat=f"!rb {query}"))
        markup.add(telebot.types.InlineKeyboardButton(text='🎎 Nyaa 🔎', switch_inline_query_current_chat=f"!nyaa {query}"), telebot.types.InlineKeyboardButton(text='🔻 Ez 🔎', switch_inline_query_current_chat=f"!ez {query}"), telebot.types.InlineKeyboardButton(text='🐌 Tor Lock 🔎', switch_inline_query_current_chat=f"!tl {query}"))
        markup.add(telebot.types.InlineKeyboardButton(text='🍿 YTS 🔎', switch_inline_query_current_chat=f"!yts {query}"), telebot.types.InlineKeyboardButton(text='⚡️ Et 🔎', switch_inline_query_current_chat=f"!et {query}") , telebot.types.InlineKeyboardButton(text='🚀 Galaxy 🔎', switch_inline_query_current_chat=f"!tg {query}"))
    
    else:
        if msg:
            markup.add(telebot.types.InlineKeyboardButton(text=language['donateBtn'][userLanguage], url='https://buymeacoffee.com/hemantapkh'))
            markup.add(telebot.types.InlineKeyboardButton(text='🌟 Rate ', url='https://t.me/tlgrmcbot?start=torrenthuntbot-review'))
    
    return msg, markup