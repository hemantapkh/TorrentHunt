"""Views shared across flows."""

from localization import Translator
from telethon import Button

from bot.views import ViewResponse, chunk


def main_keyboard(t: Translator, private: bool = True) -> list[list[Button]] | None:
    """Persistent reply keyboard with the main shortcuts."""
    if not private:
        return None

    return [
        [
            Button.text(t.get("bookmarksCmd"), resize=True),
            Button.text(t.get("settingsCmd"), resize=True),
        ],
    ]


def render_language_menu(
    t: Translator,
    language_config: dict[str, dict[str, str]],
    welcome: bool = False,
) -> ViewResponse:
    buttons = [
        Button.inline(
            language_config[key]["title"],
            f'setLanguage{"New" if welcome else ""}_{key}'.encode(),
        )
        for key in language_config
    ]

    return ViewResponse(
        message=t.get("chooseLanguage"),
        buttons=chunk(buttons, 2),
    )
