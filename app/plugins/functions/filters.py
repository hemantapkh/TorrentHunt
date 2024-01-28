"""Custom filters"""

import re

from database.models import Admin
from pyrogram import filters, types
from sqlalchemy import exists, select


class Filter:
    def __init__(self, Client):
        self.Client = Client

    # Filter to set user to DB
    async def init_flt(_, Client, message):
        await Client.DB.set_user(message)

        return True

    # Filter message from bot admins
    async def admin_flt(_, Client, message):
        query = select(exists().where(Admin.user_id == message.from_user.id))
        is_admin = await Client.DB.execute(query)

        return is_admin.scalar()

    # Filter message from chat admins
    def chat_admin_flt(self, alert=True):
        async def func(flt, Client, message):
            if isinstance(message, types.CallbackQuery):
                callback_id = message.id
                from_user = message.from_user.id
                message = message.message
                message.from_user.id = from_user

            if message.chat.type.name == "PRIVATE":
                return True

            member = await Client.get_chat_member(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
            )

            if member.status.name != "MEMBER":
                return True

            # Show alert message to non-admins users
            if flt.alert:
                user_lang = await Client.misc.user_lang(message)
                if "callback_id" in locals():
                    await Client.answer_callback_query(
                        callback_query_id=callback_id,
                        text=Client.language.STR("noPermission", user_lang),
                        show_alert=True,
                    )

                else:
                    await Client.send_message(
                        chat_id=message.chat.id,
                        text=Client.language.STR("noPermission", user_lang),
                        reply_to_message_id=message.id,
                    )

        return filters.create(func, alert=alert)

    # Command filters with reply keyboard
    def cmd(self, data):
        async def func(flt, Client, message):
            if message.text:
                language = await Client.misc.user_lang(message)
                text = re.sub(r"^\/?([^@]+).*", r"\1", message.text)

                if text in [flt.data, self.Client.language.CMD(flt.data, language)]:
                    return True

        return filters.create(func, data=data)

    # Filter via message from own
    async def via_flt(_, Client, message):
        if message.via_bot:
            return message.via_bot.id == Client.me.id

    init = filters.create(init_flt)
    admin = filters.create(admin_flt)
    via_me = filters.create(via_flt)
    chat_admin = filters.create(chat_admin_flt)
