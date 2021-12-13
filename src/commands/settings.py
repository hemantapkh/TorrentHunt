from src.objs import *
from time import time

#: Settings
@bot.on_message(filters.command('settings'))
async def settings(client, message, userLanguage=None, called=False):
    chatId = message.message.chat.id if called else message.chat.id
    userLanguage = userLanguage or dbSql.getSetting(chatId, 'language')
    
    if (message.message.chat.type if called else message.chat.type) == 'private' or bot.get_chat_member(chatId, message.from_user.id).status in ['creator', 'administrator']:
        restrictedMode = dbSql.getSetting(chatId, 'restrictedMode')
        
        markup = pyrogram.types.InlineKeyboardMarkup([
            [pyrogram.types.InlineKeyboardButton(text=language['languageSetting'][userLanguage], callback_data=f'cb_languageSetting{time()}')],
            [pyrogram.types.InlineKeyboardButton(text=language['turnOffRestrictedMode' if restrictedMode else 'turnOnRestrictedMode'][userLanguage], callback_data=f"cb_restrictedMode{'Off' if restrictedMode else 'On'}")]
        ])

        #! Edit the message if called
        if called:
            await bot.edit_message_text(chat_id=chatId, message_id=message.message.message_id, text=language['settings'][userLanguage].format(language['settingsBtn'][userLanguage]), reply_markup=markup)
        
        #! Else, send a new message
        else:
            await bot.send_message(chatId, text=language['settings'][userLanguage].format(language['settingsBtn'][userLanguage]), reply_markup=markup, reply_to_message_id=message.message_id if message.chat.type != 'private' else None)

    else:
        await bot.send_message(chatId, text=language['noPermission'][userLanguage], reply_to_message_id=message.message_id if message.chat.type != 'private' else None)