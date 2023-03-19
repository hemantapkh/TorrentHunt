'''Markup for reply and inline keywords'''

from pyrogram import types


class KeyBoard:
    def __init__(self, client):
        self.client = client

    def main(self, lang):
        return types.ReplyKeyboardMarkup(
            [
                [
                    self.client.LG.CMD('settings', lang),
                    self.client.LG.CMD('help', lang),
                    self.client.LG.CMD('support', lang),
                ],
            ],
            resize_keyboard=True,
        )

    def sites(self, keyword):
        results = [
            types.InlineKeyboardButton(
                text=self.client.sites[key]['title'],
                switch_inline_query_current_chat=f"{self.client.sites[key]['code']} {keyword}",
            )

            for key in
            self.client.sites if not self.client.sites[key].get('deactivated')
        ]

        return types.InlineKeyboardMarkup(
            self.client.MISC.split_list(results, 3),
        )

    def language(self):
        results = [
            types.InlineKeyboardButton(
                text=self.client.LG.config[key]['title'],
                callback_data=f'setLanguage_{key}',
            )

            for key in
            self.client.LG.config
        ]

        return types.InlineKeyboardMarkup(
            self.client.MISC.split_list(results, 2),
        )

    def torrent_info(self, hash):
        results = [
            types.InlineKeyboardButton(
                text=self.client.LG.BTN('addToSeedr'),
                url=f'https://t.me/torrentseedrbot?start=addTorrent_{hash}',
            ),
        ]

        return types.InlineKeyboardMarkup(
            [results],
        )
