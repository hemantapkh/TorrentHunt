import base64
from src.objs import *
from src.functions.resultParser import result
from src.functions.funs import getSuggestions

#: Custom query search
def querySearch(message, userLanguage):
    sent = bot.send_message(message.chat.id, language['searchingQuery'][userLanguage].format(message.text))
    response = torrent.search(message.text)

    msg, markup = result(response, userLanguage, torrentType='query', page=1, query=message.text, originalQuery=message.text)
    
    if not msg:
        try:
            suggestion = getSuggestions(message.text)
            
            if suggestion:
                if suggestion[0] != message.text:
                    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['searchingQuery'][userLanguage].format(suggestion[0]))
                    response = torrent.search(suggestion[0])
                    
                    msg, markup = result(response, userLanguage, torrentType='query', page=1, query=suggestion[0], originalQuery=message.text)

                if not msg:
                    markup.add(telebot.types.InlineKeyboardButton(text='🔎 Google suggestions', switch_inline_query_current_chat=f'!google {message.text}'))
                    
                bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg or language['noResults'][userLanguage], reply_markup=markup)
            
            else:
                bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['noResults'][userLanguage], reply_markup=markup)
        
        except Exception as e:
            bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['noResults'][userLanguage], reply_markup=markup)
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg, reply_markup=markup)