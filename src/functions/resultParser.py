from time import time
from src.objs import *

#: Parse the torrent result
def result(response, userLanguage, resultType, torrentType, page, category=None, week=None, query=None, originalQuery=None):
    msg = ''
    markup = None
    
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
                    buttons.append(pyrogram.types.InlineKeyboardButton('🔘' if i == page else i, callback_data=f"cb_nextPage{time()}:{i}:{torrentType}-{category}-{week}:{query or ''}"))

                markup = pyrogram.types.InlineKeyboardMarkup([buttons])

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
                buttons.append(pyrogram.types.InlineKeyboardButton('🔘' if i == page else i, callback_data=cb))
            
            markup = pyrogram.types.InlineKeyboardMarkup([buttons])

            if pageCount > 10:
                if page <= 10:
                    cb = f"q{str(time())[-3:]}:{firstPage+10}:{query}" if query else f"cb_nextPage{time()}:{firstPage+10}:{torrentType}-{category}-{week}"
                    markup.inline_keyboard.append([pyrogram.types.InlineKeyboardButton(language['nextBtn'][userLanguage], callback_data=cb)])

                elif 10 < page <= (pageCount - 10):
                    cb1 = f"q{str(time())[-3:]}:{firstPage-10}:{query}" if query else f"cb_nextPage{time()}:{firstPage-10}:{torrentType}-{category}-{week}"
                    cb2 = f"q{str(time())[-3:]}:{firstPage+10}:{query}" if query else f"cb_nextPage{time()}:{firstPage+10}:{torrentType}-{category}-{week}"

                    markup.inline_keyboard.append([pyrogram.types.InlineKeyboardButton(language['previousBtn'][userLanguage], callback_data=cb1), pyrogram.types.InlineKeyboardButton(language['nextBtn'][userLanguage], callback_data=cb2)])
                
                else:
                    cb = f"q{str(time())[-3:]}:{firstPage-10}:{query}" if query else f"cb_nextPage{time()}:{firstPage-10}:{torrentType}-{category}-{week}"
                    markup.inline_keyboard.append([pyrogram.types.InlineKeyboardButton(language['previousBtn'][userLanguage], callback_data=cb)])                      
                        
    if query:
        button1 = [pyrogram.types.InlineKeyboardButton(text='⚡️ Pirate', switch_inline_query_current_chat=f"!pb {query}"), pyrogram.types.InlineKeyboardButton(text='⚡️ Rarbg', switch_inline_query_current_chat=f"!rb {query}")]
        button2 = [pyrogram.types.InlineKeyboardButton(text='🎎 Nyaa', switch_inline_query_current_chat=f"!nyaa {query}"), pyrogram.types.InlineKeyboardButton(text='📺 Ez', switch_inline_query_current_chat=f"!ez {query}"), pyrogram.types.InlineKeyboardButton(text='⚡️ Tor Lock', switch_inline_query_current_chat=f"!tl {query}")]
        button3 = [pyrogram.types.InlineKeyboardButton(text='🍿 YTS', switch_inline_query_current_chat=f"!yts {query}"), pyrogram.types.InlineKeyboardButton(text='📺 Et', switch_inline_query_current_chat=f"!et {query}") , pyrogram.types.InlineKeyboardButton(text='⚡️ Galaxy', switch_inline_query_current_chat=f"!tg {query}")]

        if not msg:
            query = originalQuery
        
        if markup:
            markup.inline_keyboard.append(button1)
            markup.inline_keyboard.append(button2)
            markup.inline_keyboard.append(button3)
        
        else:
            markup = pyrogram.types.InlineKeyboardMarkup([button1, button2, button3])
    
    else:
        if msg:
            button1 = pyrogram.types.InlineKeyboardButton(text='🌟 Rate ', url='https://t.me/tlgrmcbot?start=torrenthuntbot-review')
            button2 = pyrogram.types.InlineKeyboardButton(text=language['donateBtn'][userLanguage], url='https://buymeacoffee.com/hemantapkh')

            if markup:
                markup.inline_keyboard.append([button1, button2])

            else:
                markup = pyrogram.types.InlineKeyboardMarkup([[button1, button2]])
    
    return msg, markup