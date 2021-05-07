import json, ssl
from os import path
from time import time

import telebot, py1337x
from aiohttp import web
from models import dbQuery

# Finding the absolute path of the config file
scriptPath = path.abspath(__file__)
dirPath = path.dirname(scriptPath)
configPath = path.join(dirPath,'config.json')

config = json.load(open(configPath))
language = json.load(open(config['language']))
dbSql = dbQuery(config['database'])

bot = telebot.TeleBot(config['botToken'], parse_mode='HTML')

# Configuration for webhook
webhookBaseUrl = f"https://{config['webhookOptions']['webhookHost']}:{config['webhookOptions']['webhookPort']}"
webhookUrlPath = f"/{config['botToken']}/"

app = web.Application()

# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post('/{token}/', handle)

# Main reply keyboard
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

# Category reply keyboard
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
    keyboard.row(button7, button9) if restrictedMode else keyboard.row(button7, button8, button9)
   
    keyboard.row(button10, button11) if allCategories else keyboard.row(button11)

    return keyboard

# Check if the user is subscribed or not, returns True if subscribed
def isSubscribed(message, userLanguage, sendMessage=True):
    telegramId = message.from_user.id
    subscribed = True
    
    try:
        status = bot.get_chat_member('-1001270853324', telegramId)
        if status.status == 'left':
            subscribed = False
        else:
            return True

    except Exception:
        subscribed = True

    if not subscribed:
        # Send the links if sendMessage is True
        if sendMessage:
            bot.send_message(message.chat.id, text=language['notSubscribed'][userLanguage], reply_markup=telebot.types.InlineKeyboardMarkup([
            [telebot.types.InlineKeyboardButton(text=language['subscribeChannelBtn'][userLanguage], url='https://www.youtube.com/h9youtube?sub_confirmation=1'),
            telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='https://t.me/h9youtube')],
            [telebot.types.InlineKeyboardButton(text=language['doneBtn'][userLanguage], callback_data='cb_checkSubscription')]
            ]))

        return False

# Returns the equivalent category of the text 
def textToCategory(text, userLanguage):
    if text == language['moviesBtn'][userLanguage]:
        return 'movies'
    
    elif text == language['tvBtn'][userLanguage]:
        return 'tv'

    elif text == language['docsBtn'][userLanguage]:
        return 'documentaries'

    elif text == language['gamesBtn'][userLanguage]:
        return 'games'

    elif text == language['musicBtn'][userLanguage]:
        return 'music'

    elif text == language['appsBtn'][userLanguage]:
        return 'apps'

    elif text == language['animeBtn'][userLanguage]:
        return 'anime'

    elif text == language['xxxBtn'][userLanguage]:
        return 'xxx'

    elif text == language['othersBtn'][userLanguage]:
        return 'other'

    elif text == language['allBtn'][userLanguage]:
        return 'all'

    else:
        return None

# Parse the torrent result
def result(response, userLanguage, torrentType, page, category=None, week=None, query=None):
    if response['items']:
            msg = ''
            for count, item in enumerate(response['items']):
                # Show only 20 items per page
                if count >= 20:
                    break
                msg += f"<b>{((page-1)*20)+count+1}. {item['name']}</b>\n\n"
                msg += f"💾 {item['size']}, 🟢 {item['seeders']}, 🔴 {item['leechers']}\n\n"

                msg += f"{language['link'][userLanguage]} /getLink_{item['id']}\n"
                msg += f"{language['moreInfo'][userLanguage]} /getInfo_{item['id']}\n\n"

            pageCount = response['pageCount']

            # Trending, popular and top torrents has more than 20 items in the same page
            if torrentType in ['trending', 'popular', 'top']:
                if response['itemCount'] > 20:
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.one_time_keyboard=True
                    markup.row_width = 6

                    buttons =  []
                    for i in range(1, -(-response['itemCount'] // 20)+1):
                        buttons.append(telebot.types.InlineKeyboardButton('🔘' if i == page else i, callback_data=f"cb_nextPage{time()}:{i}:{torrentType}-{category}-{week}:{query or ''}"))

                    markup.add(*buttons)
                else:
                    markup = None

            # For other category, create page according to pageCount
            elif pageCount > 1:
                # FirstPage is the firstPage in a page list. Eg: FirstPage of (1 to 10) is 1, (11 to 20) is 11.
                firstPage = 1
                for i in range(-(-page // 10)-1):
                    firstPage += 10
                
                markup = telebot.types.InlineKeyboardMarkup()
                markup.one_time_keyboard=True
                markup.row_width = 5

                buttons =  []
                for i in range(firstPage, pageCount+1):
                    # Show 10 buttons at once
                    if len(buttons) >= 10:
                        break
                    buttons.append(telebot.types.InlineKeyboardButton('🔘' if i == page else i, callback_data=f"cb_nextPage{time()}:{i}:{torrentType}-{category}-{week}:{query or ''}"))

                markup.add(*buttons)
                if pageCount > 10:
                    if page <= 10:
                        markup.add(telebot.types.InlineKeyboardButton(language['nextBtn'][userLanguage], callback_data=f"cb_nextPage{time()}:{firstPage+10}:{torrentType}-{category}-{week}:{query or ''}"))

                    elif 10 < page <= (pageCount - 10):
                        markup.add(telebot.types.InlineKeyboardButton(language['previousBtn'][userLanguage], callback_data=f"cb_nextPage{time()}:{firstPage-10}:{torrentType}-{category}-{week}:{query or ''}"), telebot.types.InlineKeyboardButton(language['nextBtn'][userLanguage], callback_data=f"cb_nextPage{time()}:{firstPage+10}:{torrentType}-{category}-{week}:{query or ''}"))
                    
                    else:
                        markup.add(telebot.types.InlineKeyboardButton(language['previousBtn'][userLanguage], callback_data=f"cb_nextPage{time()}:{firstPage-10}:{torrentType}-{category}-{week}:{query or ''}"))                      
            
            # No markup if items are less than 20
            else:
                markup = None
    # No markup and message if items are empty
    else:
        msg = markup = None

    return msg, markup

# Start handler
@bot.message_handler(commands=['start'])
def start(message):
    if dbSql.setAccount(message.from_user.id):
        userLanguage = dbSql.getSetting(message.from_user.id, 'language')
        bot.send_message(message.chat.id, text=language['greet'][userLanguage].format(message.from_user.first_name), reply_markup=mainReplyKeyboard(userLanguage), disable_web_page_preview=True)
    else:
        lang(message, userLanguage='english', greet=True)

# Settings
@bot.message_handler(commands=['settings'])
def settings(message, userLanguage, called=False):
    restrictedMode = dbSql.getSetting(message.from_user.id, 'restrictedMode')
    markup = telebot.types.InlineKeyboardMarkup()
    
    markup.add(telebot.types.InlineKeyboardButton(text=language['languageSetting'][userLanguage], callback_data=f'cb_languageSetting{time()}'))
    markup.add(telebot.types.InlineKeyboardButton(text=language['turnOffRestrictedMode' if restrictedMode else 'turnOnRestrictedMode'][userLanguage], callback_data=f"cb_restrictedMode{'Off' if restrictedMode else 'On'}"))

    # Edit the message if called
    if called:
        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id, text=language['settings'][userLanguage].format(language['settingsBtn'][userLanguage]), reply_markup=markup)
    # Else, send a new message
    else:
        bot.send_message(message.chat.id, text=language['settings'][userLanguage].format(language['settingsBtn'][userLanguage]), reply_markup=markup)

# Select language
def lang(message, userLanguage, called=False, greet=False):
    markup = telebot.types.InlineKeyboardMarkup()
    
    markup.add(telebot.types.InlineKeyboardButton('🌐 English', callback_data=f'cb_language_{greet}_english'), telebot.types.InlineKeyboardButton('🇳🇵 नेपाली', callback_data=f'cb_language_{greet}_nepali')) # English, Nepali
    markup.add(telebot.types.InlineKeyboardButton('🇧🇩 Bengali', callback_data=f'cb_language_{greet}_bengali'), telebot.types.InlineKeyboardButton('🇧🇾 Беларуская', callback_data=f'cb_language_{greet}_belarusian')) # Bengali, Belarusian
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
        bot.send_message(message.chat.id, language['chooseLanguage'][userLanguage], reply_markup=markup)

# Handler for trending, popular, top and browse torrents
@bot.message_handler(commands=['trending', 'popular', 'top', 'browse'])
def browse(message,userLanguage, torrentType=None, referred=False, customMessage=None):
    if referred or isSubscribed(message, userLanguage):
        torrentType = torrentType or message.text.split()[0][1:]
        
        sent = bot.send_message(message.chat.id, text=customMessage or language['selectCategory'][userLanguage], reply_markup=categoryReplyKeyboard(userLanguage, allCategories=False if torrentType == 'browse' else True, restrictedMode=dbSql.getSetting(message.from_user.id, 'restrictedMode')))
        bot.register_next_step_handler(sent, browse2, userLanguage, torrentType)

# Next step handler for trending, popular, top and browse torrents
def browse2(message, userLanguage, torrentType, category=None, customMessage=None):
    # Main menu
    if message.text == language['mainMenuBtn'][userLanguage]:
        bot.send_message(message.chat.id, text=language['backToMenu'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
    else:
        category = category or textToCategory(message.text, userLanguage)
        if category:
            # Send time keyboard if trending and popular torrents
            if torrentType in ['trending', 'popular']:
                keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

                button1 = telebot.types.KeyboardButton(text=language['trendingToday' if torrentType == 'trending' else 'popularToday'][userLanguage])
                button2 = telebot.types.KeyboardButton(text=language['trendingThisWeek' if torrentType == 'trending' else 'popularThisWeek'][userLanguage])
                button3 = telebot.types.KeyboardButton(text=language['backBtn'][userLanguage])
                button4 = telebot.types.KeyboardButton(text=language['mainMenuBtn'][userLanguage])

                keyboard.row(button1)
                keyboard.row(button2)
                keyboard.row(button3, button4)

                sent = bot.send_message(message.chat.id, text=customMessage or language['selectTimePeriod'][userLanguage], reply_markup=keyboard)
                bot.register_next_step_handler(sent, browse3, userLanguage, torrentType, category)
            else:
                browse4(message, userLanguage, torrentType, category)
        else:
            browse(message, userLanguage, torrentType,referred=True, customMessage=language['unknownCategory'][userLanguage])

# Next step handler for trending and popular torrents
def browse3(message, userLanguage, torrentType, category):
    # Main menu
    if message.text == language['mainMenuBtn'][userLanguage]:
        bot.send_message(message.chat.id, text=language['backToMenu'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
    # Back
    elif message.text == language['backBtn'][userLanguage]:
        browse(message,userLanguage, torrentType, referred=True)
    else:
        week = True if message.text == language[torrentType+'ThisWeek'][userLanguage] else False if message.text == language[torrentType+'Today'][userLanguage] else None
        
        # If week is None, return to browse2
        if week == None:
            browse2(message, userLanguage, torrentType, category, customMessage=language['unknownTimePeriod'][userLanguage])
        
        else:
            bot.send_message(message.chat.id, text=language['fetchingTorrents'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))

            torrent = py1337x.py1337x()
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, week=week)

            msg, markup = result(response, userLanguage, torrentType, 1, category, week)
            
            bot.send_message(chat_id=message.chat.id, text=msg or language['emptyPage'][userLanguage], reply_markup=markup)

# Next step handler for top and browse torrents
def browse4(message, userLanguage, torrentType, category):
    bot.send_message(message.chat.id, text=language['fetchingTorrents'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
    
    torrent = py1337x.py1337x()
    response =  getattr(torrent, torrentType)(category=None if category == 'all' else category)

    msg, markup = result(response, userLanguage, torrentType, 1, category)

    bot.send_message(chat_id=message.chat.id, text=msg or language['emptyPage'][userLanguage], reply_markup=markup)
    
# Get magnet link of the torrent
@bot.message_handler(func=lambda message: message.text and message.text[:9] == '/getLink_')
def getLink(message):
    userLanguage = dbSql.getSetting(message.from_user.id, 'language')
    sent = bot.send_message(message.chat.id, language['fetchingMagnetLink'][userLanguage])
    
    torrentId = message.text[9:]
    torrent = py1337x.py1337x()
    
    response = torrent.info(torrentId, id=True)

    msg = f"✨ <b>{response['name']}</b>\n\n<code>{response['magnetLink']}</code>" if response['magnetLink'] else language['errorFetchingLink'][userLanguage]
    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg)

# Get information about the torrent
@bot.message_handler(func=lambda message: message.text and message.text[:9] == '/getInfo_')
def getInfo(message):
    userLanguage = dbSql.getSetting(message.from_user.id, 'language')
    sent = bot.send_message(message.chat.id, text=language['fetchingTorrentInfo'][userLanguage])
    
    torrentId = message.text[9:]
    torrent = py1337x.py1337x()
    
    response = torrent.info(torrentId, id=True)

    if response['name']:
        genre = '\n\n'+', '.join(response['genre']) if response['genre'] else None
        description = '\n'+response['description'] if genre and response['description'] else '\n\n'+response['description'] if response['description'] else None
        msg = f"<b>✨ {response['name']}</b>\n\n{language['category'][userLanguage]} {response['category']}\n{language['language'][userLanguage]} {response['language']}\n{language['size'][userLanguage]} {response['size']}\n{language['uploadedBy'][userLanguage]} {response['uploader']}\n{language['downloads'][userLanguage]} {response['downloads']}\n{language['lastChecked'][userLanguage]} {response['lastChecked']}\n{language['uploadedOn'][userLanguage]} {response['uploadDate']}\n{language['seeders'][userLanguage]} {response['seeders']}\n{language['leechers'][userLanguage]} {response['leechers']}{'<b>'+genre+'</b>' if genre else ''}{'<code>'+description+'</code>' if description else ''}\n\n{language['link'][userLanguage]} /getLink_{torrentId}"
    else:
        msg = language['errorFetchingInfo'][userLanguage]  
        
    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg)

# Text handler
@bot.message_handler(content_types=['text'])
def text(message):
    userLanguage = dbSql.getSetting(message.from_user.id, 'language')
    # Main menu
    if message.text == language['mainMenuBtn'][userLanguage]:
        bot.send_message(message.chat.id, text=language['backToMenu'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
    
    # Trending torrents
    elif message.text == language['trendingBtn'][userLanguage]:
        browse(message, userLanguage, 'trending')

    # Popular torrents
    elif message.text == language['popularBtn'][userLanguage]:
        browse(message, userLanguage, 'popular')
        
    # Top torrents
    elif message.text == language['topBtn'][userLanguage]:
        browse(message, userLanguage, 'top')
    
    # Browse torrents
    elif message.text == language['browseBtn'][userLanguage]:
        browse(message, userLanguage, 'browse')

    # Settings
    elif message.text in ['/settings', language['settingsBtn'][userLanguage]]:
        settings(message, userLanguage)

    # Help
    elif message.text in ['/help', language['helpBtn'][userLanguage]]:
        bot.send_message(message.chat.id, language['help'][userLanguage].format(language['helpBtn'][userLanguage]))

    # Support
    elif message.text in ['/support', language['supportBtn'][userLanguage]]:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text=language['shareWithFriendsBtn'][userLanguage], url=f"https://t.me/share/url?url=t.me/torrenthuntbot&text={language['shareText'][userLanguage]}"))
        markup.add(telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='t.me/h9youtube'), telebot.types.InlineKeyboardButton(text=language['joinDiscussionBtn'][userLanguage], url='t.me/h9discussion'))
        markup.add(telebot.types.InlineKeyboardButton(text=language['subscribeChannelBtn'][userLanguage], url='https://youtube.com/h9youtube'), telebot.types.InlineKeyboardButton(text=language['followGithubBtn'][userLanguage], url='https://github.com/hemantapkh'))

        bot.send_message(message.from_user.id, language['support'][userLanguage].format(language['supportBtn'][userLanguage]), reply_markup=markup, disable_web_page_preview=True)
    
    # Query search
    else:
        if isSubscribed(message, userLanguage):
            sent = bot.send_message(message.chat.id, language['searchingQuery'][userLanguage].format(message.text))
            torrent = py1337x.py1337x()
            response = torrent.search(message.text)

            msg, markup = result(response, userLanguage, torrentType='query', page=1, query=message.text)

            bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg or language['noResults'][userLanguage], reply_markup=markup)

# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callbackHandler(call):
    userLanguage = dbSql.getSetting(call.from_user.id, 'language')
    # Next page
    if call.data[:11] == 'cb_nextPage':
        splittedData = call.data.split(':', 3)
        page = int(splittedData[1])
        torrentType = splittedData[2].split('-')[0]
        category =  splittedData[2].split('-')[1]
        week =  splittedData[2].split('-')[2]
        query = splittedData[3]

        # Next page for query search
        if torrentType == 'query':
            torrent = py1337x.py1337x()
            response = torrent.search(query, page=page)

            msg, markup = result(response, userLanguage, torrentType, page=page, query=query)

            # 1337x may return empty response sometime. So, changing the case to prevent this.
            if not msg and query.islower():
                response = torrent.search(query.capitalize(), page=page)
                msg, markup = result(response, userLanguage, torrentType, page=page, query=query)
            
            elif not msg:
                response = torrent.search(query.lower(), page=page)
                msg, markup = result(response, userLanguage, torrentType, page=page, query=query)
        
        # Next page for trending and popular torrents
        elif torrentType in ['trending', 'popular']:
            torrent = py1337x.py1337x()
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, week=True if week == 'True' else False)
            
            del response['items'][:(page-1)*20]
            msg, markup = result(response, userLanguage, torrentType, page=page, category=category, query=query)
        
        # Next page for top torrents
        elif torrentType == 'top':
            torrent = py1337x.py1337x()
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category)
            
            del response['items'][:(page-1)*20]
            msg, markup = result(response, userLanguage, torrentType, page=page, category=category)

        # Next page for browse torrents
        else:
            torrent = py1337x.py1337x()
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, page=page)

            msg, markup = result(response, userLanguage, torrentType, page=page, category=category)

        if msg:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=msg, reply_markup=markup)
        # If msg is None
        else:
            bot.answer_callback_query(call.id, text=language['emptyPage'][userLanguage], show_alert=True)
    
    # Check whether a user is subscribed or not after clicking done button
    elif call.data == 'cb_checkSubscription':
        if isSubscribed(call, None, sendMessage=False):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=language['thanksForSub'][userLanguage])
        else:
            bot.answer_callback_query(call.id, language['notSubscribedCallback'][userLanguage])

    # Language settings
    elif call.data[:18] == 'cb_languageSetting':
        lang(call, userLanguage, called=True)

    # Select language
    elif call.data[:12] == 'cb_language_':
        greet = call.data.split('_')[2]
        userLanguage = call.data.split('_')[3]

        dbSql.setSetting(call.from_user.id, 'language', userLanguage)
        
        if greet == 'True':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            bot.send_message(chat_id=call.message.chat.id, text=language['greet'][userLanguage].format(call.from_user.first_name), reply_markup=mainReplyKeyboard(userLanguage))
        
        else:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            bot.send_message(chat_id=call.message.chat.id, text=language['languageSelected'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))

    # Content filter setting
    elif call.data[:17] == 'cb_restrictedMode':
        restrictedMode = 1 if call.data[17:] == 'On' else 0
        dbSql.setSetting(call.from_user.id, 'restrictedMode', restrictedMode)
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=language['restrictedModeOn' if restrictedMode else 'restrictedModeOff'][userLanguage])

    # Back to settings
    elif call.data[:17] == 'cb_backToSettings':
        settings(call, userLanguage, called=True)

# Polling Bot
if config['connectionType'] == 'polling':
    # Remove previous webhook if exists
    bot.remove_webhook()
    bot.polling(none_stop=True)

# Webhook Bot
elif config['connectionType'] == 'webhook':
    # Set webhook
    bot.set_webhook(url=webhookBaseUrl + webhookUrlPath,
                    certificate=open(config['webhookOptions']['sslCertificate'], 'r'))

    # Build ssl context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(config['webhookOptions']['sslCertificate'], config['webhookOptions']['sslPrivatekey'])

    # Start aiohttp server
    web.run_app(
        app,
        host=config['webhookOptions']['webhookListen'],
        port=config['webhookOptions']['webhookPort'],
        ssl_context=context,
    )