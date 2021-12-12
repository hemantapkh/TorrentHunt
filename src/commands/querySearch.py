import base64
from src.objs import *
from src.functions.resultParser import result
from src.functions.funs import getSuggestions

#: Custom query search
def querySearch(message, userLanguage):
    if message.chat.type == "private":
        sent = bot.send_message(message.chat.id, language['searchingQuery'][userLanguage].format(message.text))
    
    else:
        message.text =  message.text[1:] if message.text[0] == '/' else message.text
        message.text = message.text.split(botUsername)[0]
        sent = bot.send_message(message.chat.id, language['searchingQuery'][userLanguage].format(message.text), reply_to_message_id=message.id)
    
    # resultType = dbSql.getSetting(message.chat.id, 'defaultMode')
    # response = torrent.search(message.text)

    # msg, markup = result(response, userLanguage, resultType, torrentType='query', page=1, query=message.text, originalQuery=message.text)
    
    # if not msg:
    #     try:
    #         suggestion = getSuggestions(message.text)
            
    #         if suggestion:
    #             if suggestion[0] != message.text:
    #                 bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['searchingQuery'][userLanguage].format(suggestion[0]))
    #                 response = torrent.search(suggestion[0])
                    
    #                 msg, markup = result(response, userLanguage, resultType, torrentType='query', page=1, query=suggestion[0], originalQuery=message.text)

    #             if not msg:
    #                 markup.add(telebot.types.InlineKeyboardButton(text='🔎 Google suggestions', switch_inline_query_current_chat=f'!google {message.text}'))
                    
    #             bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg or language['noResults'][userLanguage], reply_markup=markup)
            
    #         else:
    #             bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['noResults'][userLanguage], reply_markup=markup)
        
    #     except Exception as e:
    #         bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['noResults'][userLanguage], reply_markup=markup)
    # else:
    #     bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg, reply_markup=markup)

    markup = telebot.types.InlineKeyboardMarkup()

    query = message.text

    markup.add(telebot.types.InlineKeyboardButton(text='⚡️ Pirate', switch_inline_query_current_chat=f"!pb {query}"), telebot.types.InlineKeyboardButton(text='⚡️ Rarbg', switch_inline_query_current_chat=f"!rb {query}"))
    markup.add(telebot.types.InlineKeyboardButton(text='🎎 Nyaa', switch_inline_query_current_chat=f"!nyaa {query}"), telebot.types.InlineKeyboardButton(text='📺 Ez', switch_inline_query_current_chat=f"!ez {query}"), telebot.types.InlineKeyboardButton(text='⚡️ Tor Lock', switch_inline_query_current_chat=f"!tl {query}"))
    markup.add(telebot.types.InlineKeyboardButton(text='🍿 YTS', switch_inline_query_current_chat=f"!yts {query}"), telebot.types.InlineKeyboardButton(text='📺 Et', switch_inline_query_current_chat=f"!et {query}") , telebot.types.InlineKeyboardButton(text='⚡️ Galaxy', switch_inline_query_current_chat=f"!tg {query}"))

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text='<b>⚠️ 1337x is currently down. Please use other sites by clicking the button below.</b>', reply_markup=markup)
    