"""Jackett constants."""

# Aggregated results endpoint; {indexer} is "all" or a single indexer id
RESULTS_ENDPOINT = "/api/v2.0/indexers/{indexer}/results"

# Canonical application categories -> Torznab category ids
CATEGORY_MAP: dict[str, list[int]] = {
    "movies": [2000],
    "tv": [5000],
    "games": [1000, 4050],
    "music": [3000],
    "apps": [4000],
    "anime": [5070],
    "documentaries": [5080],
    "others": [6000],
}
