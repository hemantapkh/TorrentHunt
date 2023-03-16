'Miscillaneous functions'

from ast import literal_eval

from loguru import logger


class Misc:
    def __init__(self, client):
        self.client = client

    # Message admins
    async def message_admins(self, message):
        admins = await self.client.DB.query(
            'fetch',
            'SELECT user_id FROM ADMINS',
        )

        for admin in admins:
            try:
                await self.client.send_message(
                    chat_id=admin.get('user_id'),
                    text=message,
                    reply_markup=await self.client.KB.main(),
                )

            except Exception as err:
                logger.error(f'Error sending message to admin: {err}')
                pass

    # Get google suggestions of a keyword
    async def google_suggestions(self, query):
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
        }

        params = (
            ('client', 'Firefox'),
            ('q', query),
        )

        response = await self.client.requests.get(
            'https://www.google.com/complete/search',
            headers=headers,
            params=params,
        )

        return literal_eval(response)[1]
