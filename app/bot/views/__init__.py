"""View layer: pure render functions for every user-facing message.

A view takes data + a Translator (never an event or the client) and returns
a ViewResponse. Handlers send/edit the response; views decide how things
look. Keyboards live next to the messages they belong to.
"""

from typing import NamedTuple


class ViewResponse(NamedTuple):
    message: str | None = None
    buttons: list | None = None
    description: str | None = None  # summary line for inline results


def chunk(lst: list, size: int) -> list[list]:
    """Split buttons into keyboard rows of `size`."""
    return [lst[i : i + size] for i in range(0, len(lst), size)]
