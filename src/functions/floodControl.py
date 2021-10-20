import time
from src.objs import *

#: Flood prevention
def floodControl(message, userLanguage):
    userId = message.from_user.id
    
    if userId == int(config['adminId']):
        return True

    #! If the user is not banned
    if not dbSql.getSetting(userId, 'blockTill', table='flood') - int(time.time())  > 0:
        lastMessage = dbSql.getSetting(userId, 'lastMessage', table='flood')
        called = True if type(message) == telebot.types.CallbackQuery else False

        messageDate = int(time.time()) if called else message.date

        #! Spam detected
        if messageDate - lastMessage < 1:
            #! If the user is already warned, block for 5 minutes
            if dbSql.getSetting(userId, 'warned', table='flood'):
                bot.send_message(message.message.chat.id if called else message.chat.id, language['blockedTooFast'][userLanguage])
                dbSql.setSetting(userId, 'blockTill', int(time.time())+300, table='flood')
                dbSql.setSetting(userId, 'warned', 0, table='flood')
            
            #! If the user is not warned, warn for the first time
            else:
                bot.send_message(message.message.chat.id if called else message.chat.id, language['warningTooFast'][userLanguage])
                dbSql.setSetting(userId, 'warned', 1, table='flood')
            
            return False
        
        #! No spam
        else:
            dbSql.setSetting(userId, 'lastMessage', messageDate, table='flood')
            return True
