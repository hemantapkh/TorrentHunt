from time import time
from src.objs import *

#: Main reply keyboard
def mainReplyKeyboard(userLanguage):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    button1 = telebot.types.KeyboardButton(text=language['trendingBtn'][userLanguage])
    button2 = telebot.types.KeyboardButton(text=language['popularBtn'][userLanguage])
    button3 = telebot.types.KeyboardButton(text=language['topBtn'][userLanguage])
    button4 = telebot.types.KeyboardButton(text=language['browseBtn'][userLanguage])
    button5 = telebot.types.KeyboardButton(text=language['settingsBtn'][userLanguage])
    button6 = telebot.types.KeyboardButton(text=language['helpBtn'][userLanguage])
    button7 = telebot.types.KeyboardButton(text=language['supportBtn'][userLanguage])
    
    keyboard.row(button1, button2)
    keyboard.row(button3, button4)
    keyboard.row(button5, button6, button7)

    return keyboard

#: Category reply keyboard
def categoryReplyKeyboard(userLanguage, allCategories, restrictedMode):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = telebot.types.KeyboardButton(text=language['moviesBtn'][userLanguage])
    button2 = telebot.types.KeyboardButton(text=language['tvBtn'][userLanguage])
    button3 = telebot.types.KeyboardButton(text=language['docsBtn'][userLanguage])
    button4 = telebot.types.KeyboardButton(text=language['gamesBtn'][userLanguage])
    button5 = telebot.types.KeyboardButton(text=language['musicBtn'][userLanguage])
    button6 = telebot.types.KeyboardButton(text=language['appsBtn'][userLanguage])
    button7 = telebot.types.KeyboardButton(text=language['animeBtn'][userLanguage])
    button8 = telebot.types.KeyboardButton(text=language['xxxBtn'][userLanguage])
    button9 = telebot.types.KeyboardButton(text=language['othersBtn'][userLanguage])
    button10 = telebot.types.KeyboardButton(text=language['allBtn'][userLanguage])
    button11 = telebot.types.KeyboardButton(text=language['mainMenuBtn'][userLanguage])

    keyboard.row(button1, button2, button3)
    keyboard.row(button4, button5, button6)

    if restrictedMode:
        keyboard.row(button7, button9, button10) if allCategories else keyboard.row(button7, button9)
        keyboard.row(button11)
    
    else:
        keyboard.row(button7, button8, button9)
        keyboard.row(button10, button11) if allCategories else keyboard.row(button11)
   
    return keyboard

#: Select language
def lang(message, userLanguage, called=False, greet=False):
    markup = telebot.types.InlineKeyboardMarkup()
    
    markup.add(telebot.types.InlineKeyboardButton('🌐 English', callback_data=f'cb_language_{greet}_english'), telebot.types.InlineKeyboardButton('🇳🇵 नेपाली', callback_data=f'cb_language_{greet}_nepali')) # English, Nepali
    markup.add(telebot.types.InlineKeyboardButton('🇧🇩 বাংলা', callback_data=f'cb_language_{greet}_bengali'), telebot.types.InlineKeyboardButton('🇧🇾 Беларуская', callback_data=f'cb_language_{greet}_belarusian')) # Bengali, Belarusian
    markup.add(telebot.types.InlineKeyboardButton('🏴󠁥󠁳󠁣󠁴󠁿 Català', callback_data=f'cb_language_{greet}_catalan'), telebot.types.InlineKeyboardButton('🇳🇱 Nederlands', callback_data=f'cb_language_{greet}_dutch')) # Catalan, Dutch
    markup.add(telebot.types.InlineKeyboardButton('🇫🇷 français', callback_data=f'cb_language_{greet}_french'), telebot.types.InlineKeyboardButton('🇩🇪 Deutsch', callback_data=f'cb_language_{greet}_german')) # French, German
    markup.add(telebot.types.InlineKeyboardButton('🇮🇳 हिन्दी', callback_data=f'cb_language_{greet}_hindi'), telebot.types.InlineKeyboardButton('🇮🇹 Italian', callback_data=f'cb_language_{greet}_italian')) # Hindi, Italian
    markup.add(telebot.types.InlineKeyboardButton('🇰🇷 한국어', callback_data=f'cb_language_{greet}_korean'), telebot.types.InlineKeyboardButton('🇮🇩 Bahasa Melayu', callback_data=f'cb_language_{greet}_malay')) # Korean, Malay
    markup.add(telebot.types.InlineKeyboardButton('🇵🇱 Polski', callback_data=f'cb_language_{greet}_polish'), telebot.types.InlineKeyboardButton('🇧🇷 Português', callback_data=f'cb_language_{greet}_portuguese')) # Polish, Portuguese
    markup.add(telebot.types.InlineKeyboardButton('🇷🇺 русский', callback_data=f'cb_language_{greet}_russian'), telebot.types.InlineKeyboardButton('🇪🇸 español', callback_data=f'cb_language_{greet}_spanish')) # Russian, Spanish
    markup.add(telebot.types.InlineKeyboardButton('🇹🇷 Türkçe', callback_data=f'cb_language_{greet}_turkish'), telebot.types.InlineKeyboardButton('🇺🇦 Український', callback_data=f'cb_language_{greet}_ukrainian')) # Turkish, Ukrainian
    
    if called:
        markup.add(telebot.types.InlineKeyboardButton(text=language['backBtn'][userLanguage], callback_data=f'cb_backToSettings{time()}'))
        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id, text=language['chooseLanguage'][userLanguage], reply_markup=markup)
    else:
        bot.send_message(message.chat.id, language['chooseLanguage'][userLanguage], reply_markup=markup, reply_to_message_id=message.id)

#: Markup for non subscribed users
def notSubscribedMarkup(userLanguage):
    markup = telebot.types.InlineKeyboardMarkup([
            [telebot.types.InlineKeyboardButton(text=language['subscribeChannelBtn'][userLanguage], url='https://www.youtube.com/h9youtube?sub_confirmation=1'),
            telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='https://t.me/h9youtube')]
            ])
    return markup