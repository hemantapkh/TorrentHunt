import base64

from src.objs import *
from src.commands.querySearch import querySearch
from src.functions.keyboard import mainReplyKeyboard, lang

#: Start handler
@bot.on_message(filters.command(['start', f'start{botUsername}']))
async def start(Client, message):
    if dbSql.setAccount(message.chat.id, message.chat.username):
        userLanguage = dbSql.getSetting(message.chat.id, 'language')
        params = message.text.split()[1] if len(message.text.split()) > 1 else None

        #! If start paramater is passed
        if message.chat.type == 'private':
            if params:
                try:
                    message.text = base64.b64decode(params.encode('utf')).decode('utf')

                    await querySearch(message, userLanguage)

                except Exception:
                    await bot.send_message(message.chat.id, text=language['greet'][userLanguage].format(message.from_user.first_name), reply_markup=mainReplyKeyboard(userLanguage), disable_web_page_preview=True)
        
            else:
                await bot.send_message(message.chat.id, text=language['greet'][userLanguage].format(message.from_user.first_name), reply_markup=mainReplyKeyboard(userLanguage), disable_web_page_preview=True)
        
        else:
            await bot.send_message(message.chat.id, text=language['greetGroup'][userLanguage].format(message.chat.title), disable_web_page_preview=True)
    else:
        if message.chat.type == 'private':
            await lang(message, userLanguage='english', greet=True)
        
        else:
            chatMember = await bot.get_chat_member(message.chat.id, message.from_user.id)

            if chatMember.status in ['creator', 'administrator']:
                await lang(message, userLanguage='english', greet=True)

            else:
                await bot.send_message(message.chat.id, text=language['greetGroup']['english'].format(message.chat.title), disable_web_page_preview=True)