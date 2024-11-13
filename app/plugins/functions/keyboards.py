"""Markup for reply and inline keywords"""
import base64
from pyrogram import types


class KeyBoard:
    def __init__(self, client):
        self.client = client

    def main(self, lang, message=None):
        if message and message.chat.type.name != "PRIVATE":
            return None

        return types.ReplyKeyboardMarkup(
            [
                [
                    types.KeyboardButton(
                        self.client.language.CMD("bookmarks", lang),
                    ),
                    types.KeyboardButton(self.client.language.CMD("settings", lang)),
                ],
            ],
            is_persistent=True,
            resize_keyboard=True,
        )

    def sites(self, keyword):
        results = [
            types.InlineKeyboardButton(
                text=self.client.sites[key]["title"],
                switch_inline_query_current_chat=f"{self.client.sites[key]['code']} {keyword}",
            )
            for key in self.client.sites
            if not self.client.sites[key].get("deactivated")
        ]

        return (
            types.InlineKeyboardMarkup(
                self.client.misc.split_list(results, 3),
            )
            if results
            else None
        )

    def language(self, welcome=False):
        results = [
            types.InlineKeyboardButton(
                text=self.client.language.config[key]["title"],
                callback_data=f'setLanguage{"New" if welcome else ""}_{key}',
            )
            for key in self.client.language.config
        ]

        return types.InlineKeyboardMarkup(
            self.client.misc.split_list(results, 2),
        )

    def torrent_info(self, user_lang, hash, magnet_link, bookmarked=False):
        if bookmarked:
            results = [
                [
                    types.InlineKeyboardButton(
                        text=self.client.language.BTN("removeFromBookmark", user_lang),
                        callback_data=f"removeFromBookmark_{hash}",
                    ),
                ]
            ]

        else:
            results = [
                [
                    types.InlineKeyboardButton(
                        text=self.client.language.BTN("addToBookmark", user_lang),
                        callback_data=f"addToBookmark_{hash}",
                    ),
                ]
            ]

        results.append(
            [
                types.InlineKeyboardButton(
                    text=self.client.language.BTN("addToSeedr", user_lang),
                    url=f"https://t.me/torrentseedrbot?start=addTorrent_{hash}",
                ),
            ],
        )
        
        results.append(
            [
                types.InlineKeyboardButton(
                    text=self.client.language.BTN("hoodyStream", user_lang),
                    url=f"https://hoody.com/torrent-proxy?af=VRWTSYO72#{base64.b64encode(magnet_link)}",
                ),
            ],
        )

        return types.InlineKeyboardMarkup(
            results,
        )
