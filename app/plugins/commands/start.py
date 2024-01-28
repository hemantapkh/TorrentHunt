from database.models import Referrer, User
from plugins.settings.language import language
from pyrogram import Client, filters
from sqlalchemy import exists, select, update


@Client.on_message(filters.command("start"))
async def message(Client, message):
    params = message.command[-1] if message.command[-1] != "start" else None

    referrer = None
    if params:
        try:
            # If params is a registered user
            user_id = int(params)
            query = select(exists().where(User.user_id == user_id))

            referrer_exists = await Client.DB.execute(query)
            referrer = referrer if referrer_exists.scalar() else None

        except ValueError:
            # If params is a valid tracking ID
            query = (
                update(Referrer)
                .where(Referrer.referrer_id == params)
                .values(clicks=Referrer.clicks + 1)
            )
            update_clicks = await Client.DB.execute(query)

            referrer = params if update_clicks.rowcount else None

    new_user = await Client.DB.set_user(message, referrer)

    if new_user:
        await language(Client, message, called=True)

    else:
        # Send welcome message
        user_lang = await Client.misc.user_lang(message)
        await Client.send_message(
            chat_id=message.chat.id,
            text=Client.language.STR("greet", user_lang).format(
                message.from_user.first_name,
            ),
            reply_markup=Client.keyboard.main(user_lang, message),
            reply_to_message_id=message.id,
        )
