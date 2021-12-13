from src.objs import *
from asyncio import sleep

#: Broadcast message
@bot.on_message(filters.command('broadcast'))
async def broadcast(client, message):
    if message.from_user.id == int(config['adminId']):
        sent = await bot.ask(chat_id=message.chat.id, text='<b>Choose the audience.</b>\n\n/all /bengali /belarusian /catalan /dutch /english /french /german /hindi /italian /korean /malay /nepali /polish /portuguese /russian /spanish /turkish /ukrainian \n\n/cancel to cancel the broadcast.')
        await broadcast2(sent)
    
    else:
        userLanguage = dbSql.getSetting(message.chat.id, 'language')
        await bot.send_message(chat_id=message.chat.id, text=language['noPermission'][userLanguage])
    
async def broadcast2(message):
    if message.text == '/cancel':
        await bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')
    else:
        if message.text == '/all':
            sent = await bot.ask(chat_id=message.chat.id, text='<b>Choose the audience to exclude from broadcasting.</b>\n\n<code>bengali</code>, <code>belarusian</code>, <code>catalan</code>, <code>dutch</code>, <code>english</code>, <code>french</code>, <code>german</code>, <code>hindi</code>, <code>italian</code>, <code>korean</code>, <code>malay</code>, <code>nepali</code>, <code>polish</code>, <code>portuguese</code>, <code>russian</code>, <code>spanish</code>, <code>turkish</code>, <code>ukrainian</code> \n\n<b>Separate by comma for multiple exclusion.</b>\n\n/cancel to cancel the broadcast.\n/skip to Skip the exclusion.')
            await broadcastExclusion(sent)
        
        elif message.text in ['/bengali', '/belarusian', '/catalan', '/dutch', '/english', '/french', '/german', '/hindi', '/italian', '/korean', '/malay', '/nepali', '/polish', '/portuguese', '/russian', '/spanish', '/turkish', '/ukrainian']:
            audience = message.text[1:]
            sent = await bot.ask(chat_id=message.chat.id, text='<b>Send the message to broadcast.</b>\n\nMarkup: HTML\nTags allowed: a href, b, i, u, s, code, pre, h1, inv, br\n\n/cancel to cancel the broadcast.')
            await broadcast3(sent, audience)
        
        else:
            await bot.send_message(chat_id=message.chat.id, text='❌ Unknown audience. Broadcast cancelled.')

async def broadcastExclusion(message):
    if message.text == '/skip':
        sent = await bot.ask(chat_id=message.chat.id, text='<b>Send the message to broadcast.</b>\n\nMarkup: HTML\nTags allowed: a href, b, i, u, s, code, pre, h1, inv, br\n\n/cancel to cancel the broadcast.')
        await broadcast3(sent, audience='all', exclude=None)
    
    elif message.text == '/cancel':
        await bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')
    
    else:
        sent = await bot.ask(chat_id=message.chat.id, text='<b>Send the message to broadcast.</b>\n\nMarkup: HTML\nTags allowed: a href, b, i, u, s, code, pre, h1, inv, br\n\n/cancel to cancel the broadcast.')
        exclude = [x.strip() for x in message.text.split(',')]
        await broadcast3(sent, audience='all', exclude=exclude)

async def broadcast3(message, audience, exclude=None):
    if message.text != '/cancel':
        sent2 = bot.ask(chat_id=message.chat.id, text='<b>To send embed button, send the link in the following format.</b>\n\n<code>Text1 -> URL1\nText2 -> URL2</code>\n\n/cancel to cancel the broadcast.\n/skip to skip the buttons.')
        await broadcast4(sent2, audience, exclude, message.text)
    
    else:
        await bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')
    
async def broadcast4(message, audience, exclude, textMessage):
    if message.text == '/cancel':
        await bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')
    
    elif message.text == '/skip':
        if audience == 'all':
            if exclude:
                users = dbSql.getUsersExcept(exclude)
            else:
                users = dbSql.getAllUsers()
        
        else:
            users = dbSql.getUsers(audience)
        
        users = len(users) if users else 0
        
        try:
            await bot.send_message(message.chat.id, text=f'<b>Message Preview</b>\n\n{textMessage}',)
            sent = await bot.ask(message.chat.id, text=f"/send to broadcast this message.\n\nTarget Audience: {audience}\nExcluded Audience: {' '.join(exclude) if exclude else None}\nTotal audience: {users}")
            await broadcast5(sent, broadcast5, audience, exclude, textMessage, markup=None)
        
        except Exception as e:
            await bot.send_message(chat_id=message.chat.id, text=f"<b>⚠️ Error</b>\n\n{str(e).replace('<','')}")

    else:
        if audience == 'all':
            if exclude:
                users = dbSql.getUsersExcept(exclude)
            else:
                users = dbSql.getAllUsers()
        
        else:
            users = dbSql.getUsers(audience)
        
        users = len(users) if users else 0

        try:
            markup = []
            for i in message.text.split('\n'):
                markup.append(pyrogram.types.InlineKeyboardButton(text=i.split('->')[0].strip(), url=i.split('->')[1].strip()))

            keyboard = pyrogram.InlineKeyboardMarkup(inline_keyboard=[markup])
            
            await bot.send_message(message.chat.id, text=f'<b>Message Preview</b>\n\n{textMessage}', reply_markup=keyboard)
            
            sent = await bot.ask(message.chat.id, text=f"/send to broadcast this message.\n\nTarget Audience: {audience}\nExcluded Audience: {' '.join(exclude) if exclude else None}\nTotal audience: {users}")
            await broadcast5(sent, audience, exclude, textMessage, markup)
        
        except Exception as e:
            await bot.send_message(message.chat.id, text=f"<b>⚠️ Error</b>\n\n{str(e).replace('<','')}")

async def broadcast5(message, audience, exclude, textMessage, markup):
    if message.text == '/send':
        sent = await bot.send_message(chat_id=message.chat.id, text='<code>Broadcasting message</code>')
        if audience == 'all':
            if exclude:
                users = dbSql.getUsersExcept(exclude)
            else:
                users = dbSql.getAllUsers()
        
        else:
            users = dbSql.getUsers(audience)
        
        failure = 0
        success = 0
        updateCount = 0

        if users:
            for userId in users:
                try:
                    await bot.send_message(chat_id=userId, text=textMessage, reply_markup=markup)
                    success += 1
                    updateCount += 1
                
                except Exception:
                    failure += 1
                    updateCount += 1

                finally:
                    sleep(0.1)
                    if updateCount == 15:
                        updateCount = 0
                        await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=f'<code>{failure+success} out of {len(users)} complete.</code>')

            await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=f'<b>✈️ Broadcast Report</b>\n\nSuccess: {success}\nFailure: {failure}')
        
        else:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=f'❌ No user to broadcast message.')
    else:
        await bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')