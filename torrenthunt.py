import requests
import json, ssl, base64
from pathlib import Path
from os import path, remove
from ast import literal_eval
from time import sleep, time

import telebot, py1337x
from tpblite import TPB
from aiohttp import web
from models import dbQuery

# Finding the absolute path of the config file
scriptPath = path.abspath(__file__)
dirPath = path.dirname(scriptPath)
configPath = path.join(dirPath,'config.json')

config = json.load(open(configPath))
language = json.load(open(config['language']))
dbSql = dbQuery(config['database'])
torrent = py1337x.py1337x(proxy='1337x.to', cache=config['cache'], cacheTime=config['cacheTime'])
pirateBay = TPB()
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

def shortner(url):
    short = requests.get(f'http://tinyurl.com/api-create.php?url={url}')
    return short.text

#: Get suggestion query
def getSuggestions(query):
    headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0'}

    params = (
        ('client', 'Firefox'),
        ('q', query),
    )

    response = requests.get('https://www.google.com/complete/search', headers=headers, params=params)
    
    return literal_eval(response.text)[1]

#: Sort list according to the length of elements
def sortList(lst):
    lst2 = sorted(lst, key=len)
    return lst2

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

    if restrictedMode:
        keyboard.row(button7, button9, button10) if allCategories else keyboard.row(button7, button9)
        keyboard.row(button11)
    
    else:
        keyboard.row(button7, button8, button9)
        keyboard.row(button10, button11) if allCategories else keyboard.row(button11)
   
    return keyboard

# Check if the user is subscribed or not, returns True if subscribed
def isSubscribed(message, userLanguage=None, sendMessage=True):
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
            bot.send_message(message.chat.id, text=language['notSubscribed'][userLanguage], reply_markup=notSubscribedMarkup(userLanguage))
        return False

def notSubscribedMarkup(userLanguage):
    markup = telebot.types.InlineKeyboardMarkup([
            [telebot.types.InlineKeyboardButton(text=language['subscribeChannelBtn'][userLanguage], url='https://www.youtube.com/h9youtube?sub_confirmation=1'),
            telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='https://t.me/h9youtube')]
            ])
    return markup


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
    markup = telebot.types.InlineKeyboardMarkup()
    markup.one_time_keyboard=True
    markup.row_width = 5
    
    msg =''
    if response['items']:
        for count, item in enumerate(response['items']):
            # Show only 20 items per page
            if count >= 20:
                break
            msg += f"<b>{((page-1)*20)+count+1}. {item['name']}</b>\n\n"
            msg += f"💾 {item['size']}, 🟢 {item['seeders']}, 🔴 {item['leechers']}\n\n"

            msg += f"{language['link'][userLanguage]} /getLink_{item['torrentId']}\n"
            msg += f"{language['moreInfo'][userLanguage]} /getInfo_{item['torrentId']}\n\n"

        pageCount = response['pageCount']

        # Trending, popular and top torrents has more than 20 items in the same page
        if torrentType in ['trending', 'popular', 'top']:
            if response['itemCount'] > 20:
                buttons =  []
                for i in range(1, -(-response['itemCount'] // 20)+1):
                    buttons.append(telebot.types.InlineKeyboardButton('🔘' if i == page else i, callback_data=f"cb_nextPage{time()}:{i}:{torrentType}-{category}-{week}:{query or ''}"))

                markup.add(*buttons)

        # For other category, create page according to pageCount
        elif pageCount > 1:
            # FirstPage is the firstPage in a page list. Eg: FirstPage of (1 to 10) is 1, (11 to 20) is 11.
            firstPage = 1
            for i in range(-(-page // 10)-1):
                firstPage += 10
            
            buttons =  []
            for i in range(firstPage, pageCount+1):
                # Show 10 buttons at once
                if len(buttons) >= 10:
                    break
                cb = f"q{str(time())[-3:]}:{i}:{query}" if query else f"cb_nextPage{time()}:{i}:{torrentType}-{category}-{week}:{query or ''}"
                buttons.append(telebot.types.InlineKeyboardButton('🔘' if i == page else i, callback_data=cb))
            
            markup.add(*buttons)
            if pageCount > 10:
                if page <= 10:
                    cb = f"q{str(time())[-3:]}:{firstPage+10}:{query}" if query else f"cb_nextPage{time()}:{firstPage+10}:{torrentType}-{category}-{week}"
                    markup.add(telebot.types.InlineKeyboardButton(language['nextBtn'][userLanguage], callback_data=cb))

                elif 10 < page <= (pageCount - 10):
                    cb1 = f"q{str(time())[-3:]}:{firstPage+10}:{query}" if query else f"cb_nextPage{time()}:{firstPage-10}:{torrentType}-{category}-{week}"
                    cb2 = f"q{str(time())[-3:]}:{firstPage+10}:{query}" if query else f"cb_nextPage{time()}:{firstPage+10}:{torrentType}-{category}-{week}"

                    markup.add(telebot.types.InlineKeyboardButton(language['previousBtn'][userLanguage], callback_data=cb1), telebot.types.InlineKeyboardButton(language['nextBtn'][userLanguage], callback_data=cb2))
                
                else:
                    cb = f"q{str(time())[-3:]}:{firstPage+10}:{query}" if query else f"cb_nextPage{time()}:{firstPage-10}:{torrentType}-{category}-{week}"
                    markup.add(telebot.types.InlineKeyboardButton(language['previousBtn'][userLanguage], callback_data=cb))                      
                        
    if query:
        markup.add(telebot.types.InlineKeyboardButton(text='Pirate Bay 🔎', switch_inline_query_current_chat=f"!pb {query}"), telebot.types.InlineKeyboardButton(text='Nyaa 🔎', switch_inline_query_current_chat=f"!nyaa {query}"))
    elif torrentType == 'top':
        markup.add(telebot.types.InlineKeyboardButton(text='Pirate Bay 🔎', switch_inline_query_current_chat=f"!pb --top"))
    if msg:
        markup.add(telebot.types.InlineKeyboardButton(text='☕ Donate', url='https://buymeacoffee.com/hemantapkh'))
    
    return msg, markup

# Start handler
@bot.message_handler(commands=['start'])
def start(message):
    if dbSql.setAccount(message.from_user.id):
        userLanguage = dbSql.getSetting(message.from_user.id, 'language')
        params = message.text.split()[1] if len(message.text.split()) > 1 else None

        #! If start paramater is passed
        if params:
            try:
                text = base64.b64decode(params.encode('utf')).decode('utf')
                sent = bot.send_message(message.chat.id, language['searchingQuery'][userLanguage].format(text))
                response = torrent.search(text)

                msg, markup = result(response, userLanguage, torrentType='query', page=1, query=text)

                bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg or language['noResults'][userLanguage], reply_markup=markup)
            
            except Exception:
                bot.send_message(message.chat.id, text=language['greet'][userLanguage].format(message.from_user.first_name), reply_markup=mainReplyKeyboard(userLanguage), disable_web_page_preview=True)
        else:
            bot.send_message(message.chat.id, text=language['greet'][userLanguage].format(message.from_user.first_name), reply_markup=mainReplyKeyboard(userLanguage), disable_web_page_preview=True)
    else:
        lang(message, userLanguage='english', greet=True)

# Settings
@bot.message_handler(commands=['settings'])
def settings(message, userLanguage=None, called=False):
    userLanguage = dbSql.getSetting(message.from_user.id, 'language')
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
        bot.send_message(message.chat.id, language['chooseLanguage'][userLanguage], reply_markup=markup)

# Handler for trending, popular, top and browse torrents
def browse(message,userLanguage, torrentType=None, referred=False, customMessage=None):
    #if referred or isSubscribed(message, userLanguage):
    torrentType = torrentType or message.text.split()[0][1:]
    
    sent = bot.send_message(message.chat.id, text=customMessage or language['selectCategory'][userLanguage], reply_markup=categoryReplyKeyboard(userLanguage, allCategories=False if torrentType in ['browse', 'popular'] else True, restrictedMode=dbSql.getSetting(message.from_user.id, 'restrictedMode')))
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
           
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, week=week)

            msg, markup = result(response, userLanguage, torrentType, 1, category, week)
            
            bot.send_message(chat_id=message.chat.id, text=msg or language['emptyPage'][userLanguage], reply_markup=markup)

# Next step handler for top and browse torrents
def browse4(message, userLanguage, torrentType, category):
    bot.send_message(message.chat.id, text=language['fetchingTorrents'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
    
    response =  getattr(torrent, torrentType)(category=None if category == 'all' else category)

    msg, markup = result(response, userLanguage, torrentType, 1, category)

    bot.send_message(chat_id=message.chat.id, text=msg or language['emptyPage'][userLanguage], reply_markup=markup)
    
# Get magnet link of the torrent
@bot.message_handler(func=lambda message: message.text and message.text[:9] == '/getLink_')
def getLink(message):
    userLanguage = dbSql.getSetting(message.from_user.id, 'language')
    sent = bot.send_message(message.chat.id, language['fetchingMagnetLink'][userLanguage])
    
    torrentId = message.text[9:]
    
    response = torrent.info(torrentId=torrentId)
    markup = None

    if response['magnetLink']:
        markup = telebot.types.InlineKeyboardMarkup()
        if dbSql.getSetting(message.from_user.id, 'restrictedMode') and response['category'] == 'XXX':
            msg = language['cantView'][userLanguage]
        else:
            msg = f"✨ <b>{response['name']}</b>\n\n<code>{response['magnetLink']}</code>\n\n<b>🔥via @TorrentHuntBot</b>"

            if response['images']:
                markup.add(telebot.types.InlineKeyboardButton(text=language['imageBtn'][userLanguage], callback_data=f"cb_getImages:{torrentId}"))

            shortUrl = shortner(response['magnetLink'])
            
            markup.add(telebot.types.InlineKeyboardButton(text=language['magnetDownloadBtn'][userLanguage], url=shortUrl), telebot.types.InlineKeyboardButton(text=language['torrentDownloadBtn'][userLanguage], callback_data=f"cb_getTorrent:{response['infoHash']}:{torrentId}"))
            markup.add(telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='t.me/h9youtube'), telebot.types.InlineKeyboardButton(text=language['joinDiscussionBtn'][userLanguage], url='t.me/h9discussion'))
            markup.add(telebot.types.InlineKeyboardButton(text=language['addToSeedr'][userLanguage], url=f't.me/torrentseedrbot?start=addTorrent_{shortUrl[20:]}'))
    else:
        msg = language['errorFetchingLink'][userLanguage]

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg, reply_markup=markup)

# Get information about the torrent
@bot.message_handler(func=lambda message: message.text and message.text[:9] == '/getInfo_')
def getInfo(message):
    userLanguage = dbSql.getSetting(message.from_user.id, 'language')
    sent = bot.send_message(message.chat.id, text=language['fetchingTorrentInfo'][userLanguage])
    
    torrentId = message.text[9:]
    response = torrent.info(torrentId=torrentId)
    markup = None

    if response['name']:
        markup = telebot.types.InlineKeyboardMarkup()
        # Hide if restricted mode is on
        if dbSql.getSetting(message.from_user.id, 'restrictedMode') and response['category'] == 'XXX':
            msg = language['cantView'][userLanguage]
        else:
            genre = '\n\n'+', '.join(response['genre']) if response['genre'] else None
            description = '\n'+response['description'] if genre and response['description'] else '\n\n'+response['description'] if response['description'] else None
            msg = f"<b>✨ {response['name']}</b>\n\n{language['category'][userLanguage]} {response['category']}\n{language['language'][userLanguage]} {response['language']}\n{language['size'][userLanguage]} {response['size']}\n{language['uploadedBy'][userLanguage]} {response['uploader']}\n{language['downloads'][userLanguage]} {response['downloads']}\n{language['lastChecked'][userLanguage]} {response['lastChecked']}\n{language['uploadedOn'][userLanguage]} {response['uploadDate']}\n{language['seeders'][userLanguage]} {response['seeders']}\n{language['leechers'][userLanguage]} {response['leechers']}{'<b>'+genre+'</b>' if genre else ''}{'<code>'+description+'</code>' if description else ''}\n\n{language['link'][userLanguage]} /getLink_{torrentId}\n\n<b>🔥via @TorrentHuntBot</b>"
            
            if response['images']:
                markup.add(telebot.types.InlineKeyboardButton(text=language['imageBtn'][userLanguage], callback_data=f"cb_getImages:{torrentId}"))
    
            shortUrl = shortner(response['magnetLink'])
            
            markup.add(telebot.types.InlineKeyboardButton(text=language['magnetDownloadBtn'][userLanguage], url=shortUrl), telebot.types.InlineKeyboardButton(text=language['torrentDownloadBtn'][userLanguage], callback_data=f"cb_getTorrent:{response['infoHash']}:{torrentId}"))
            markup.add(telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='t.me/h9youtube'), telebot.types.InlineKeyboardButton(text=language['joinDiscussionBtn'][userLanguage], url='t.me/h9discussion'))
            markup.add(telebot.types.InlineKeyboardButton(text=language['addToSeedr'][userLanguage], url=f't.me/torrentseedrbot?start=addTorrent_{shortUrl[20:]}'))
    else:
        msg = language['errorFetchingInfo'][userLanguage]  
        
    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg, reply_markup=markup)

# Broadcast message
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == int(config['adminId']):
        sent = bot.send_message(chat_id=message.chat.id, text='<b>Choose the audience.</b>\n\n/all /bengali /belarusian /catalan /dutch /english /french /german /hindi /italian /korean /malay /nepali /polish /portuguese /russian /spanish /turkish /ukrainian \n\n/cancel to cancel the broadcast.')
        bot.register_next_step_handler(sent, broadcast2)
    else:
        userLanguage = dbSql.getSetting(message.from_user.id, 'language')
        bot.send_message(chat_id=message.chat.id, text=language['noPermission'][userLanguage])
    
def broadcast2(message):
    if message.text == '/cancel':
        bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')
    else:
        if message.text == '/all':
            sent = bot.send_message(chat_id=message.chat.id, text='<b>Choose the audience to exclude from broadcasting.</b>\n\n<code>bengali</code>, <code>belarusian</code>, <code>catalan</code>, <code>dutch</code>, <code>english</code>, <code>french</code>, <code>german</code>, <code>hindi</code>, <code>italian</code>, <code>korean</code>, <code>malay</code>, <code>nepali</code>, <code>polish</code>, <code>portuguese</code>, <code>russian</code>, <code>spanish</code>, <code>turkish</code>, <code>ukrainian</code> \n\n<b>Separate by comma for multiple exclusion.</b>\n\n/cancel to cancel the broadcast.\n/skip to Skip the exclusion.')
            bot.register_next_step_handler(sent, broadcastExclusion)
        
        elif message.text in ['/bengali', '/belarusian', '/catalan', '/dutch', '/english', '/french', '/german', '/hindi', '/italian', '/korean', '/malay', '/nepali', '/polish', '/portuguese', '/russian', '/spanish', '/turkish', '/ukrainian']:
            audience = message.text[1:]
            sent = bot.send_message(chat_id=message.chat.id, text='<b>Send the message to broadcast.</b>\n\nMarkup: HTML\nTags allowed: a href, b, i, u, s, code, pre, h1, inv, br\n\n/cancel to cancel the broadcast.')
            bot.register_next_step_handler(sent, broadcast3, audience)
        
        else:
            bot.send_message(chat_id=message.chat.id, text='❌ Unknown audience. Broadcast cancelled.')

def broadcastExclusion(message):
    if message.text == '/skip':
        sent = bot.send_message(chat_id=message.chat.id, text='<b>Send the message to broadcast.</b>\n\nMarkup: HTML\nTags allowed: a href, b, i, u, s, code, pre, h1, inv, br\n\n/cancel to cancel the broadcast.')
        bot.register_next_step_handler(sent, broadcast3, audience='all', exclude=None)
    
    elif message.text == '/cancel':
        bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')
    
    else:
        sent = bot.send_message(chat_id=message.chat.id, text='<b>Send the message to broadcast.</b>\n\nMarkup: HTML\nTags allowed: a href, b, i, u, s, code, pre, h1, inv, br\n\n/cancel to cancel the broadcast.')
        exclude = [x.strip() for x in message.text.split(',')]
        bot.register_next_step_handler(sent, broadcast3, audience='all', exclude=exclude)

def broadcast3(message, audience, exclude=None):
    if message.text != '/cancel':
        sent2 = bot.send_message(chat_id=message.chat.id, text='<b>To send embed button, send the link in the following format.</b>\n\n<code>Text1 -> URL1\nText2 -> URL2</code>\n\n/cancel to cancel the broadcast.\n/skip to skip the buttons.')
        bot.register_next_step_handler(sent2, broadcast4, audience, exclude, message.text)
    else:
        bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')
    
def broadcast4(message, audience, exclude, textMessage):
    markup = telebot.types.InlineKeyboardMarkup()
    if message.text == '/cancel':
        bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')
    
    elif message.text == '/skip':
        if audience == 'all':
            if exclude:
                users = dbSql.getUsersExcept(exclude)
            else:
                users = dbSql.getAllUsers()
        else:
            users = dbSql.getUsers(audience)
        
        users = len(users) if users else 0
        
        try:
            bot.send_message(message.chat.id, text=f'<b>Message Preview</b>\n\n{textMessage}',)
            sent = bot.send_message(message.chat.id, text=f"/send to broadcast this message.\n\nTarget Audience: {audience}\nExcluded Audience: {' '.join(exclude) if exclude else None}\nTotal audience: {users}")
            bot.register_next_step_handler(sent, broadcast5, audience, exclude, textMessage, markup=None)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id, text=f"<b>⚠️ Error</b>\n\n{str(e).replace('<','')}")

    else:
        if audience == 'all':
            if exclude:
                users = dbSql.getUsersExcept(exclude)
            else:
                users = dbSql.getAllUsers()
        else:
            users = dbSql.getUsers(audience)
        
        users = len(users) if users else 0

        try:
            for i in message.text.split('\n'):
                markup.add(telebot.types.InlineKeyboardButton(text=i.split('->')[0].strip(), url=i.split('->')[1].strip()))
        
            bot.send_message(message.chat.id, text=f'<b>Message Preview</b>\n\n{textMessage}', reply_markup=markup)
            sent = bot.send_message(message.chat.id, text=f"/send to broadcast this message.\n\nTarget Audience: {audience}\nExcluded Audience: {' '.join(exclude) if exclude else None}\nTotal audience: {users}")
            bot.register_next_step_handler(sent, broadcast5, audience, exclude, textMessage, markup)
        
        except Exception as e:
            bot.send_message(message.chat.id, text=f"<b>⚠️ Error</b>\n\n{str(e).replace('<','')}")

def broadcast5(message, audience, exclude, textMessage, markup):
    if message.text == '/send':
        sent = bot.send_message(chat_id=message.chat.id, text='<code>Broadcasting message</code>')
        if audience == 'all':
            if exclude:
                users = dbSql.getUsersExcept(exclude)
            else:
                users = dbSql.getAllUsers()
        else:
            users = dbSql.getUsers(audience)
        failure = 0
        success = 0
        updateCount = 0

        if users:
            for userId in users:
                try:
                    bot.send_message(chat_id=userId, text=textMessage, reply_markup=markup)
                    success += 1
                    updateCount += 1
                
                except Exception:
                    failure += 1
                    updateCount += 1

                finally:
                    sleep(0.1)
                    if updateCount == 15:
                        updateCount = 0
                        bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=f'<code>{failure+success} out of {len(users)} complete.</code>')

            bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=f'<b>✈️ Broadcast Report</b>\n\nSuccess: {success}\nFailure: {failure}')
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=f'❌ No user to broadcast message.')
    else:
        bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')

# Stats
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == int(config['adminId']):
        languageSet = ["english", "nepali", "bengali", "belarusian", "catalan", "dutch",  "french",  "german", "hindi", "italian", "korean", "malay", "polish", "portuguese", "russian", "spanish", "turkish", "ukrainian"]
        
        msg = f'<b>📊 Statistics</b>\n\n'
        
        languageStats = {}
        for i in languageSet:
            languageStats[i.capitalize()] = len(dbSql.getUsers(i)) if dbSql.getUsers(i) else 0

        languageStats = {k: v for k, v in sorted(languageStats.items(), key=lambda item: item[1], reverse=True)}

        for i in languageStats:
            msg += f'{i}: {languageStats[i]}\n'

        msg += f'\n<b>Total users: {len(dbSql.getAllUsers()) if dbSql.getAllUsers() else 0}</b>'
        bot.send_message(chat_id=message.chat.id, text=msg)

    else:
        userLanguage = dbSql.getSetting(message.from_user.id, 'language')
        bot.send_message(chat_id=message.chat.id, text=language['noPermission'][userLanguage])

# Text handler
@bot.message_handler(content_types=['text'])
def text(message):
    userLanguage = dbSql.getSetting(message.from_user.id, 'language')

    # Don't search if the message is via bot
    if 'via_bot' in message.json.keys() and message.json['via_bot']['id'] == 1700458114:
        pass
    
    # Main menu
    elif message.text == language['mainMenuBtn'][userLanguage]:
        bot.send_message(message.chat.id, text=language['backToMenu'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
    
    # Trending torrents
    elif message.text in ['/trending', language['trendingBtn'][userLanguage]]:
        browse(message, userLanguage, 'trending')

    # Popular torrents
    elif message.text in ['/popular', language['popularBtn'][userLanguage]]:
        browse(message, userLanguage, 'popular')
        
    # Top torrents
    elif message.text in ['/top', language['topBtn'][userLanguage]]:
        browse(message, userLanguage, 'top')
    
    # Browse torrents
    elif message.text in ['/browse', language['browseBtn'][userLanguage]]:
        browse(message, userLanguage, 'browse')

    # Settings
    elif message.text in ['/settings', language['settingsBtn'][userLanguage]]:
        settings(message, userLanguage)

    # Help
    elif message.text in ['/help', language['helpBtn'][userLanguage]]:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text=language['inlineSearchBtn'][userLanguage], switch_inline_query_current_chat=""))
        bot.send_message(message.chat.id, language['help'][userLanguage].format(language['helpBtn'][userLanguage]), reply_markup=markup)

    # Support
    elif message.text in ['/support', language['supportBtn'][userLanguage]]:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text=language['shareWithFriendsBtn'][userLanguage], url=f"https://t.me/share/url?url=t.me/torrenthuntbot&text={language['shareText'][userLanguage]}"))
        markup.add(telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='t.me/h9youtube'), telebot.types.InlineKeyboardButton(text=language['joinDiscussionBtn'][userLanguage], url='t.me/h9discussion'))
        markup.add(telebot.types.InlineKeyboardButton(text=language['subscribeChannelBtn'][userLanguage], url='https://youtube.com/h9youtube'), telebot.types.InlineKeyboardButton(text=language['followGithubBtn'][userLanguage], url='https://github.com/hemantapkh'))

        bot.send_message(message.from_user.id, language['support'][userLanguage].format(language['supportBtn'][userLanguage]), reply_markup=markup, disable_web_page_preview=True)
    
    # Query search
    else:
        #if isSubscribed(message, userLanguage):
        sent = bot.send_message(message.chat.id, language['searchingQuery'][userLanguage].format(message.text))
        response = torrent.search(message.text)

        msg, markup = result(response, userLanguage, torrentType='query', page=1, query=message.text)
        
        if not msg:
            try:
                suggestion = getSuggestions(message.text)
                
                if suggestion:
                    if suggestion[0] != message.text:
                        bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['searchingQuery'][userLanguage].format(suggestion[0]))
                        response = torrent.search(suggestion[0])
                        
                        msg, markup = result(response, userLanguage, torrentType='query', page=1, query=suggestion[0])

                    if not msg:
                        markup.row_width = 3
                        suggestion = sortList(suggestion)
                        buttons = []
                        smallButtons = []
                        
                        for i in suggestion[1:]:
                            suggestedQuery = base64.b64encode(i.encode()).decode()
                            if len(suggestedQuery) <= 64:

                                if len(i) < 13:
                                    smallButtons.append(telebot.types.InlineKeyboardButton(text=i, url=f"https://t.me/torrenthuntbot?start={suggestedQuery}"))
                                
                                elif len(i) < 18:
                                    buttons.append(telebot.types.InlineKeyboardButton(text=i, url=f"https://t.me/torrenthuntbot?start={suggestedQuery}"))
                                
                                else:
                                    markup.add(telebot.types.InlineKeyboardButton(text=i, url=f"https://t.me/torrenthuntbot?start={suggestedQuery}"))

                        
                        markup.add(*smallButtons)
                        markup.row_width = 2
                        markup.add(*buttons)
                        
                    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg or language['noResults'][userLanguage], reply_markup=markup)
                
                else:
                    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=language['noResults'][userLanguage], reply_markup=markup)
            
            except Exception as e:
                bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg, reply_markup=markup)
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg, reply_markup=markup)

# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callbackHandler(call):
    userLanguage = dbSql.getSetting(call.from_user.id, 'language')
    # Next page for query 
    if call.data[:1] == 'q':
        splittedData = call.data.split(':', 2)
        page = int(splittedData[1])
        query = splittedData[2]
        torrentType = None

        response = torrent.search(query, page=page)

        msg, markup = result(response, userLanguage, torrentType, page=page, query=query)

        # 1337x may return empty response sometime. So, changing the case to prevent this.
        if not msg and query.islower():
            response = torrent.search(query.capitalize(), page=page)
            msg, markup = result(response, userLanguage, torrentType, page=page, query=query)
        
        elif not msg:
            response = torrent.search(query.lower(), page=page)
            msg, markup = result(response, userLanguage, torrentType, page=page, query=query)

        if msg:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=msg, reply_markup=markup)
        # If msg is None
        else:
            bot.answer_callback_query(call.id, text=language['emptyPage'][userLanguage], show_alert=True)

    # Next page
    if call.data[:11] == 'cb_nextPage':
        splittedData = call.data.split(':', 2)
        page = int(splittedData[1])
        torrentType = splittedData[2].split('-')[0]
        category =  splittedData[2].split('-')[1]
        week =  splittedData[2].split('-')[2]
        
        # Next page for trending and popular torrents
        if torrentType in ['trending', 'popular']:
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, week=True if week == 'True' else False)
            
            del response['items'][:(page-1)*20]
            msg, markup = result(response, userLanguage, torrentType, page=page, category=category)
        
        # Next page for top torrents
        elif torrentType == 'top':
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category)
            
            del response['items'][:(page-1)*20]
            msg, markup = result(response, userLanguage, torrentType, page=page, category=category)

        # Next page for browse torrents
        else:
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

    # Download .Torrent file
    elif call.data[:14] == 'cb_getTorrent:':
        infoHash = call.data.split(':')[1]
        torrentId = call.data.split(':')[2]

        headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'}
        response = requests.get(f'http://itorrents.org/torrent/{infoHash}.torrent', headers=headers)
        
        if response.ok and not response.content.startswith(b'<!DOCTYPE html PUBLIC'):
            bot.answer_callback_query(call.id)
            bot.send_chat_action(call.message.chat.id, 'upload_document')
            torrentInfo = torrent.info(torrentId=torrentId)

            # -- Writing the file and sending it because telegram don't let change the file name. ToDo: Change this method--
            # Create temp directory if not exists
            Path(f"/TorrentHuntTmp/{call.from_user.id}").mkdir(parents=True, exist_ok=True)

            open(f"/TorrentHuntTmp/{call.from_user.id}/{torrentInfo['infoHash']}.torrent", 'wb').write(response.content)
            thumbnail = requests.get(torrentInfo['thumbnail']) if torrentInfo['thumbnail'] else None
            
            data = open(f"/TorrentHuntTmp/{call.from_user.id}/{torrentInfo['infoHash']}.torrent", 'rb')

            # Deleting the file
            remove(f"/TorrentHuntTmp/{call.from_user.id}/{torrentInfo['infoHash']}.torrent")

            bot.send_document(call.message.chat.id, data=data, caption=f"{torrentInfo['name']}\n\n{language['size'][userLanguage]}{torrentInfo['size']}\n{language['seeders'][userLanguage]}{torrentInfo['seeders']}\n{language['leechers'][userLanguage]}{torrentInfo['leechers']}\n\n<b>🔥via @TorrentHuntBot</b>", thumb=thumbnail.content if thumbnail else None)
        
        # Torrent file not found in itorrents
        else:
            bot.answer_callback_query(call.id, text=language['fileNotFound'][userLanguage], show_alert=True)

    elif call.data[:13] == 'cb_getImages:':
        bot.answer_callback_query(call.id)
        bot.send_chat_action(call.message.chat.id, 'upload_photo')
        torrentId = call.data[13:]
        response = torrent.info(torrentId=torrentId)
        media = []
        
        try:
            if len(response['images']) >= 2:
                for image in response['images']:
                    media.append(telebot.types.InputMediaPhoto(image.replace('.th.','.'), caption=f"✨ {response['name']}\n\n{language['moreInfo'][userLanguage]} /getLink_{torrentId}\n{language['link'][userLanguage]} /getLink_{torrentId}\n\n🔥 via @TorrentHuntBot"))
                    if len(media) > 6:
                        bot.send_media_group(call.message.chat.id, media)
                        media = []
                
                if media:
                    bot.send_media_group(call.message.chat.id, media)
            else:
                bot.send_photo(call.message.chat.id, photo=response['images'][0].replace('.th.','.'), caption=f"✨ {response['name']}\n\n{language['moreInfo'][userLanguage]} /getLink_{torrentId}\n{language['link'][userLanguage]} /getLink_{torrentId}\n\n🔥 via @TorrentHuntBot")
        
        except Exception as e:
            bot.send_message(call.message.chat.id, language['errorSendingImage'][userLanguage])

# Inline query
@bot.inline_handler(lambda query: len(query.query) >= 1)
def query_text(inline_query):
    userLanguage = dbSql.getSetting(inline_query.from_user.id, 'language')
    if isSubscribed(inline_query, sendMessage=False):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='☕ Donate', url='https://buymeacoffee.com/hemantapkh'))
        if inline_query.query[:3] == '!pb':
            page = int(inline_query.offset) if inline_query.offset else 1
            
            # Top torrents of all category
            if inline_query.query == '!pb --top':
                results = pirateBay.top()[(page-1)*30:]
            
            # -- Error in tpblite package ---
            # Top torrents of all category
            # elif inline_query.query == '!pb --top-48hrs':
            #     results = pirateBay.top(last_48=True)
            
            # Query search
            else:
                results = pirateBay.search(inline_query.query[4:], page)

                if results or page > 1:
                    queryResult = []
                    for count, item in enumerate(results):
                        if count >= 30:
                            break
                        queryResult.append(telebot.types.InlineQueryResultArticle(id=count, title=item.title, url=item.url, hide_url=True, thumb_url='https://raw.githubusercontent.com/hemantapkh/TorrentHunt/main/images/pirateBay.jpg', thumb_width='123', thumb_height='182', description=f"{'[TRUSTED] ' if item.is_trusted else ''}{'[VIP] ' if item.is_vip else ''}{item.filesize} size {item.seeds} seeders {item.leeches} leechers", input_message_content=telebot.types.InputTextMessageContent(queryMessageContent(userId=inline_query.from_user.id, torrentz=item, source='tpb'), parse_mode='HTML'),reply_markup=markup))
                    
                    bot.answer_inline_query(inline_query.id, queryResult, next_offset=page+1 if len(results) else None, is_personal=True)
                
                else:
                    bot.answer_inline_query(inline_query.id, [telebot.types.InlineQueryResultArticle(id=0, title=language['noResults'][userLanguage], url='https://t.me/h9youtube', hide_url=True, thumb_url='https://image.freepik.com/free-vector/error-404-found-glitch-effect_8024-4.jpg', input_message_content=telebot.types.InputTextMessageContent(language['noResults'][userLanguage], parse_mode='HTML'))], is_personal=True)
        
        elif inline_query.query[:5] == '!nyaa':
            page = int(inline_query.offset) if inline_query.offset else 0
            results = literal_eval(requests.get('https://api.api-zero.workers.dev/nyaasi/'+inline_query.query[6:]).text)

            if 'error' not in results:
                results = results[page*50:(page+1)*50]
                queryResult = []
                for count, item in enumerate(results):
                    queryResult.append(telebot.types.InlineQueryResultArticle(id=count, title=item['Name'], url=item['Url'], hide_url=True, thumb_url='https://i.pinimg.com/736x/2d/8d/5c/2d8d5c5e953fd50493e388da2759ac41.jpg', thumb_width='123', thumb_height='182', description=f"{item['Size']} size {item['Seeder']} seeders {item['Leecher']} leechers", input_message_content=telebot.types.InputTextMessageContent(queryMessageContent(userId=inline_query.from_user.id, torrentz=item, source='nyaa'), parse_mode='HTML'), reply_markup=markup))
                    
                bot.answer_inline_query(inline_query.id, queryResult, next_offset=page+1 if len(results) else None, is_personal=True, cache_time=0)
                
            else:
                bot.answer_inline_query(inline_query.id, [telebot.types.InlineQueryResultArticle(id=0, title=language['noResults'][userLanguage], url='https://t.me/h9youtube', hide_url=True, thumb_url='https://image.freepik.com/free-vector/error-404-found-glitch-effect_8024-4.jpg', input_message_content=telebot.types.InputTextMessageContent(language['noResults'][userLanguage], parse_mode='HTML'))], is_personal=True)

        else:
            offset = int(inline_query.offset.split(':')[0]) if inline_query.offset else 0
            page = int(inline_query.offset.split(':')[1]) if inline_query.offset else 1

            results = torrent.search(inline_query.query, page)

            if results['itemCount'] or page > 1:
                pageCount = results['pageCount']

                queryResult = []
                for count, item in enumerate(results['items'][offset:]):
                    if count >= 5:
                        break
                    info = torrent.info(link=item['link'])
                    queryResult.append(telebot.types.InlineQueryResultArticle(id=count, title=item['name'], url=item['link'], hide_url=True, thumb_url=info['thumbnail'] or 'https://raw.githubusercontent.com/hemantapkh/TorrentHunt/main/images/TorrentHunt.jpg', thumb_width='123', thumb_height='182', description=f"{item['size']} size {item['seeders']} seeders {item['leechers']} leechers", input_message_content=telebot.types.InputTextMessageContent(queryMessageContent(userId=inline_query.from_user.id, torrentz=item['torrentId'], source='1337x'), parse_mode='HTML'), reply_markup=markup))
                
                nextOffset = offset + 5 if offset < 20 else 0
                nextPage = page+1 if nextOffset == 20 else page
                nextOffset = 0 if nextOffset == 20 else nextOffset

                bot.answer_inline_query(inline_query.id, queryResult, next_offset=None if (nextPage == pageCount and nextOffset == 15) else f'{nextOffset}:{nextPage}', is_personal=True)
            
            else:
                bot.answer_inline_query(inline_query.id, [telebot.types.InlineQueryResultArticle(id=0, title=language['noResults'][userLanguage], url='https://t.me/h9youtube', hide_url=True, thumb_url='https://image.freepik.com/free-vector/error-404-found-glitch-effect_8024-4.jpg', input_message_content=telebot.types.InputTextMessageContent(language['noResults'][userLanguage], parse_mode='HTML'))], is_personal=True)
    else:
        reply = telebot.types.InlineQueryResultArticle(id=1, title=language['notSubscribedCallback'][userLanguage], description=language['clickForMoreDetails'][userLanguage], thumb_url='https://raw.githubusercontent.com/hemantapkh/TorrentHunt/main/images/H9Logo.jpg', input_message_content=telebot.types.InputTextMessageContent(language['notSubscribed'][userLanguage], parse_mode='HTML'), reply_markup=notSubscribedMarkup(userLanguage))
        bot.answer_inline_query(inline_query.id, [reply], is_personal=True, cache_time=0)
     
def queryMessageContent(userId, torrentz, source):
    userLanguage = dbSql.getSetting(userId, 'language')
    if source == '1337x':
        response = torrent.info(torrentId=torrentz)
        if dbSql.getSetting(userId, 'restrictedMode') and response['category'] == 'XXX':
                msg = language['cantView'][userLanguage]
        else:
            genre = '\n\n'+', '.join(response['genre']) if response['genre'] else None
            description = '\n'+response['description'] if genre and response['description'] else '\n\n'+response['description'] if response['description'] else None
            msg = f"<b>✨ {response['name']}</b>\n\n{language['category'][userLanguage]}{response['category']}\n{language['language'][userLanguage]}{response['language']}\n{language['size'][userLanguage]}{response['size']}\n{language['uploadedBy'][userLanguage]}{response['uploader']}\n{language['downloads'][userLanguage]}{response['downloads']}\n{language['lastChecked'][userLanguage]}{response['lastChecked']}\n{language['uploadedOn'][userLanguage]}{response['uploadDate']}\n{language['seeders'][userLanguage]}{response['seeders']}\n{language['leechers'][userLanguage]}{response['leechers']}{'<b>'+genre+'</b>' if genre else ''}{'<code>'+description+'</code>' if description else ''}\n\n<b>Magnet Link: </b><code>{response['magnetLink']}</code>"
    
    elif source == 'tpb':
        msg = f"<b>✨ {torrentz.title}</b>\n\n{language['size'][userLanguage]}{torrentz.filesize}\n{language['seeders'][userLanguage]}{torrentz.seeds}\n{language['leechers'][userLanguage]}{torrentz.leeches}\n{language['uploadedBy'][userLanguage]}{torrentz.uploader}\n{language['uploadedOn'][userLanguage]}{torrentz.upload_date}\n\n<b>Magnet Link: </b><code>{torrentz.magnetlink}</code>"

    elif source ==  'nyaa':
        msg = f"<b>✨ {torrentz['Name']}</b>\n\n{language['size'][userLanguage]}{torrentz['Size']}\n{language['seeders'][userLanguage]}{torrentz['Seeder']}\n{language['leechers'][userLanguage]}{torrentz['Leecher']}\n{language['uploadedOn'][userLanguage]}{torrentz['Date']}\n\n<b>Magnet Link: </b><code>{torrentz['Magnet']}</code>"

    return msg

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
