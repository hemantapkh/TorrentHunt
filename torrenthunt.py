from src import *
    
#: Text handler
@bot.on_message(filters.text)
async def text(client, message):
    userLanguage = dbSql.getSetting(message.chat.id, 'language')
    
    if message.chat.type != 'private' or await floodControl(message, userLanguage):
        if message.via_bot:
            #! Don't search if the message is via the same bot
            if message.via_bot.id == int(botId):
                if message.text.startswith('⦿'):
                    message.text = message.text[1:]
                    await querySearch(message, userLanguage)
                
                else:
                    pass
                
            #! IMDB bot
            elif message.via_bot.username == 'imdb':
                message.text = message.text.split(' •')[0]
                await querySearch(message, userLanguage)
        
        #! Main menu
        elif message.text == language['mainMenuBtn'][userLanguage]:
            await bot.send_message(message.chat.id, text=language['backToMenu'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
        
        #! Trending torrents
        elif message.text in ['/trending', language['trendingBtn'][userLanguage]]:
            await browse(message, userLanguage, 'trending')

        #! Popular torrents
        elif message.text in ['/popular', language['popularBtn'][userLanguage]]:
            await browse(message, userLanguage, 'popular')
            
        #! Top torrents
        elif message.text in ['/top', language['topBtn'][userLanguage]]:
            await browse(message, userLanguage, 'top')
        
        #! Browse torrents
        elif message.text in ['/browse', language['browseBtn'][userLanguage]]:
            await browse(message, userLanguage, 'browse')

        # Settings
        elif message.text == language['settingsBtn'][userLanguage]:
            await settings(client, message, userLanguage)

        #! Help
        elif message.text == language['helpBtn'][userLanguage]:
            await help(client, message, userLanguage)

        #! Support
        elif message.text == language['supportBtn'][userLanguage]:
            await support(client, message, userLanguage)
        
        #! Query search
        else:
            await querySearch(message, userLanguage)

bot.run()