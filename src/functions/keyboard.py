from time import time
from src.objs import *

#: Main reply keyboard
def mainReplyKeyboard(userLanguage):
    keyboard = pyrogram.types.ReplyKeyboardMarkup([

    [pyrogram.types.KeyboardButton(text=language['trendingBtn'][userLanguage]), pyrogram.types.KeyboardButton(text=language['popularBtn'][userLanguage])],
    [pyrogram.types.KeyboardButton(text=language['topBtn'][userLanguage]), pyrogram.types.KeyboardButton(text=language['browseBtn'][userLanguage])],
    [pyrogram.types.KeyboardButton(text=language['settingsBtn'][userLanguage]), pyrogram.types.KeyboardButton(text=language['helpBtn'][userLanguage]), pyrogram.types.KeyboardButton(text=language['supportBtn'][userLanguage])]], 
    
    resize_keyboard=True)
        
    return keyboard

#: Category reply keyboard
def categoryReplyKeyboard(userLanguage, allCategories, restrictedMode):
    button1 = pyrogram.types.KeyboardButton(text=language['moviesBtn'][userLanguage])
    button2 = pyrogram.types.KeyboardButton(text=language['tvBtn'][userLanguage])
    button3 = pyrogram.types.KeyboardButton(text=language['docsBtn'][userLanguage])
    button4 = pyrogram.types.KeyboardButton(text=language['gamesBtn'][userLanguage])
    button5 = pyrogram.types.KeyboardButton(text=language['musicBtn'][userLanguage])
    button6 = pyrogram.types.KeyboardButton(text=language['appsBtn'][userLanguage])
    button7 = pyrogram.types.KeyboardButton(text=language['animeBtn'][userLanguage])
    button8 = pyrogram.types.KeyboardButton(text=language['xxxBtn'][userLanguage])
    button9 = pyrogram.types.KeyboardButton(text=language['othersBtn'][userLanguage])
    button10 = pyrogram.types.KeyboardButton(text=language['allBtn'][userLanguage])
    button11 = pyrogram.types.KeyboardButton(text=language['mainMenuBtn'][userLanguage])
    
    keyboard = pyrogram.types.ReplyKeyboardMarkup([
        [button1, button2, button3],
        [button4, button5, button6]
    ], 
    
    resize_keyboard=True)

    if restrictedMode:
        keyboard.keyboard.append([button7, button9, button10]) if allCategories else keyboard.keyboard.append([button7, button9])
        keyboard.keyboard.append([button11])
    
    else:
        keyboard.keyboard.append([button7, button8, button9])
        keyboard.keyboard.append([button10, button11]) if allCategories else keyboard.keyboard.append([button11])
   
    return keyboard

#: Select language
async def lang(message, userLanguage, called=False, greet=False):
    markup = pyrogram.types.InlineKeyboardMarkup([
        [pyrogram.types.InlineKeyboardButton('🌐 English', callback_data=f'cb_language_{greet}_english'), pyrogram.types.InlineKeyboardButton('🇳🇵 नेपाली', callback_data=f'cb_language_{greet}_nepali')], # English, Nepali
        [pyrogram.types.InlineKeyboardButton('🇧🇩 বাংলা', callback_data=f'cb_language_{greet}_bengali'), pyrogram.types.InlineKeyboardButton('🇧🇾 Беларуская', callback_data=f'cb_language_{greet}_belarusian')], # Bengali, Belarusian
        [pyrogram.types.InlineKeyboardButton('🏴󠁥󠁳󠁣󠁴󠁿 Català', callback_data=f'cb_language_{greet}_catalan'), pyrogram.types.InlineKeyboardButton('🇳🇱 Nederlands', callback_data=f'cb_language_{greet}_dutch')], # Catalan, Dutch
        [pyrogram.types.InlineKeyboardButton('🇫🇷 français', callback_data=f'cb_language_{greet}_french'), pyrogram.types.InlineKeyboardButton('🇩🇪 Deutsch', callback_data=f'cb_language_{greet}_german')], # French, German
        [pyrogram.types.InlineKeyboardButton('🇮🇳 हिन्दी', callback_data=f'cb_language_{greet}_hindi'), pyrogram.types.InlineKeyboardButton('🇮🇹 Italian', callback_data=f'cb_language_{greet}_italian')], # Hindi, Italian
        [pyrogram.types.InlineKeyboardButton('🇰🇷 한국어', callback_data=f'cb_language_{greet}_korean'), pyrogram.types.InlineKeyboardButton('🇮🇩 Bahasa Melayu', callback_data=f'cb_language_{greet}_malay')], # Korean, Malay
        [pyrogram.types.InlineKeyboardButton('🇵🇱 Polski', callback_data=f'cb_language_{greet}_polish'), pyrogram.types.InlineKeyboardButton('🇧🇷 Português', callback_data=f'cb_language_{greet}_portuguese')], # Polish, Portuguese
        [pyrogram.types.InlineKeyboardButton('🇷🇺 русский', callback_data=f'cb_language_{greet}_russian'), pyrogram.types.InlineKeyboardButton('🇪🇸 español', callback_data=f'cb_language_{greet}_spanish')], # Russian, Spanish
        [pyrogram.types.InlineKeyboardButton('🇹🇷 Türkçe', callback_data=f'cb_language_{greet}_turkish'), pyrogram.types.InlineKeyboardButton('🇺🇦 Український', callback_data=f'cb_language_{greet}_ukrainian')] # Turkish, Ukrainian
    ])
        
    if called:
        markup.inline_keyboard.append([pyrogram.types.InlineKeyboardButton(text=language['backBtn'][userLanguage], callback_data=f'cb_backToSettings{time()}')])
        
        await bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id, text=language['chooseLanguage'][userLanguage], reply_markup=markup)
    
    else:
        await bot.send_message(message.chat.id, language['chooseLanguage'][userLanguage], reply_markup=markup, reply_to_message_id=message.message_id)

#: Markup for non subscribed users
def notSubscribedMarkup(userLanguage):
    markup = pyrogram.types.InlineKeyboardMarkup([[
            pyrogram.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='https://t.me/h9youtube'),
            pyrogram.types.InlineKeyboardButton(text=language['subscribeChannelBtn'][userLanguage], url='https://www.youtube.com/h9youtube?sub_confirmation=1'),
            ]])
    
    return markup