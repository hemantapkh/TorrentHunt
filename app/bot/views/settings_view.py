"""Views for /start greetings and the settings flow."""

from html import escape

from localization import Translator
from telethon import Button

from bot.views import ViewResponse
from bot.views.shared_view import main_keyboard


def render_settings_menu(t: Translator, restriction_mode: bool | None) -> ViewResponse:
    if restriction_mode:
        restriction_button_text = t.get("turnOffRestrictedModeBtn")
    else:
        restriction_button_text = t.get("turnOnRestrictedModeBtn")

    return ViewResponse(
        message=t.get("settings").format(t.get("settingsCmd")),
        buttons=[
            [Button.inline(t.get("languageSettingBtn"), b"language")],
            [Button.inline(restriction_button_text, f"restriction_{not restriction_mode}".encode())],
        ],
    )


def render_greet(t: Translator, first_name: str | None, private: bool = True) -> ViewResponse:
    return ViewResponse(
        message=t.get("greet").format(escape(first_name or "")),
        buttons=main_keyboard(t, private=private),
    )


def render_language_selected(t: Translator, private: bool = True) -> ViewResponse:
    return ViewResponse(
        message=t.get("languageSelected"),
        buttons=main_keyboard(t, private=private),
    )


def render_restriction_changed(t: Translator, value: str) -> ViewResponse:
    return ViewResponse(message=t.get(f"restrictedMode{value}"))
