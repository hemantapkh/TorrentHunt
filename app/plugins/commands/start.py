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

    await Client.DB.set_user(message, referrer)
    await language(Client, message, called=True)
