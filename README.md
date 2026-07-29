<p align="center">
<a href="https://github.com/hemantapkh/torrenthunt/stargazers">
<img src="https://img.shields.io/github/stars/hemantapkh/torrenthunt" alt="Stars">
</a>
<a href="https://github.com/hemantapkh/torrenthunt/fork">
<img src="https://img.shields.io/github/forks/hemantapkh/torrenthunt.svg" alt="Forks"/>
</a>
<a href="https://github.com/hemantapkh/torrenthunt/graphs/contributors">
<img src="https://img.shields.io/github/contributors/hemantapkh/torrenthunt.svg" alt="Contributors" />
</a>
<a href="https://github.com/hemantapkh/torrenthunt/blob/main/LICENSE">
<img src="https://img.shields.io/github/license/hemantapkh/torrenthunt" alt="License" />
</a>
<img src="https://img.shields.io/badge/python-3.14+-blue?logo=python&logoColor=white" alt="Python 3.14+" />
</p>

<p align="center">
<img src="images/torrenthunt.jpg" align="center" height=365 alt="Torrent Hunt Bot" />
</p>

<p align="center">
<a href="https://t.me/torrenthuntbot?start=githubReadme">
<img src="https://img.shields.io/badge/Telegram-@torrenthuntbot-2CA5E0?logo=telegram&logoColor=white&style=for-the-badge" alt="Open in Telegram" />
</a>
</p>

<h1 align='center'>🔍 Torrent Hunt Bot</h1>

Torrent Hunt is a Telegram bot for searching torrents. Send it a keyword and
it searches your configured indexers and delivers the magnet links right
inside Telegram, in your language.

# ✨ Features

- **Search** any keyword, browse results in a single message, and tap a title to get its magnet link
- **Filter & sort** by category, seeders, size, or upload date; jump to any page
- **Inline search** in any chat (`@torrenthuntbot <query>`), per-site too
- **Bookmarks** to save torrents for later
- **19 languages** and an optional restricted mode for adult content

# 🔌 Search Provider

Torrent Hunt supports [Jackett](https://github.com/Jackett/Jackett) and [Prowlarr](https://github.com/Prowlarr/Prowlarr) as its search providers. Every indexer you configure in them becomes searchable from the bot.

# 🗣️ Languages

Torrent Hunt Bot speaks 19 languages.

<details>
<summary>Full list & translation credits</summary>

- Arabic (Added by [Omar Khalid](https://github.com/omvrkhvlid))
- Bengali (Checked and fixed by [sobuj53](https://github.com/sobuj53))
- Belarusian
- Catalan
- Dutch
- English (Original)
- French (Checked and fixed by [xav35000](https://github.com/xav35000))
- German
- Hindi
- Italian (Checked and fixed by [bacchilega](https://github.com/bacchilega))
- Korean
- Malay
- Nepali
- Polish (Checked and fixed by [Oskar](https://discordapp.com/users/171642532818714624))
- Portuguese
- Russian
- Spanish
- Turkish (Checked and fixed by [Berce](https://github.com/must4f))
- Ukrainian

</details>

# ⚒️ Deployment

### Run locally

```bash
# 1. Configure: copy sample.env to .env and fill in the values
cp sample.env .env

# 2. Install dependencies and run
uv sync
uv run app/main.py
```

### Docker

```bash
docker build -t torrenthunt .
docker run --env-file .env torrenthunt
```

### Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/hemantapkh/torrenthunt)

---

❇️ Author/Maintainer: [Hemanta Pokharel](https://github.com/hemantapkh/) [[✉️](mailto:hemantapkh@yahoo.com) [💬](https://t.me/hemantapkh)]
