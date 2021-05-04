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
def mainReplyKeyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    button1 = telebot.types.KeyboardButton(text=language['trendingBtn']['en'])
    button2 = telebot.types.KeyboardButton(text=language['popularBtn']['en'])
    button3 = telebot.types.KeyboardButton(text=language['topBtn']['en'])
    button4 = telebot.types.KeyboardButton(text=language['browseBtn']['en'])
    button5 = telebot.types.KeyboardButton(text=language['settingsBtn']['en'])
    button6 = telebot.types.KeyboardButton(text=language['helpBtn']['en'])
    button7 = telebot.types.KeyboardButton(text=language['supportBtn']['en'])
    
    keyboard.row(button1, button2)
    keyboard.row(button3, button4)
    keyboard.row(button5, button6, button7)

    return keyboard

# Category reply keyboard
def categoryReplyKeyboard(allCategories=True):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = telebot.types.KeyboardButton(text=language['moviesBtn']['en'])
    button2 = telebot.types.KeyboardButton(text=language['tvBtn']['en'])
    button3 = telebot.types.KeyboardButton(text=language['docsBtn']['en'])
    button4 = telebot.types.KeyboardButton(text=language['gamesBtn']['en'])
    button5 = telebot.types.KeyboardButton(text=language['musicBtn']['en'])
    button6 = telebot.types.KeyboardButton(text=language['appsBtn']['en'])
    button7 = telebot.types.KeyboardButton(text=language['animeBtn']['en'])
    button8 = telebot.types.KeyboardButton(text=language['xxxBtn']['en'])
    button9 = telebot.types.KeyboardButton(text=language['othersBtn']['en'])
    button10 = telebot.types.KeyboardButton(text=language['allBtn']['en'])
    button11 = telebot.types.KeyboardButton(text=language['mainMenuBtn']['en'])

    keyboard.row(button1, button2, button3)
    keyboard.row(button4, button5, button6)
    keyboard.row(button7, button8, button9)
   
    keyboard.row(button10, button11) if allCategories else keyboard.row(button11)

    return keyboard

# Check if the user is subscribed or not, returns True if subscribed
def isSubscribed(message, sendMessage=True):
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
            bot.send_message(message.chat.id, text=language['notSubscribed']['en'].format(message.from_user.first_name), reply_markup=telebot.types.InlineKeyboardMarkup([
            [telebot.types.InlineKeyboardButton(text=language['subscribeChannelBtn']['en'], url='https://www.youtube.com/h9youtube?sub_confirmation=1'),
            telebot.types.InlineKeyboardButton(text=language['joinChannelBtn']['en'], url='https://t.me/h9youtube')],
            [telebot.types.InlineKeyboardButton(text=language['doneBtn']['en'], callback_data='cb_checkSubscription')]
            ]))

        return False

# Returns the equivalent category of the text 
def textToCategory(text):
    if text == language['moviesBtn']['en']:
        return 'movies'
    
    elif text == language['tvBtn']['en']:
        return 'tv'

    elif text == language['docsBtn']['en']:
        return 'documentries'

    elif text == language['gamesBtn']['en']:
        return 'games'

    elif text == language['musicBtn']['en']:
        return 'music'

    elif text == language['appsBtn']['en']:
        return 'apps'

    elif text == language['animeBtn']['en']:
        return 'anime'

    elif text == language['xxxBtn']['en']:
        return 'xxx'

    elif text == language['othersBtn']['en']:
        return 'other'

    elif text == language['allBtn']['en']:
        return 'all'

    else:
        return None

# Parse the torrent result
def result(response, torrentType, page, category=None, week=None, query=None):
    if response['items']:
            msg = ''
            for count, item in enumerate(response['items']):
                # Show only 20 items per page
                if count >= 20:
                    break
                msg += f"<b>{((page-1)*20)+count+1}. {item['name']}</b>\n\n"
                msg += f"💾 {item['size']}, 🟢 {item['seeders']}, 🔴 {item['leechers']}\n\n"

                msg += f"{language['link']['en']}: /getLink_{item['id']}\n"
                msg += f"{language['moreInfo']['en']}: /getInfo_{item['id']}\n\n"

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
                        markup.add(telebot.types.InlineKeyboardButton(language['nextBtn']['en'], callback_data=f"cb_nextPage{time()}:{firstPage+10}:{torrentType}-{category}-{week}:{query or ''}"))

                    elif 10 < page <= (pageCount - 10):
                        markup.add(telebot.types.InlineKeyboardButton(language['previousBtn']['en'], callback_data=f"cb_nextPage{time()}:{firstPage-10}:{torrentType}-{category}-{week}:{query or ''}"), telebot.types.InlineKeyboardButton(language['nextBtn']['en'], callback_data=f"cb_nextPage{time()}:{firstPage+10}:{torrentType}-{category}-{week}:{query or ''}"))
                    
                    else:
                        markup.add(telebot.types.InlineKeyboardButton(language['previousBtn']['en'], callback_data=f"cb_nextPage{time()}:{firstPage-10}:{torrentType}-{category}-{week}:{query or ''}"))                      
            
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
    dbSql.setAccount(message.from_user.id)
    bot.send_message(message.chat.id, text=language['greet']['en'].format(message.from_user.first_name), reply_markup=mainReplyKeyboard(), disable_web_page_preview=True)

# Handler for trending, popular, top and browse torrents
@bot.message_handler(commands=['trending', 'popular', 'top', 'browse'])
def browse(message, torrentType=None):
    if isSubscribed(message):
        torrentType = torrentType or message.text.split()[0][1:]
        sent = bot.send_message(message.chat.id, text=language['selectCategory']['en'], reply_markup=categoryReplyKeyboard(allCategories=False if torrentType == 'browse' else True))
        bot.register_next_step_handler(sent, browse2, torrentType)

# Next step handler for trending, popular, top and browse torrents
def browse2(message, torrentType, category=None):
    # Main menu
    if message.text == language['mainMenuBtn']['en']:
        bot.send_message(message.chat.id, text=language['backToMenu']['en'], reply_markup=mainReplyKeyboard())
    else:
        category = category or textToCategory(message.text)
        if category:
            # Send time keyboard if trending and popular torrents
            if torrentType in ['trending', 'popular']:
                keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

                button1 = telebot.types.KeyboardButton(text=f"{'✨' if torrentType == 'trending' else '⚡️'} {language['timeCategory']['en'].format(torrentType=language[torrentType]['en'].capitalize(), category='' if category in ['all', 'other'] else language[category]['en'], time=language['today']['en'])}")
                button2 = telebot.types.KeyboardButton(text=f"{'✨' if torrentType == 'trending' else '⚡️'} {language['timeCategory']['en'].format(torrentType=language[torrentType]['en'].capitalize(), category='' if category in ['all', 'other'] else language[category]['en'], time=language['week']['en'])}")
                button3 = telebot.types.KeyboardButton(text=language['backBtn']['en'])
                button4 = telebot.types.KeyboardButton(text=language['mainMenuBtn']['en'])

                keyboard.row(button1)
                keyboard.row(button2)
                keyboard.row(button3, button4)

                sent = bot.send_message(message.chat.id, text=language['selectTime']['en'], reply_markup=keyboard)
                bot.register_next_step_handler(sent, browse3, torrentType, category)
            else:
                browse4(message, torrentType, category)
        else:
            browse(message, torrentType)

# Next step handler for trending and popular torrents
def browse3(message, torrentType, category):
    # Main menu
    if message.text == language['mainMenuBtn']['en']:
        bot.send_message(message.chat.id, text=language['backToMenu']['en'], reply_markup=mainReplyKeyboard())
    # Back
    elif message.text == language['backBtn']['en']:
        browse2(message, torrentType)
    else:
        if message.text[2 if torrentType == 'trending' else 3:] == language['timeCategory']['en'].format(torrentType=language[torrentType]['en'].capitalize(), category='' if category in ['all', 'other'] else language[category]['en'], time=language['today']['en']):
            week = False
        elif message.text[2 if torrentType == 'trending' else 3:] == language['timeCategory']['en'].format(torrentType=language[torrentType]['en'].capitalize(), category='' if category in ['all', 'other'] else language[category]['en'], time=language['week']['en']):
            week = True
        else:
            week = 'unknown'
        
        # If week is unknown, return to browse2
        if week == 'unknown':
            browse2(message, torrentType, category)
        
        else:
            bot.send_message(message.chat.id, text=language['fetchingTorrentTime']['en'].format(torrentType=language[torrentType]['en'], category=language['torrents']['en'] if category in ['all', 'other'] else language[category]['en'], time=language['week']['en'] if week else language['today']['en']), reply_markup=mainReplyKeyboard())

            torrent = py1337x.py1337x()
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, week=week)

            msg, markup = result(response, torrentType, 1, category, week)
            
            bot.send_message(chat_id=message.chat.id, text=msg or language['emptyPage']['en'], reply_markup=markup)

# Next step handler for top and browse torrents
def browse4(message, torrentType, category):
    bot.send_message(message.chat.id, text=language['fetchingTorrent' if torrentType == 'top' else 'fetchingTorrentBrowse']['en'].format(torrentType='' if torrentType == 'browse' else language['top']['en'], category=language['torrents']['en'] if category in ['all', 'other'] else language[category]['en']), reply_markup=mainReplyKeyboard())
    
    torrent = py1337x.py1337x()
    response =  getattr(torrent, torrentType)(category=None if category == 'all' else category)

    msg, markup = result(response, torrentType, 1, category)

    bot.send_message(chat_id=message.chat.id, text=msg or language['emptyPage']['en'], reply_markup=markup)
    
# Get magnet link of the torrent
@bot.message_handler(func=lambda message: message.text and message.text[:9] == '/getLink_')
def getLink(message):
    sent = bot.send_message(message.chat.id, language['fetchingMagnetLink']['en'])
    
    torrentId = message.text[9:]
    torrent = py1337x.py1337x()
    
    response = torrent.info(torrentId, id=True)

    msg = f"✨ <b>{response['name']}</b>\n\n<code>{response['magnetLink']}</code>" if response['magnetLink'] else language['errorFetchingLink']['en']
    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg)

# Get information about the torrent
@bot.message_handler(func=lambda message: message.text and message.text[:9] == '/getInfo_')
def getInfo(message):
    sent = bot.send_message(message.chat.id, text=language['fetchingTorrentInfo']['en'])
    
    torrentId = message.text[9:]
    torrent = py1337x.py1337x()
    
    response = torrent.info(torrentId, id=True)

    if response['name']:
        genre = '\n\n'+', '.join(response['genre']) if response['genre'] else None
        description = '\n'+response['description'] if genre and response['description'] else '\n\n'+response['description'] if response['description'] else None
        msg = f"<b>✨ {response['name']}</b>\n\n{language['category']['en']}: {response['category']}\n{language['language']['en']}: {response['language']}\n{language['size']['en']}: {response['size']}\n{language['uploadedBy']['en']}: {response['uploader']}\n{language['downloads']['en']}: {response['downloads']}\n{language['lastChecked']['en']}: {response['lastChecked']}\n{language['uploadedOn']['en']}: {response['uploadDate']}\n{language['seeders']['en']}: {response['seeders']}\n{language['leechers']['en']}: {response['leechers']}{'<b>'+genre+'</b>' if genre else ''}{'<code>'+description+'</code>' if description else ''}\n\n{language['link']['en']}: /getLink_{torrentId}"
    else:
        msg = language['errorFetchingInfo']['en']  
        
    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg)

# Text handler
@bot.message_handler(content_types=['text'])
def text(message):
    # Main menu
    if message.text == language['mainMenuBtn']['en']:
        bot.send_message(message.chat.id, text=language['backToMenu']['en'], reply_markup=mainReplyKeyboard())
    
    # Trending torrents
    elif message.text == language['trendingBtn']['en']:
        browse(message, 'trending')

    # Popular torrents
    elif message.text == language['popularBtn']['en']:
        browse(message, 'popular')
        
    # Top torrents
    elif message.text == language['topBtn']['en']:
        browse(message, 'top')
    
    # Browse torrents
    elif message.text == language['browseBtn']['en']:
        browse(message, 'browse')

    # Settings
    elif message.text in ['/settings', language['settingsBtn']['en']]:
        pass

    # Help
    elif message.text in ['/help', language['helpBtn']['en']]:
        bot.send_message(message.chat.id, language['help']['en'])

    # Support
    elif message.text in ['/support', language['supportBtn']['en']]:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text=language['joinChannelBtn']['en'], url='t.me/h9youtube'), telebot.types.InlineKeyboardButton(text=language['shareWithFriendsBtn']['en'], url=f"https://t.me/share/url?url=t.me/torrenthuntbot&text={language['shareText']['en']}"))
        markup.add(telebot.types.InlineKeyboardButton(text=language['joinDiscussionBtn']['en'], url='t.me/h9discussion'))
        markup.add(telebot.types.InlineKeyboardButton(text=language['followGithubBtn']['en'], url='https://github.com/hemantapkh'))
        markup.add(telebot.types.InlineKeyboardButton(text=language['subscribeChannelBtn']['en'], url='https://youtube.com/h9youtube'))

        bot.send_message(message.from_user.id, language['support']['en'], reply_markup=markup, disable_web_page_preview=True)
    
    # Query search
    else:
        if isSubscribed(message):
            sent = bot.send_message(message.chat.id, language['searchingQuery']['en'].format(message.text))
            torrent = py1337x.py1337x()
            response = torrent.search(message.text)

            msg, markup = result(response, torrentType='query', page=1, query=message.text)

            bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg or language['noResults']['en'], reply_markup=markup)

# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callbackHandler(call):
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

            msg, markup = result(response, torrentType, page=page, query=query)

            # 1337x may return empty response sometime. So, changing the case to prevent this.
            if not msg and query.islower():
                response = torrent.search(query.capitalize(), page=page)
                msg, markup = result(response, torrentType, page=page, query=query)
            
            elif not msg:
                response = torrent.search(query.lower(), page=page)
                msg, markup = result(response, torrentType, page=page, query=query)
        
        # Next page for trending and popular torrents
        elif torrentType in ['trending', 'popular']:
            torrent = py1337x.py1337x()
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, week=True if week == 'True' else False)
            
            del response['items'][:(page-1)*20]
            msg, markup = result(response, torrentType, page=page, category=category, query=query)
        
        # Next page for top torrents
        elif torrentType == 'top':
            torrent = py1337x.py1337x()
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category)
            
            del response['items'][:(page-1)*20]
            msg, markup = result(response, torrentType, page=page, category=category)

        # Next page for browse torrents
        else:
            torrent = py1337x.py1337x()
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, page=page)

            msg, markup = result(response, torrentType, page=page, category=category)

        if msg:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=msg, reply_markup=markup)
        # If msg is None
        else:
            bot.answer_callback_query(call.id, text=language['emptyPage']['en'], show_alert=True)
    
    # Check whether a user is subscribed or not after clicking done button
    elif call.data == 'cb_checkSubscription':
        if isSubscribed(call, sendMessage=False):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=language['thanksForSub']['en'])
        else:
            bot.answer_callback_query(call.id, language['notSubscribedCallback']['en'])

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