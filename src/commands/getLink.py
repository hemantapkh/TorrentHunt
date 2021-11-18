from src.objs import *
from src.functions.funs import shortner
from src.functions.floodControl import floodControl

#: Get magnet link of the torrent
@bot.message_handler(func=lambda message: message.text and message.text[:9] == '/getLink_')
def getLink(message, userLanguage=None, called=False):
    chatId = message.message.chat.id if called else message.chat.id
    userLanguage = userLanguage or dbSql.getSetting(chatId, 'language')
    
    if (message.message.chat.type if called else message.chat.type) != 'private' or floodControl(message, userLanguage):
        if called:
            torrentId = message.data[11:]
        
        else:
            sent = bot.send_message(chatId, text=language['fetchingMagnetLink'][userLanguage], reply_to_message_id=message.id if message.chat.type != 'private' else None)
            torrentId = message.text[9:] if message.chat.type == 'private' else message.text[9:].split('@')[0]
        
        response = torrent.info(torrentId=torrentId)
        markup = None

        if response['magnetLink']:
            markup = telebot.types.InlineKeyboardMarkup()
            if dbSql.getSetting(chatId, 'restrictedMode') and response['category'] == 'XXX':
                msg = language['cantView'][userLanguage]
            
            else:
                msg = f"✨ <b>{response['name']}</b>\n\n<code>{response['magnetLink']}</code>\n\n<b>🔥via @TorrentHuntBot</b>"

                if response['images']:
                    markup.add(telebot.types.InlineKeyboardButton(text='ℹ️ ' + language['moreInfo'][userLanguage].replace(':',''), callback_data=f"cb_getInfo:{torrentId}"), telebot.types.InlineKeyboardButton(text=language['imageBtn'][userLanguage], callback_data=f"cb_getImages:{torrentId}"))
        
                else:
                    markup.add(telebot.types.InlineKeyboardButton(text='ℹ️ ' + language['moreInfo'][userLanguage].replace(':',''), callback_data=f"cb_getInfo:{torrentId}"))

                shortUrl = shortner(response['magnetLink'])
                magnetKey = 'Db_'+dbSql.setMagnet(response['magnetLink']) if botId == '1700458114' else 'URL_'+shortUrl[14:]
                
                markup.add(telebot.types.InlineKeyboardButton(text=language['torrentDownloadBtn'][userLanguage], callback_data=f"cb_getTorrent:{response['infoHash']}:{torrentId}"), telebot.types.InlineKeyboardButton(text=language['magnetDownloadBtn'][userLanguage], url=shortUrl))
                #markup.add(telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='t.me/h9youtube'), telebot.types.InlineKeyboardButton(text=language['joinDiscussionBtn'][userLanguage], url='t.me/h9discussion'))
                markup.add(telebot.types.InlineKeyboardButton(text=language['addToSeedr'][userLanguage], url=f't.me/torrentseedrbot?start=addTorrent{magnetKey}'))
        else:
            msg = language['errorFetchingLink'][userLanguage]

        if called:
            bot.answer_callback_query(message.id)
            bot.edit_message_text(msg, chatId, message_id=message.message.id, reply_markup=markup)
        
        else:
            bot.edit_message_text(msg, chatId, message_id=sent.message_id, reply_markup=markup)