from src.objs import *
from src.commands.getLink import getLink
from src.commands.getInfo import getInfo
from src.commands.settings import settings
from src.functions.funs import isSubscribed
from src.callbacks.getImages import getImages
from src.callbacks.getTorrent import getTorrent
from src.callbacks.nextPage import nextPage, nextPageQuery
from src.functions.keyboard import mainReplyKeyboard, lang

#: Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callbackHandler(call):
    userLanguage = dbSql.getSetting(call.from_user.id, 'language')
    resultType = dbSql.getSetting(call.from_user.id, 'defaultMode')

    #! Next page handler for query
    if call.data[:1] == 'q':
        nextPageQuery(call, userLanguage, resultType)

    #! Next page handler
    elif call.data[:11] == 'cb_nextPage':
        nextPage(call, userLanguage, resultType)

    #! Get torrent link
    elif call.data[:10] == 'cb_getLink':
        getLink(call, userLanguage, called=True)
        dbSql.setSetting(call.from_user.id, 'defaultMode', 'link')

    #! Get torrent info
    elif call.data[:10] == 'cb_getInfo':
        getInfo(call, userLanguage, called=True)
        dbSql.setSetting(call.from_user.id, 'defaultMode', 'info')

    #! Get torrent images
    elif call.data[:13] == 'cb_getImages:':
        getImages(call, userLanguage)

    #! Get torrent file
    elif call.data[:14] == 'cb_getTorrent:':
        getTorrent(call, userLanguage)

    #! Language settings
    elif call.data[:18] == 'cb_languageSetting':
        lang(call, userLanguage, called=True)

    #! Select language
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

    #! Content filter setting
    elif call.data[:17] == 'cb_restrictedMode':
        restrictedMode = 1 if call.data[17:] == 'On' else 0
        dbSql.setSetting(call.from_user.id, 'restrictedMode', restrictedMode)
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=language['restrictedModeOn' if restrictedMode else 'restrictedModeOff'][userLanguage])

    #! Back to settings
    elif call.data[:17] == 'cb_backToSettings':
        settings(call, userLanguage, called=True)

    #! Check whether a user is subscribed or not after clicking done button
    elif call.data == 'cb_checkSubscription':
        if isSubscribed(call, None, sendMessage=False):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=language['thanksForSub'][userLanguage])
        else:
            bot.answer_callback_query(call.id, language['notSubscribedCallback'][userLanguage])