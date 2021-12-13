from src.objs import *
from src.functions.resultParser import result
from src.functions.funs import textToCategory
from src.commands.querySearch import querySearch
from src.functions.keyboard import mainReplyKeyboard, categoryReplyKeyboard

#: Handler for trending, popular, top and browse torrents
async def browse(message,userLanguage, torrentType=None, customMessage=None):
    if message.chat.type == 'private':
        #! If referred or isSubscribed(message, userLanguage):
        torrentType = torrentType or message.text.split()[0][1:]
        
        sent = await bot.ask(message.chat.id, text=customMessage or language['selectCategory'][userLanguage], reply_markup=categoryReplyKeyboard(userLanguage, allCategories=False if torrentType in ['browse', 'popular'] else True, restrictedMode=dbSql.getSetting(message.chat.id, 'restrictedMode')))
        await browse2(sent, userLanguage, torrentType)
    
    else:
        querySearch(message, userLanguage)

#: Next step handler for trending, popular, top and browse torrents
async def browse2(message, userLanguage, torrentType, category=None, customMessage=None):
    #! Main menu
    if message.text == language['mainMenuBtn'][userLanguage]:
        await bot.send_message(message.chat.id, text=language['backToMenu'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
    
    else:
        category = category or textToCategory(message.text, userLanguage)
        if category:
            #! Send time keyboard if trending and popular torrents
            if torrentType in ['trending', 'popular']:
                button1 = pyrogram.types.KeyboardButton(text=language['trendingToday' if torrentType == 'trending' else 'popularToday'][userLanguage])
                button2 = pyrogram.types.KeyboardButton(text=language['trendingThisWeek' if torrentType == 'trending' else 'popularThisWeek'][userLanguage])
                button3 = pyrogram.types.KeyboardButton(text=language['backBtn'][userLanguage])
                button4 = pyrogram.types.KeyboardButton(text=language['mainMenuBtn'][userLanguage])

                keyboard = pyrogram.types.ReplyKeyboardMarkup([
                    [button1],
                    [button2],
                    [button3, button4]
                ],
                
                resize_keyboard=True)

                sent = await bot.ask(message.chat.id, text=customMessage or language['selectTimePeriod'][userLanguage], reply_markup=keyboard)
                await browse3(sent, userLanguage, torrentType, category)
            
            else:
                await browse4(message, userLanguage, torrentType, category)
        else:
            await browse(message, userLanguage, torrentType, customMessage=language['unknownCategory'][userLanguage])

#: Next step handler for trending and popular torrents
async def browse3(message, userLanguage, torrentType, category):
    #! Main menu
    if message.text == language['mainMenuBtn'][userLanguage]:
        await bot.send_message(message.chat.id, text=language['backToMenu'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
    
    #! Back
    elif message.text == language['backBtn'][userLanguage]:
        await browse(message,userLanguage, torrentType, referred=True)
    
    else:
        week = True if message.text == language[torrentType+'ThisWeek'][userLanguage] else False if message.text == language[torrentType+'Today'][userLanguage] else None
        
        #! If week is None, return to browse2
        if week == None:
            await browse2(message, userLanguage, torrentType, category, customMessage=language['unknownTimePeriod'][userLanguage])
        
        else:
            resultType = dbSql.getSetting(message.chat.id, 'defaultMode')
            await bot.send_message(message.chat.id, text=language['fetchingTorrents'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
           
            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, week=week)
            msg, markup = result(response, userLanguage, resultType, torrentType, 1, category, week)
            
            await bot.send_message(chat_id=message.chat.id, text=msg or language['emptyPage'][userLanguage], reply_markup=markup)

#: Next step handler for top and browse torrents
async def browse4(message, userLanguage, torrentType, category):
    await bot.send_message(message.chat.id, text=language['fetchingTorrents'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
    resultType = dbSql.getSetting(message.chat.id, 'defaultMode')
    
    response =  getattr(torrent, torrentType)(category=None if category == 'all' else category)
    msg, markup = result(response, userLanguage, resultType, torrentType, 1, category)

    await bot.send_message(chat_id=message.chat.id, text=msg or language['emptyPage'][userLanguage], reply_markup=markup)