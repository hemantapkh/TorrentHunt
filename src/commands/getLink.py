from src.objs import *
from src.functions.funs import shortner

#: Get magnet link of the torrent
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
                markup.add(telebot.types.InlineKeyboardButton(text=language['imageBtn'][userLanguage], callback_data=f"cb_getImages:{torrentId}"), telebot.types.InlineKeyboardButton(text=language['torrentDownloadBtn'][userLanguage], callback_data=f"cb_getTorrent:{response['infoHash']}:{torrentId}"))
    
            else:
                markup.add(telebot.types.InlineKeyboardButton(text=language['torrentDownloadBtn'][userLanguage], callback_data=f"cb_getTorrent:{response['infoHash']}:{torrentId}"))

            shortUrl = shortner(response['magnetLink'])
            magnetKey = 'Db_'+dbSql.setMagnet(response['magnetLink']) if botId == '1700458114' else 'URL_'+shortUrl[20:]
            
            markup.add(telebot.types.InlineKeyboardButton(text=language['magnetDownloadBtn'][userLanguage], url=shortUrl))
            markup.add(telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='t.me/h9youtube'), telebot.types.InlineKeyboardButton(text=language['joinDiscussionBtn'][userLanguage], url='t.me/h9discussion'))
            markup.add(telebot.types.InlineKeyboardButton(text=language['addToSeedr'][userLanguage], url=f't.me/torrentseedrbot?start=addTorrent{magnetKey}'))
    else:
        msg = language['errorFetchingLink'][userLanguage]

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=msg, reply_markup=markup)