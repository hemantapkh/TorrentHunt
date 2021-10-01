import base64
from src.objs import *
from src.functions.resultParser import result
from src.functions.funs import getSuggestions, sortList

#: Custom query search
def querySearch(message, userLanguage):
    sent = bot.send_message(message.chat.id, language['searchingQuery'][userLanguage].format(message.text))
    response = torrent.search(message.text)

    msg, markup = result(response, userLanguage, torrentType='query', page=1, query=message.text)
    
    if not msg:
        try:
            suggestion = getSuggestions(message.text)
            
            if suggestion:
                if suggestion[0] != message.text:
                    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['searchingQuery'][userLanguage].format(suggestion[0]))
                    response = torrent.search(suggestion[0])
                    
                    msg, markup = result(response, userLanguage, torrentType='query', page=1, query=suggestion[0])

                if not msg:
                    markup.row_width = 3
                    suggestion = sortList(suggestion)
                    buttons = []
                    smallButtons = []
                    
                    for i in suggestion[1:]:
                        suggestedQuery = base64.b64encode(i.encode()).decode()
                        
                        if len(suggestedQuery) <= 64:
                            if len(i) < 13:
                                smallButtons.append(telebot.types.InlineKeyboardButton(text=i, url=f"https://t.me/torrenthuntbot?start={suggestedQuery}"))
                            
                            elif len(i) < 18:
                                buttons.append(telebot.types.InlineKeyboardButton(text=i, url=f"https://t.me/torrenthuntbot?start={suggestedQuery}"))
                            
                            else:
                                markup.add(telebot.types.InlineKeyboardButton(text=i, url=f"https://t.me/torrenthuntbot?start={suggestedQuery}"))

                    markup.add(*smallButtons)
                    markup.row_width = 2
                    markup.add(*buttons)
                    
                bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg or language['noResults'][userLanguage], reply_markup=markup)
            
            else:
                bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['noResults'][userLanguage], reply_markup=markup)
        
        except Exception as e:
            bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['noResults'][userLanguage], reply_markup=markup)
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg, reply_markup=markup)