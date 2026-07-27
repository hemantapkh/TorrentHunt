"""Structured logging configuration.

Local environments get a pretty console renderer; anything else emits JSON
lines for log aggregation. Per-update context (handler, user id) is bound
via contextvars in `bot.decorators.setup_handler`, so it appears on every
log line without being passed around.
"""

import logging
import sys

import structlog


def configure_logging(environment: str = "local") -> None:
    # Route stdlib logging through a plain handler and keep third-party
    # loggers (telethon, sqlalchemy, ...) quiet unless they warn
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.WARNING)

    processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ],
        ),
        structlog.processors.StackInfoRenderer(),
    ]

    if environment == "local":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors += [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )
