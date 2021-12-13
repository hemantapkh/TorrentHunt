from src.objs import *   

#: Get images of the torrent   
async def getImages(call, userLanguage):    
    await bot.answer_callback_query(call.id)
    await bot.send_chat_action(call.message.chat.id, 'upload_photo')
    
    torrentId = call.data[13:]
    response = torrent.info(torrentId=torrentId)
    media = []
    
    try:
        if len(response['images']) >= 2:
            for image in response['images']:
                media.append(pyrogram.types.InputMediaPhoto(image.replace('.th.','.'), caption=f"✨ {response['name']}\n\n{language['moreInfo'][userLanguage]} /getLink_{torrentId}\n{language['link'][userLanguage]} /getLink_{torrentId}\n\n🔥 via @TorrentHuntBot"))
                
                if len(media) > 6:
                    await bot.send_media_group(call.message.chat.id, media)
                    media = []
            
            if media:
                await bot.send_media_group(call.message.chat.id, media)
        else:
            await bot.send_photo(call.message.chat.id, photo=response['images'][0].replace('.th.','.'), caption=f"✨ {response['name']}\n\n{language['moreInfo'][userLanguage]} /getLink_{torrentId}\n{language['link'][userLanguage]} /getLink_{torrentId}\n\n🔥 via @TorrentHuntBot")
    
    except Exception as e:
        await bot.send_message(call.message.chat.id, language['errorSendingImage'][userLanguage])