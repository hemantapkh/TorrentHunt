from src.objs import *

#: Help menu
@bot.message_handler(commands=['help'])
def help(message, userLanguage=None):
    userLanguage = userLanguage or dbSql.getSetting(message.chat.id, 'language')

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text=language['inlineSearchBtn'][userLanguage], switch_inline_query_current_chat=""))
    bot.send_message(message.chat.id, language['help'][userLanguage].format(language['helpBtn'][userLanguage]), reply_markup=markup)