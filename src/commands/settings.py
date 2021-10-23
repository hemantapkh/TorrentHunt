from src.objs import *
from time import time

#: Settings
@bot.message_handler(commands=['settings'])
def settings(message, userLanguage=None, called=False):
    chatId = message.message.chat.id if called else message.chat.id
    userLanguage = dbSql.getSetting(chatId, 'language')
    
    if (message.message.chat.type if called else message.chat.type) == 'private' or bot.get_chat_member(chatId, message.from_user.id).status in ['creator', 'administrator']:
        restrictedMode = dbSql.getSetting(chatId, 'restrictedMode')
        
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text=language['languageSetting'][userLanguage], callback_data=f'cb_languageSetting{time()}'))
        markup.add(telebot.types.InlineKeyboardButton(text=language['turnOffRestrictedMode' if restrictedMode else 'turnOnRestrictedMode'][userLanguage], callback_data=f"cb_restrictedMode{'Off' if restrictedMode else 'On'}"))

        #! Edit the message if called
        if called:
            bot.edit_message_text(chat_id=chatId, message_id=message.message.id, text=language['settings'][userLanguage].format(language['settingsBtn'][userLanguage]), reply_markup=markup)
        
        #! Else, send a new message
        else:
            bot.send_message(chatId, text=language['settings'][userLanguage].format(language['settingsBtn'][userLanguage]), reply_markup=markup, reply_to_message_id=message.id if message.chat.type != 'private' else None)

    else:
        bot.send_message(chatId, text=language['noPermission'][userLanguage], reply_to_message_id=message.id if message.chat.type != 'private' else None)