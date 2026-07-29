"""Application configuration.

All environment access lives here: a single typed Settings class loaded
from the process environment plus the .env file (app/ or repo root). Paths
are anchored to APP_DIR so the app can be launched from any directory.
The rest of the code imports `settings` and never touches os.environ.
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(APP_DIR / ".env", APP_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_name: str = "Torrent Hunt"
    bot_token: str
    api_id: int
    api_hash: str
    bot_admins: str = ""  # comma-separated user ids
    workdir: str = ""

    # Database
    database_url: str = "sqlite:///torrenthunt.db"
    torrent_cache_days: float = 90

    # Background jobs
    cleanup_interval_minutes: float = 60

    # Torrent search provider
    torrent_provider: Literal["jackett", "prowlarr"] = "jackett"
    jackett_url: str = "http://localhost:9117"
    jackett_api_key: str = ""
    jackett_indexer: str = "all"
    jackett_timeout: float = 40

    prowlarr_url: str = "http://localhost:9696"
    prowlarr_api_key: str = ""
    prowlarr_indexer: str = "all"
    prowlarr_timeout: float = 40

    message_search_tag: str = ""
    inline_search_tag: str = ""

    # Message to forward on start
    start_ads: bool = False
    start_ads_channel: str = ""
    start_ads_message: str = ""

    # Monitoring
    sentry_dsn: str = ""
    environment: str = "local"


# Required fields (bot_token, ...) come from the environment/.env
settings = Settings()  # ty: ignore[missing-argument]
