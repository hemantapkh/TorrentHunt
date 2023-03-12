'Miscillaneous functions'

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
