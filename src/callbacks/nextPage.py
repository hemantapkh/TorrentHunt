from src.objs import *
from src.functions.resultParser import result

#: Next page handler for query
async def nextPageQuery(call, userLanguage, resultType):
    splittedData = call.data.split(':', 2)
    page = int(splittedData[1])
    query = splittedData[2]
    torrentType = None

    response = torrent.search(query, page=page)

    msg, markup = result(response, userLanguage, resultType, torrentType, page=page, query=query)

    #! 1337x may return empty response sometime. So, changing the case to prevent this.
    if not msg and query.islower():
        response = torrent.search(query.capitalize(), page=page)
        msg, markup = result(response, userLanguage, resultType, torrentType, page=page, query=query)
    
    elif not msg:
        response = torrent.search(query.lower(), page=page)
        msg, markup = result(response, userLanguage, resultType, torrentType, page=page, query=query)

    if msg:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup)
    
    #! If msg is None
    else:
        await bot.answer_callback_query(call.id, text=language['emptyPage'][userLanguage], show_alert=True)

#! Next page
async def nextPage(call, userLanguage, resultType):
    splittedData = call.data.split(':', 2)
    page = int(splittedData[1])
    torrentType = splittedData[2].split('-')[0]
    category =  splittedData[2].split('-')[1]
    week =  splittedData[2].split('-')[2]
    
    #! Next page for trending and popular torrents
    if torrentType in ['trending', 'popular']:
        response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, week=True if week == 'True' else False)
        
        del response['items'][:(page-1)*20]
        msg, markup = result(response, userLanguage, resultType, torrentType, page=page, category=category)
    
    #! Next page for top torrents
    elif torrentType == 'top':
        response =  getattr(torrent, torrentType)(category=None if category == 'all' else category)
        
        del response['items'][:(page-1)*20]
        msg, markup = result(response, userLanguage, resultType, torrentType, page=page, category=category)

    #! Next page for browse torrents
    else:
        response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, page=page)

        msg, markup = result(response, userLanguage, resultType, torrentType, page=page, category=category)

    if msg:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup)
    
    #! If msg is None
    else:
        await bot.answer_callback_query(call.id, text=language['emptyPage'][userLanguage], show_alert=True)