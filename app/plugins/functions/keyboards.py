"""Markup for reply and inline keywords"""

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
                text=self.client.sites[key]["website"],
                switch_inline_query_current_chat=f"!{key} {keyword}",
            )
            for key in self.client.sites
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

    def categories(self, query):
        category_map = {
            "movies": "🎬 Movies",
            "tv": "📺 TV",
            "games": "🎮 Games",
            "music": "🎵 Music",
            "apps": "🖥️ Apps",
            "anime": "🎎 Anime",
            "documentaries": "🎥 Documentaries",
            "xxx": "🔞 Other",
        }

        # Truncate query to the max safe length to avoid hitting Telegram's limit
        truncated_query = query[:46]

        buttons = [
            types.InlineKeyboardButton(
                text=display_text,
                callback_data=f"cat_{category_name}_{truncated_query}",
            )
            for category_name, display_text in category_map.items()
        ]

        return types.InlineKeyboardMarkup(
            self.client.misc.split_list(buttons, 2),
        )

    def torrent_info(self, user_lang, hash, bookmarked=False):
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

        return types.InlineKeyboardMarkup(
            results,
        )
