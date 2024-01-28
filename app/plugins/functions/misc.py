"Miscillaneous functions"

from database.models import Setting
from loguru import logger
from pyrogram import types
from sqlalchemy import select


class Misc:
    def __init__(self, Client):
        self.Client = Client

    # Fetching config from Torrent Hunt API
    async def fetch_config(self):
        # Get available sites
        config = await self.Client.TH.request(
            "/api/config",
        )

        if "error" in config:
            logger.error("Error connecting to Torrent Hunt API.")
            self.Client.sites = {}

        else:
            logger.info("Successfully fetched config for Torrent Hunt API")
            self.Client.sites = config

        # await self.message_admins('🔃 Bot has been restarted.')

    # Message admins
    async def message_admins(self, message):
        admins = await self.Client.DB.query(
            "fetch",
            "SELECT user_id FROM ADMINS",
        )

        for admin in admins:
            user_lang = await self.user_lang(admin.get("user_id"))
            try:
                await self.Client.send_message(
                    chat_id=admin.get("user_id"),
                    text=message,
                    reply_markup=self.Client.KB.main(user_lang),
                )

            except Exception as err:
                logger.error(f"Error sending message to admin: {err}")
                pass

    # Get user language
    async def user_lang(self, message):
        if isinstance(message, types.InlineQuery):
            user_id = message.from_user.id

        elif isinstance(message, types.CallbackQuery):
            if message.message:
                user_id = message.message.chat.id
            else:
                user_id = message.from_user.id

        elif isinstance(message, int):
            user_id = message

        else:
            user_id = message.chat.id

        statement = select(Setting.language).where(Setting.user_id == user_id)
        lang = await self.Client.DB.execute(statement)
        lang = lang.scalar()

        return lang or "english"

    # Split message
    def split_list(self, lst, size):
        return [lst[i : i + size] for i in range(0, len(lst), size)]

    # Get the site by it's code
    def code_to_site(self, code):
        data = self.Client.sites
        return next((key for key, value in data.items() if value["code"] == code), None)
