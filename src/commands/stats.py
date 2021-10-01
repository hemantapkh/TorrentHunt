from src.objs import *

#: Get the Statistics of users
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == int(config['adminId']):
        languageSet = ["english", "nepali", "bengali", "belarusian", "catalan", "dutch",  "french",  "german", "hindi", "italian", "korean", "malay", "polish", "portuguese", "russian", "spanish", "turkish", "ukrainian"]
        
        msg = f'<b>📊 Statistics</b>\n\n'
        
        languageStats = {}
        for i in languageSet:
            languageStats[i.capitalize()] = len(dbSql.getUsers(i)) if dbSql.getUsers(i) else 0

        languageStats = {k: v for k, v in sorted(languageStats.items(), key=lambda item: item[1], reverse=True)}

        for i in languageStats:
            msg += f'{i}: {languageStats[i]}\n'

        msg += f'\n<b>Total users: {len(dbSql.getAllUsers()) if dbSql.getAllUsers() else 0}</b>'
        bot.send_message(chat_id=message.chat.id, text=msg)

    else:
        userLanguage = dbSql.getSetting(message.from_user.id, 'language')
        bot.send_message(chat_id=message.chat.id, text=language['noPermission'][userLanguage])