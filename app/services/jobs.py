"""Periodic background jobs running on the bot's event loop.

Telethon has no scheduler of its own, so jobs are plain asyncio tasks:
each runs immediately at startup (so frequent restarts never starve a
job), then repeats on its interval. A failing run is logged and the job
keeps its schedule.
"""

import asyncio
from collections.abc import Awaitable, Callable

from structlog import get_logger

logger = get_logger(__name__)

Job = tuple[str, float, Callable[[], Awaitable[None]]]


def start_background_jobs(jobs: list[Job]) -> list[asyncio.Task]:
    """Start every (name, interval seconds, coroutine function) job."""
    return [
        asyncio.create_task(_run_periodically(name, interval, job), name=name)
        for name, interval, job in jobs
    ]


async def _run_periodically(
    name: str,
    interval: float,
    job: Callable[[], Awaitable[None]],
) -> None:
    while True:
        try:
            await job()
        except Exception:
            logger.exception("Background job failed", job=name)

        await asyncio.sleep(interval)
