from src.objs import *   

#: Get images of the torrent   
def getImages(call, userLanguage):    
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