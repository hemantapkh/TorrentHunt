"""Views for the search flow: results pages and their picker keyboards."""

from collections.abc import Callable
from dataclasses import replace
from html import escape
from typing import Any

from localization import Translator
from telethon import Button

from bot.views import ViewResponse, chunk
from bot.views.callbacks import SearchState

PAGE_SIZE = 10

# Category -> label key in the locale files
CATEGORY_LABELS: dict[str, str] = {
    "movies": "moviesBtn",
    "tv": "tvBtn",
    "games": "gamesBtn",
    "music": "musicBtn",
    "apps": "appsBtn",
    "anime": "animeBtn",
    "documentaries": "docsBtn",
    "others": "othersBtn",
}

# Sort modes: code -> (label key, sort key on item dict)
SORTS: dict[str, tuple[str, Callable[[dict[str, Any]], float]]] = {
    "s": ("seedsBtn", lambda item: item.get("seeders") or 0),
    "z": ("sizeBtn", lambda item: item.get("size_bytes") or 0),
    "d": ("uploadDateBtn", lambda item: item.get("uploaded_at") or 0),
}

# Header of paged search results
header_template = """{search_icon} <b>{query}</b>
<blockquote>{category_str}: {category}
{sort_str}: {sort_label}
{page_str}: {page}/{pages} · {total} {results_str}</blockquote>
"""

# One item in paged search results. The title is a deep link
# (t.me/<bot>?start=get_<id>) so tapping it delivers the torrent.
item_template = """
<b>{num}. <a href="{link}">{title}</a></b>
<i>{storage_icon} {size} · {seeders_icon} {seeders} · {leechers_icon} {leechers} · {date_icon} {uploaded_on}</i>
"""


def category_label(t: Translator, category: str | None) -> str:
    return t.get(CATEGORY_LABELS[category]) if category else t.get("allBtn")


def render_searching(query: str, t: Translator) -> ViewResponse:
    return ViewResponse(message=t.get("searchingQuery").format(escape(query)))


def render_group_search_prompt(t: Translator) -> ViewResponse:
    """Ask for a search query, force-replying the requester."""
    return ViewResponse(
        message=t.get("queryToSearch"),
        buttons=Button.force_reply(selective=True),
    )


def page_count(total_items: int) -> int:
    """Number of result pages for a result-set size."""
    return max((total_items + PAGE_SIZE - 1) // PAGE_SIZE, 1)


def render_search_results(
    response: dict[str, Any],
    t: Translator,
    state: SearchState,
    username: str,
    sites: dict[str, dict[str, str]],
) -> ViewResponse:
    """One page of search results with its control keyboard.

    The page in `state` is clamped to the available range before
    rendering.
    """
    items = list(response.get("items") or [])

    if not items:
        return ViewResponse(
            message=t.get("noResults"),
            buttons=_controls(replace(state, page=1), 1, sites, t, has_results=False),
        )

    items.sort(key=SORTS.get(state.sort, SORTS["s"])[1], reverse=True)

    pages = page_count(len(items))
    state = replace(state, page=min(max(state.page, 1), pages))
    page_items = items[(state.page - 1) * PAGE_SIZE : state.page * PAGE_SIZE]

    text = header_template.format(
        search_icon=t.get("searchIcon"),
        query=escape(state.query),
        category=category_label(t, state.category),
        sort_label=t.get(SORTS.get(state.sort, SORTS["s"])[0]),
        page=state.page,
        pages=pages,
        total=len(items),
        category_str=t.get("category"),
        sort_str=t.get("sortBy"),
        page_str=t.get("page"),
        results_str=t.get("results"),
    )

    # Items are listed in reverse (best result at the bottom), so the top
    # result sits right next to the buttons
    for offset, item in reversed(list(enumerate(page_items))):
        text += item_template.format(
            num=(state.page - 1) * PAGE_SIZE + offset + 1,
            link=f"https://t.me/{username}?start=get_{item.get('torrent_id')}",
            title=escape(item.get("name")[:70]),
            size=item.get("size"),
            seeders=item.get("seeders"),
            leechers=item.get("leechers"),
            uploaded_on=item.get("uploaded_on") or "—",
            storage_icon=t.get("storageIcon"),
            seeders_icon=t.get("seedersIcon"),
            leechers_icon=t.get("leechersIcon"),
            date_icon=t.get("dateIcon"),
        )

    return ViewResponse(message=text, buttons=_controls(state, pages, sites, t))


def _controls(
    state: SearchState,
    pages: int,
    sites: dict[str, dict[str, str]],
    t: Translator,
    has_results: bool = True,
) -> list[list[Button]]:
    """Control keyboard under a results page."""
    rows = []

    # Pagination; the middle indicator opens the page picker
    if pages > 1:
        rows.append(
            [
                Button.inline(
                    t.get("previousIcon"),
                    replace(state, page=state.page - 1).pack("res") if state.page > 1 else b"noop",
                ),
                Button.inline(f"{state.page}/{pages}", state.pack("pages")),
                Button.inline(
                    t.get("nextIcon"),
                    replace(state, page=state.page + 1).pack("res") if state.page < pages else b"noop",
                ),
            ],
        )

    # Collapsed filter controls; each expands into a picker keyboard.
    # Sorting is pointless without results, so only category (which can
    # rescue an over-filtered search) stays in that case.
    controls = []
    if has_results:
        controls.append(Button.inline(t.get("sortBtn"), state.pack("sort")))
    controls.append(Button.inline(t.get("categoryBtn"), state.pack("cats")))
    rows.append(controls)

    # Direct shortcuts for the first few sites; the rest sit behind More
    site_buttons = [
        Button.switch_inline(
            sites[key]["website"],
            query=f"!{key} {state.query}",
            same_peer=True,
        )
        for key in list(sites)[:5]
    ]
    rows += chunk(site_buttons, 3)

    if len(sites) > 5:
        rows.append([Button.inline(t.get("moreSitesBtn"), state.pack("sites"))])

    return rows


def render_sort_picker(state: SearchState, t: Translator) -> ViewResponse:
    """Sort mode picker; tapping one returns to re-sorted results."""
    return ViewResponse(
        buttons=[
            [
                Button.inline(
                    ("✓ " if code == state.sort else "") + t.get(label_key),
                    b"noop" if code == state.sort else replace(state, sort=code, page=1).pack("res"),
                )
                for code, (label_key, _) in SORTS.items()
            ],
            [Button.inline(t.get("backBtn"), state.pack("res"))],
        ],
    )


def render_category_picker(state: SearchState, t: Translator) -> ViewResponse:
    """Category filter picker; tapping one re-runs the search filtered."""
    categories: list[str | None] = [None, *CATEGORY_LABELS]

    buttons = [
        Button.inline(
            ("✓ " if category == state.category else "") + category_label(t, category),
            b"noop"
            if category == state.category
            else replace(state, category=category, page=1).pack("res"),
        )
        for category in categories
    ]

    rows = chunk(buttons, 3)
    rows.append([Button.inline(t.get("backBtn"), state.pack("res"))])

    return ViewResponse(buttons=rows)


def render_page_picker(state: SearchState, pages: int, t: Translator) -> ViewResponse:
    """Grid of page numbers to jump to; any tap returns to the results."""
    buttons = [
        Button.inline(
            f"· {number} ·" if number == state.page else str(number),
            b"noop" if number == state.page else replace(state, page=number).pack("res"),
        )
        for number in range(1, min(pages, 30) + 1)
    ]

    rows = chunk(buttons, 5)
    rows.append([Button.inline(t.get("backBtn"), state.pack("res"))])

    return ViewResponse(buttons=rows)


def render_site_picker(
    state: SearchState,
    sites: dict[str, dict[str, str]],
    t: Translator,
) -> ViewResponse:
    """Expanded list of per-site inline searches with a back button."""
    buttons = [
        Button.switch_inline(
            sites[key]["website"],
            query=f"!{key} {state.query}",
            same_peer=True,
        )
        for key in sites
    ]

    rows = chunk(buttons, 2)
    rows.append([Button.inline(t.get("backBtn"), state.pack("res"))])

    return ViewResponse(buttons=rows)
