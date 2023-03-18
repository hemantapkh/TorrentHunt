'Miscillaneous functions'

from ast import literal_eval

from loguru import logger
from pyrogram import types


class Misc:
    def __init__(self, Client):
        self.Client = Client

    # Message admins
    async def message_admins(self, message):
        admins = await self.Client.DB.query(
            'fetch',
            'SELECT user_id FROM ADMINS',
        )

        for admin in admins:
            try:
                await self.Client.send_message(
                    chat_id=admin.get('user_id'),
                    text=message,
                    reply_markup=await self.Client.KB.main(),
                )

            except Exception as err:
                logger.error(f'Error sending message to admin: {err}')
                pass

    # Get user language
    async def user_lang(self, message):
        if isinstance(message, types.InlineQuery):
            user_id = message.from_user.id

        else:
            user_id = message.chat.id

            logger.info(f'User language: {user_id}')

        lang = await self.Client.DB.query(
            'fetchval',
            'SELECT language FROM SETTINGS WHERE user_id = $1',
            user_id,
        )

        return lang or 'english'

    # Split message
    def split_list(self, lst, size):
        return [lst[i:i+size] for i in range(0, len(lst), size)]

    # Get the site by it's code
    def code_to_site(self, code):
        data = self.Client.sites
        return next((key for key, value in data.items() if value['code'] == code), None)

    # Get google suggestions of a keyword
    async def google_suggestions(self, query):
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
        }

        params = (
            ('Client', 'Firefox'),
            ('q', query),
        )

        response = await self.Client.requests.get(
            'https://www.google.com/complete/search',
            headers=headers,
            params=params,
        )

        return literal_eval(response)[1]
