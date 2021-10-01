from src.objs import *
from time import time

#: Settings
@bot.message_handler(commands=['settings'])
def settings(message, userLanguage=None, called=False):
    userLanguage = dbSql.getSetting(message.from_user.id, 'language')
    restrictedMode = dbSql.getSetting(message.from_user.id, 'restrictedMode')
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text=language['languageSetting'][userLanguage], callback_data=f'cb_languageSetting{time()}'))
    markup.add(telebot.types.InlineKeyboardButton(text=language['turnOffRestrictedMode' if restrictedMode else 'turnOnRestrictedMode'][userLanguage], callback_data=f"cb_restrictedMode{'Off' if restrictedMode else 'On'}"))

    #! Edit the message if called
    if called:
        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id, text=language['settings'][userLanguage].format(language['settingsBtn'][userLanguage]), reply_markup=markup)
    
    #! Else, send a new message
    else:
        bot.send_message(message.chat.id, text=language['settings'][userLanguage].format(language['settingsBtn'][userLanguage]), reply_markup=markup)