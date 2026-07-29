"""Bot command menus, localized per language.

One menu is registered per language using Telegram's `lang_code`, so each
user's client shows the commands in its own language automatically (with
the English menu as the default for everything else). Bot admins get an
extended menu via a peer scope, in their configured bot language.

Command descriptions come from the locale files (`<name>CmdDescription`).
"""

from database import get_session
from database.repositories import AdminRepository, UserRepository
from localization import Translator
from structlog import get_logger
from telethon import TelegramClient
from telethon.tl import functions, types

from bot.context import ctx

logger = get_logger(__name__)

DEFAULT_COMMANDS = ("start", "bookmarks", "settings")
GROUP_COMMANDS = ("search",)
GROUP_ADMIN_COMMANDS = ("search", "settings")
BOT_ADMIN_COMMANDS = (*DEFAULT_COMMANDS, "stats", "reload")


def _commands(t: Translator, names: tuple[str, ...]) -> list[types.BotCommand]:
    return [types.BotCommand(name, t.get(f"{name}CmdDescription")) for name in names]


async def set_command_menus(client: TelegramClient) -> None:
    logger.info("Setting bot command menus", languages=len(ctx.language_service.config))

    async def apply(
        scope: types.TypeBotCommandScope,
        names: tuple[str, ...],
        t: Translator,
        lang_code: str,
    ) -> None:
        await client(
            functions.bots.SetBotCommandsRequest(
                scope=scope,
                lang_code=lang_code,
                commands=_commands(t, names),
            ),
        )

    # One menu per language; English is the fallback for every other client
    for language, meta in ctx.language_service.config.items():
        t = ctx.language_service.get_translator(language)
        lang_code = "" if language == "english" else meta.get("code", "")

        await apply(types.BotCommandScopeUsers(), DEFAULT_COMMANDS, t, lang_code)
        await apply(types.BotCommandScopeChats(), GROUP_COMMANDS, t, lang_code)
        await apply(types.BotCommandScopeChatAdmins(), GROUP_ADMIN_COMMANDS, t, lang_code)

    # Bot admins get an extended menu, in their configured bot language
    async with get_session() as session:
        admin_ids = await AdminRepository(session).ids()

    for admin_id in admin_ids:
        try:
            async with get_session() as session:
                language = await UserRepository(session).get_language(admin_id)

            t = ctx.language_service.get_translator(language or "english")
            peer = await client.get_input_entity(admin_id)

            await apply(types.BotCommandScopePeer(peer=peer), BOT_ADMIN_COMMANDS, t, "")
        except Exception as err:
            logger.warning("Error setting commands for admin", admin_id=admin_id, error=str(err))
