"""Shared application context.

One module-level singleton holds the app-lifetime dependencies and runtime
state shared across handlers. Everything is wired at startup in
`torrenthunt.py`; per-update dependencies (event, client, translator) are
injected by `bot.decorators.setup_handler` instead.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from localization import LanguageService
    from models.explicit_detector.explicit_detector import ExplicitDetector
    from services.search import SearchService
    from telethon.tl.types import User


class Context:
    # Assigned during startup, before any handler runs
    language_service: LanguageService
    explicit_detector: ExplicitDetector
    search: SearchService
    me: User

    def __init__(self) -> None:
        self.sites: dict[str, dict[str, str]] = {}  # inline-searchable sources


ctx = Context()
