# AI Link Radar Bot

A Telegram bot that collects links from chats, deduplicates them, identifies the source platform, fetches page titles, and saves everything as structured Markdown cards.

Prepared for **OpenAI Build Week** in the **Work & Productivity** track.

## Overview

AI Link Radar Bot turns Telegram into a personal link inbox. Send the bot any message containing a link, and it will:

- Recognize and parse the URL
- Deduplicate against your existing collection
- Auto-tag the platform (e.g. `x.com`, `github.com`, `bbc.com`)
- Fetch the page title and write it back to the card
- Save the result as a Markdown card in a local `links.md` file

You can then browse, search, tag, and annotate your link collection directly from Telegram.

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/daisylovekris/ai-link-radar-bot.git
cd ai-link-radar-bot
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env` and paste your Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather)).

### 4. Run

```bash
python tg_bot_ignition.py
```

You should see:

```text
[系统状态] TG 机器人已启动，正在监听链接并保存为 Markdown...
```

Stop the bot with `Ctrl + C`.

## Project Structure

```text
.env.example          Environment template (BOT_TOKEN)
.gitignore            Prevents sensitive files from being committed
LICENSE               MIT License
README.md             This file
links.example.md      Example link collection
requirements.txt      Python dependencies
tg_bot_ignition.py    Bot main program
```

## Markdown Card Format

Every saved link becomes a structured card in `links.md`:

```markdown
## 2026-05-10 04:16:26

- 标题：待抓取
- 来源：@example_user
- 平台：x.com
- 链接：https://x.com/...
- 标签：#待分类
- 状态：待脱水
- 备注：待补充

---
```

## Title Fetching

When a new link is saved, the bot automatically tries to fetch the page title:

1. Save the card with title set to "待抓取"
2. Attempt to fetch the page title via HTTP
3. On success, write the real title back into the card
4. On failure, keep "待抓取" — you can retry later with `/fetch_title`

Normal web pages usually work directly. Platforms like X/Twitter or LinuxDo may require the Jina Reader fallback due to login walls or anti-scraping measures. The bot tries the fallback automatically.

## Commands

| Command | Description |
|---|---|
| `/help` | Show usage instructions |
| `/health` | Check if the bot is online |
| `/stats` | Link collection statistics (total, pending, processed, completion rate) |
| `/recent [n]` | Show the last N links (default 3, max 10) |
| `/all_links [page]` | Browse all links with pagination |
| `/todo [page]` | Browse pending (unprocessed) links |
| `/todo_links [page]` | Quick list of pending link URLs |
| `/done_links [page]` | Quick list of processed link URLs |
| `/done <id>` | Mark a link as processed |
| `/undo <id>` | Revert a processed link back to pending |
| `/platforms` | Show link counts per platform |
| `/platform <name> [page]` | Browse links from a specific platform |
| `/search <keyword>` | Search across titles, tags, platforms, and notes |
| `/card <id>` | View the full Markdown card for a link |
| `/tag <id> <tag>` | Add or update the tag on a link |
| `/note <id> <text>` | Add or update the note on a link |
| `/fetch_title <id>` | Retry title fetching for a specific link |

## Safety and Privacy

- **Link records are stored locally** in `links.md`.
- **Tokens are kept in `.env`**, which is `.gitignore`d and never committed.
- **The bot communicates with the Telegram Bot API**, and title fetching may request the target webpage or an optional fallback reader service.
- **No analytics and no telemetry** are included.
- **Deduplication** prevents accidental duplicates from cluttering your inbox.
- This bot is a personal tool, not a multi-user service. Use it in private chats you control.

## Roadmap

- **AI summarization** — Call an LLM API to auto-generate summaries and mark links as processed.
- **Smarter scraping** — Platform-specific fetch strategies for X, Reddit, YouTube, and other sites.
- **Export formats** — Obsidian-compatible frontmatter, CSV export, or integration with note-taking tools.

## License

[MIT](LICENSE)
