"""Prowlarr constants."""

# Search results endpoint
RESULTS_ENDPOINT = "/api/v1/search"
INDEXERS_ENDPOINT = "/api/v1/indexer"
TAGS_ENDPOINT = "/api/v1/tag"

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
