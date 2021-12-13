from src.objs import *

#: Support menu
@bot.on_message(filters.command('support'))
async def support(client, message, userLanguage=None):
    userLanguage = userLanguage or dbSql.getSetting(message.chat.id, 'language')

    buttons = [
        [pyrogram.types.InlineKeyboardButton(text=language['donateBtn'][userLanguage], url='https://buymeacoffee.com/hemantapkh')], 
        [pyrogram.types.InlineKeyboardButton(text=language['subscribeChannelBtn'][userLanguage], url='https://youtube.com/h9youtube'), pyrogram.types.InlineKeyboardButton(text=language['followGithubBtn'][userLanguage], url='https://github.com/hemantapkh')],
        [pyrogram.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='t.me/h9youtube'), pyrogram.types.InlineKeyboardButton(text=language['joinDiscussionBtn'][userLanguage], url='https://t.me/h9discussion')],
    ]

    markup = pyrogram.types.InlineKeyboardMarkup(buttons)
    
    await bot.send_message(message.chat.id, language['support'][userLanguage].format(language['supportBtn'][userLanguage]), reply_markup=markup, disable_web_page_preview=True)