from src.objs import *
from time import sleep

#: Broadcast message
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == int(config['adminId']):
        sent = bot.send_message(chat_id=message.chat.id, text='<b>Choose the audience.</b>\n\n/all /bengali /belarusian /catalan /dutch /english /french /german /hindi /italian /korean /malay /nepali /polish /portuguese /russian /spanish /turkish /ukrainian \n\n/cancel to cancel the broadcast.')
        bot.register_next_step_handler(sent, broadcast2)

def broadcast2(message):
    if message.text == '/cancel':
        bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')
    else:
        if message.text == '/all':
            sent = bot.send_message(chat_id=message.chat.id, text='<b>Choose the audience to exclude from broadcasting.</b>\n\n<code>bengali</code>, <code>belarusian</code>, <code>catalan</code>, <code>dutch</code>, <code>english</code>, <code>french</code>, <code>german</code>, <code>hindi</code>, <code>italian</code>, <code>korean</code>, <code>malay</code>, <code>nepali</code>, <code>polish</code>, <code>portuguese</code>, <code>russian</code>, <code>spanish</code>, <code>turkish</code>, <code>ukrainian</code> \n\n<b>Separate by comma for multiple exclusion.</b>\n\n/cancel to cancel the broadcast.\n/skip to Skip the exclusion.')
            bot.register_next_step_handler(sent, broadcastExclusion)

        elif message.text in ['/bengali', '/belarusian', '/catalan', '/dutch', '/english', '/french', '/german', '/hindi', '/italian', '/korean', '/malay', '/nepali', '/polish', '/portuguese', '/russian', '/spanish', '/turkish', '/ukrainian']:
            audience = message.text[1:]
            sent = bot.send_message(chat_id=message.chat.id, text='<b>Send the message to broadcast.</b>\n\nMarkup: HTML\nTags allowed: a href, b, i, u, s, code, pre, h1, inv, br\n\n/cancel to cancel the broadcast.')
            bot.register_next_step_handler(sent, broadcast3, audience)

        else:
            bot.send_message(chat_id=message.chat.id, text='❌ Unknown audience. Broadcast cancelled.')

def broadcastExclusion(message):
    if message.text == '/skip':
        sent = bot.send_message(chat_id=message.chat.id, text='<b>Send the message to broadcast.</b>\n/cancel to cancel the broadcast.')
        bot.register_next_step_handler(sent, broadcast3, audience='all', exclude=None)

    elif message.text == '/cancel':
        bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')

    else:
        sent = bot.send_message(chat_id=message.chat.id, text='<b>Send the message to broadcast.\n/cancel to cancel the broadcast.')
        exclude = [x.strip() for x in message.text.split(',')]
        bot.register_next_step_handler(sent, broadcast3, audience='all', exclude=exclude)

def broadcast3(message, audience, exclude=None):
    if message.text != '/cancel':
        sent2 = bot.send_message(chat_id=message.chat.id, text='<b>To send embed button, send the link in the following format.</b>\n\n<code>Text1 -> URL1\nText2 -> URL2</code>\n\n/cancel to cancel the broadcast.\n/skip to skip the buttons.')
        bot.register_next_step_handler(sent2, broadcast4, audience, exclude, message)

    else:
        bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')

def broadcast4(message, audience, exclude, textMessage):
    markup = telebot.types.InlineKeyboardMarkup()
    if message.text == '/cancel':
        bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')

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
            if textMessage.photo:
                bot.send_photo(message.chat.id, photo=textMessage.photo[0].file_id, caption=textMessage.caption, parse_mode='MarkdownV2')

            else:
                bot.send_message(message.chat.id, text=textMessage.text, parse_mode='MarkdownV2')
            sent = bot.send_message(message.chat.id, text=f"/send to broadcast this message.\n\nTarget Audience: {audience}\nExcluded Audience: {' '.join(exclude) if exclude else None}\nTotal audience: {users}")
            bot.register_next_step_handler(sent, broadcast5, audience, exclude, textMessage, markup=None)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id, text=f"<b>⚠️ Error</b>\n\n{str(e).replace('<','')}")

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
            for i in message.text.split('\n'):
                markup.add(telebot.types.InlineKeyboardButton(text=i.split('->')[0].strip(), url=i.split('->')[1].strip()))

            bot.send_message(message.chat.id, text=f'<b>Message Preview</b>\n\n{textMessage}', reply_markup=markup)
            sent = bot.send_message(message.chat.id, text=f"/send to broadcast this message.\n\nTarget Audience: {audience}\nExcluded Audience: {' '.join(exclude) if exclude else None}\nTotal audience: {users}")
            bot.register_next_step_handler(sent, broadcast5, audience, exclude, textMessage, markup)

        except Exception as e:
            bot.send_message(message.chat.id, text=f"<b>⚠️ Error</b>\n\n{str(e).replace('<','')}")

def broadcast5(message, audience, exclude, textMessage, markup):
    if message.text == '/send':
        sent = bot.send_message(chat_id=message.chat.id, text='<code>Broadcasting message</code>')
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
                    if textMessage.photo:
                        bot.send_photo(userId, photo=textMessage.photo[0].file_id, caption=textMessage.caption, reply_markup=markup, disable_notification=True, parse_mode='MarkdownV2')

                    else:
                        bot.send_message(chat_id=userId, text=textMessage.text, reply_markup=markup, parse_mode='MarkdownV2')
                    success += 1
                    updateCount += 1

                except Exception:
                    failure += 1
                    updateCount += 1

                finally:
                    sleep(0.2)
                    if updateCount == 5000:
                        updateCount = 0
                        bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=f'<code>{failure+success} out of {len(users)} complete. Success: {success}, Failure: {failure}</code>')

            bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=f'<b>✈️ Broadcast Report</b>\n\nSuccess: {success}\nFailure: {failure}')

        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=f'❌ No user to broadcast message.')
    else:
        bot.send_message(chat_id=message.chat.id, text='❌ Broadcast cancelled')