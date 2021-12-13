from src.objs import *

#: Help menu
@bot.on_message(filters.command('help'))
async def help(client, message, userLanguage=None):
    userLanguage = userLanguage or dbSql.getSetting(message.chat.id, 'language')

    markup= pyrogram.types.InlineKeyboardMarkup([
        [pyrogram.types.InlineKeyboardButton(text=language['inlineSearchBtn'][userLanguage], switch_inline_query_current_chat="")]
    ])
    
    await bot.send_message(message.chat.id, language['help'][userLanguage].format(language['helpBtn'][userLanguage]), reply_markup=markup)