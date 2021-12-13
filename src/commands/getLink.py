from src.objs import *
from src.functions.funs import shortner
from src.functions.floodControl import floodControl

#: Get magnet link of the torrent
@bot.on_message(filters.regex('/getLink_'))
async def getLink(Client, message, userLanguage=None, called=False):
    chatId = message.message.chat.id if called else message.chat.id
    userLanguage = userLanguage or dbSql.getSetting(chatId, 'language')
    
    if (message.message.chat.type if called else message.chat.type) != 'private' or await floodControl(message, userLanguage):
        if called:
            torrentId = message.data[11:]
        
        else:
            sent = await bot.send_message(chatId, text=language['fetchingMagnetLink'][userLanguage], reply_to_message_id=message.message_id if message.chat.type != 'private' else None)
            torrentId = message.text[9:] if message.chat.type == 'private' else message.text[9:].split('@')[0]
        
        response = torrent.info(torrentId=torrentId)
        markup = None

        if response['magnetLink']:
            buttons = []
            if dbSql.getSetting(chatId, 'restrictedMode') and response['category'] == 'XXX':
                msg = language['cantView'][userLanguage]
            
            else:
                msg = f"✨ <b>{response['name']}</b>\n\n<code>{response['magnetLink']}</code>\n\n<b>🔥via @TorrentHuntBot</b>"
                buttons.append([pyrogram.types.InlineKeyboardButton(text='ℹ️ ' + language['moreInfo'][userLanguage].replace(':',''), callback_data=f"cb_getInfo:{torrentId}")])
                
                if response['images']:
                    buttons.append([pyrogram.types.InlineKeyboardButton(text=language['imageBtn'][userLanguage], callback_data=f"cb_getImages:{torrentId}"), pyrogram.types.InlineKeyboardButton(text=language['torrentDownloadBtn'][userLanguage], callback_data=f"cb_getTorrent:{response['infoHash']}:{torrentId}")])
        
                else:
                    buttons.append([pyrogram.types.InlineKeyboardButton(text=language['torrentDownloadBtn'][userLanguage], callback_data=f"cb_getTorrent:{response['infoHash']}:{torrentId}")])
                
                if botId != '1700458114': 
                    shortUrl = shortner(response['magnetLink'])
                    magnetKey = 'URL_'+shortUrl[14:]
                
                else:
                    magnetKey = 'Db_'+dbSql.setMagnet(response['magnetLink'])
                                
                buttons.append([pyrogram.types.InlineKeyboardButton(text=language['addToSeedr'][userLanguage], url=f't.me/torrentseedrbot?start=addTorrent{magnetKey}')])
                markup = pyrogram.types.InlineKeyboardMarkup(buttons)

        else:
            msg = language['errorFetchingLink'][userLanguage]

        if called:
            await bot.answer_callback_query(message.id)
            await bot.edit_message_text(chat_id=chatId, message_id=message.message.message_id, text=msg, reply_markup=markup)
        
        else:
            await bot.edit_message_text(chat_id=chatId, message_id=sent.message_id, text=msg, reply_markup=markup)