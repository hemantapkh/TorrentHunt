"""Language management.

One YAML file per language in `localization/i18n/` (flat key -> string,
with `Btn`/`Cmd` suffix conventions for buttons and command words).
`languages.yml` holds the picker config (title + ISO code per language).

Resolution chain: requested language -> english -> the key itself, so a
missing translation never crashes a handler.
"""

from pathlib import Path

import yaml

DEFAULT_LANGUAGE = "english"


class Translator:
    def __init__(self, strings: dict[str, str], fallback_strings: dict[str, str], language: str):
        self.language = language
        self._strings = strings
        self._fallback_strings = fallback_strings

    def get(self, key: str) -> str:
        return self._strings.get(key) or self._fallback_strings.get(key, key)


class LanguageService:
    def __init__(self, directory: str | Path = "localization"):
        directory = Path(directory)
        self._languages: dict[str, dict[str, str]] = {}
        self._translation_cache: dict[str, set[str]] = {}

        for file_path in sorted((directory / "i18n").glob("*.yml")):
            with open(file_path, encoding="utf-8") as f:
                self._languages[file_path.stem] = yaml.safe_load(f) or {}

        with open(directory / "languages.yml", encoding="utf-8") as f:
            self.config: dict[str, dict[str, str]] = yaml.safe_load(f)

    def get_translator(self, language: str = DEFAULT_LANGUAGE) -> Translator:
        if language not in self._languages:
            language = DEFAULT_LANGUAGE

        return Translator(
            strings=self._languages.get(language, {}),
            fallback_strings=self._languages.get(DEFAULT_LANGUAGE, {}),
            language=language,
        )

    def translations(self, key: str) -> set[str]:
        """Every translation of a key across all languages (for routing).

        Cached: this runs on every incoming message via command matching.
        """
        if key not in self._translation_cache:
            self._translation_cache[key] = {
                strings[key]
                for strings in self._languages.values()
                if strings.get(key)
            }

        return self._translation_cache[key]
