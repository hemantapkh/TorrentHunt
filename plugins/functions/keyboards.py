'''Markup for reply and inline keywords'''

from pyrogram import types


class KeyBoard:
    def __init__(self, client):
        self.client = client

    async def main(self, message):
        return types.ReplyKeyboardMarkup(
            [
                [
                    await self.client.LG.BTN('settings', message),
                    await self.client.LG.BTN('help', message),
                    await self.client.LG.BTN('support', message),
                ],
            ],
            resize_keyboard=True,
        )
