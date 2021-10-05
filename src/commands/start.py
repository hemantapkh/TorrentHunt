import base64
from src.objs import *
from src.commands.querySearch import querySearch
from src.functions.keyboard import mainReplyKeyboard, lang

#: Start handler
@bot.message_handler(commands=['start'])
def start(message):
    if dbSql.setAccount(message.from_user.id):
        userLanguage = dbSql.getSetting(message.from_user.id, 'language')
        params = message.text.split()[1] if len(message.text.split()) > 1 else None

        #! If start paramater is passed
        if params:
            try:
                message.text = base64.b64decode(params.encode('utf')).decode('utf')

                querySearch(message, userLanguage)

            except Exception:
                bot.send_message(message.chat.id, text=language['greet'][userLanguage].format(message.from_user.first_name), reply_markup=mainReplyKeyboard(userLanguage), disable_web_page_preview=True)
        else:
            bot.send_message(message.chat.id, text=language['greet'][userLanguage].format(message.from_user.first_name), reply_markup=mainReplyKeyboard(userLanguage), disable_web_page_preview=True)
    else:
        lang(message, userLanguage='english', greet=True)