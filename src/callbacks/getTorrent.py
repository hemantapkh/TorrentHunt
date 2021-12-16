import requests
from os import remove
from src.objs import *
from pathlib import Path

#: Get the torrent file
def getTorrent(call, userLanguage):
    infoHash = call.data.split(':')[1]
    torrentId = call.data.split(':')[2]

    headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'}
    response = requests.get(f'http://itorrents.org/torrent/{infoHash}.torrent', headers=headers)
    
    if response.ok and not response.content.startswith(b'<!DOCTYPE html PUBLIC'):
        bot.answer_callback_query(call.id)
        bot.send_chat_action(call.message.chat.id, 'upload_document')
        torrentInfo = torrent.info(torrentId=torrentId)

        Path(f"/tmp/TorrentHunt/{call.from_user.id}").mkdir(parents=True, exist_ok=True)

        open(f"/tmp/TorrentHunt/{call.from_user.id}/{torrentInfo['infoHash']}.torrent", 'wb').write(response.content)
        thumbnail = requests.get(torrentInfo['thumbnail']) if torrentInfo['thumbnail'] else None
        
        data = open(f"/tmp/TorrentHunt/{call.from_user.id}/{torrentInfo['infoHash']}.torrent", 'rb')

        #! Deleting the file
        remove(f"/tmp/TorrentHunt/{call.from_user.id}/{torrentInfo['infoHash']}.torrent")

        bot.send_document(call.message.chat.id, data=data, caption=f"{torrentInfo['name']}\n\n{language['size'][userLanguage]}{torrentInfo['size']}\n{language['seeders'][userLanguage]}{torrentInfo['seeders']}\n{language['leechers'][userLanguage]}{torrentInfo['leechers']}\n\n<b>🔥via @TorrentHuntBot</b>", thumb=thumbnail.content if thumbnail else None)
    
    #! Torrent file not found in itorrents
    else:
        bot.answer_callback_query(call.id, text=language['fileNotFound'][userLanguage], show_alert=True)