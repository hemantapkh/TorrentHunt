import base64

from src.objs import *
from src.commands.querySearch import querySearch
from src.functions.keyboard import mainReplyKeyboard, lang

#: Start handler
@bot.message_handler(commands=['start'])
def start(message):
    params = message.text.split()[1].split('_') if len(message.text.split()) > 1 else None

    referrer = params[0] if params else None
    query = params[1] if params and len(params) > 1 else None

    if dbSql.setAccount(message.chat.id, message.chat.username, referrer):
        userLanguage = dbSql.getSetting(message.chat.id, 'language')

        #! If start paramater is passed
        if message.chat.type == 'private':
            if query:
                try:
                    message.text = base64.b64decode(query.encode('utf')).decode('utf')

                    querySearch(message, userLanguage)

                except Exception:
                    bot.send_message(message.chat.id, text=language['greet'][userLanguage].format(message.from_user.first_name), reply_markup=mainReplyKeyboard(userLanguage), disable_web_page_preview=True)

            else:
                bot.send_message(message.chat.id, text=language['greet'][userLanguage].format(message.from_user.first_name), reply_markup=mainReplyKeyboard(userLanguage), disable_web_page_preview=True)

        else:
            bot.send_message(message.chat.id, text=language['greetGroup'][userLanguage].format(message.chat.title), disable_web_page_preview=True)
    else:
        if message.chat.type == 'private':
            lang(message, userLanguage='english', greet=True)

        else:
            if bot.get_chat_member(message.chat.id, message.from_user.id).status in ['creator', 'administrator']:
                lang(message, userLanguage='english', greet=True)

            else:
                bot.send_message(message.chat.id, text=language['greetGroup']['english'].format(message.chat.title), disable_web_page_preview=True)