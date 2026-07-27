"""The middleware core: one decorator wraps every handler.

`setup_handler` provides:
- guards: `admin` (bot admins only), `chat_admin` (private chats or group
  admins, with an alert to others), `track_user` (upsert the user in the DB)
- dependency injection by signature: a handler declares only the parameters
  it needs from {event, client, t} and the wrapper passes just those
  (`t` is a Translator bound to the user's language)
- logging context: handler name and user id are bound to contextvars so
  every log line during the update carries them automatically
- centralized exception handling: errors are logged instead of killing the
  dispatcher
- dispatch control: after a handler runs (or crashes), `events.StopPropagation`
  stops later handlers, so only the first matching handler in the
  registration table handles an update. A failed guard returns silently,
  letting later handlers (e.g. the catch-all search) take the update instead.
"""

import functools
import inspect
from collections.abc import Callable, Coroutine
from typing import Any

import structlog
from database import get_session
from database.repositories import UserRepository
from structlog import get_logger
from telethon import events

from bot.helpers import is_admin, is_chat_admin, resolve_translator

logger = get_logger(__name__)

Event = (
    events.NewMessage.Event
    | events.CallbackQuery.Event
    | events.InlineQuery.Event
)


def setup_handler(
    track_user: bool = False,
    admin: bool = False,
    chat_admin: bool = False,
) -> Callable:
    def decorator(func: Callable[..., Coroutine[Any, Any, None]]) -> Callable:
        signature = inspect.signature(func)
        handler_name = getattr(func, "__name__", repr(func))

        @functools.wraps(func)
        async def wrapper(event: Event) -> None:
            structlog.contextvars.clear_contextvars()
            structlog.contextvars.bind_contextvars(
                handler=handler_name,
                user_id=event.sender_id,
            )

            try:
                if admin and not await is_admin(event.sender_id):
                    return

                if track_user:
                    async with get_session() as session:
                        await UserRepository(session).upsert_from_event(event)

                t = await resolve_translator(event)

                if chat_admin and not await is_chat_admin(event, t):
                    return

                dependencies: dict[str, Any] = {
                    "event": event,
                    "client": event.client,
                    "t": t,
                }

                await func(**{
                    key: value
                    for key, value in dependencies.items()
                    if key in signature.parameters
                })

            except events.StopPropagation:
                raise

            except Exception:
                logger.exception("Unhandled error in handler")

            raise events.StopPropagation

        return wrapper

    return decorator
