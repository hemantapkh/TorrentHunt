from src.objs import *
from datetime import datetime
from src.functions.floodControl import floodControl

languageSet = [
        "english", 
        "nepali", 
        "bengali", 
        "belarusian", 
        "catalan", 
        "dutch",  
        "french",  
        "german",
        "hindi", 
        "italian", 
        "korean", 
        "malay", 
        "polish", 
        "portuguese", 
        "russian", 
        "spanish", 
        "turkish", 
        "ukrainian"
    ]

#: Get the Statistics of users
@bot.message_handler(commands=['stats'])
def stats(message):
    userLanguage = dbSql.getSetting(message.from_user.id, 'language')

    if message.from_user.id == int(config['adminId']):
        currentDate = datetime.today().strftime('%Y-%m-%d')

        msg = f'<b>📊 Statistics</b>\n\n'

        languageStats = dbSql.getAllUsers(countOnly=True, langStats=True)

        for i in languageStats[1:]:
            msg += f'{i[0].capitalize()}: {i[1]}\n'

        totalGroups = dbSql.getAllUsers(type="groups", countOnly=True)

        msg += f'\n<b>Users: {languageStats[0][1]} <code>({dbSql.getAllUsers(date=currentDate, countOnly=True)} today)</code></b>'
        msg += f'\n<b>Groups: {totalGroups} <code>({dbSql.getAllUsers(type="groups", date=currentDate, countOnly=True)} today)</code></b>'

        bot.send_message(chat_id=message.chat.id, text=msg)