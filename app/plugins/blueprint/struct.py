"""Structure of text message"""

# Structure of search results
search_struct = """
<b>{count}. {title}</b>

💾 {size}, 🟢 {seeders}, 🔴 {leechers}

{link_str}: /getLink_{torrent_id}
"""

# Structure of torrent content
content_struct = """
<b>✨ {title}</b>

{size_str}: {size}
{seeders_str}: {seeders}
{leechers_str}: {leechers}
{uploaded_on_str}: {uploaded_on}

<b>{magnet_link_str}: </b><code>{magnet}</code>
"""
