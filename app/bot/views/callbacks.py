"""Callback-data protocol for the search flow.

Every search control (pagination, sort, category, pickers) round-trips the
full search state through Telegram callback data. Wire format:

    <action>_<category code><sort code><page>_<query>

One-char category/sort codes and the query truncated at search time keep
the payload within Telegram's 64-byte callback-data limit.
"""

from dataclasses import dataclass

# One-char category codes; None (no category filter) is encoded as "0"
CATEGORY_CODES: dict[str | None, str] = {
    None: "0",
    "movies": "m",
    "tv": "t",
    "games": "g",
    "music": "u",
    "apps": "a",
    "anime": "n",
    "documentaries": "d",
    "others": "x",
}
CODE_TO_CATEGORY: dict[str, str | None] = {
    code: category for category, code in CATEGORY_CODES.items()
}


@dataclass(frozen=True)
class SearchState:
    query: str
    category: str | None = None
    sort: str = "s"
    page: int = 1

    def pack(self, action: str) -> bytes:
        return f"{action}_{CATEGORY_CODES[self.category]}{self.sort}{self.page}_{self.query}".encode()

    @classmethod
    def unpack(cls, data: bytes) -> SearchState:
        _, state, query = data.decode().split("_", 2)

        return cls(
            query=query,
            category=CODE_TO_CATEGORY[state[0]],
            sort=state[1],
            page=int(state[2:] or 1),
        )
