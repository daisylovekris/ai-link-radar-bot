# AI Link Radar Bot

A Telegram bot that turns saved URLs into structured Markdown cards, with local organization tools and an optional GPT-5.6 metadata triage workflow.

Prepared for **OpenAI Build Week** in the **Work & Productivity** track.

## Overview

AI Link Radar Bot turns Telegram into a personal link inbox. Send the bot any message containing a link, and it will:

- Recognize and parse the first URL in the message
- Deduplicate against your existing collection
- Auto-tag the platform (e.g. `x.com`, `github.com`, `bbc.com`)
- Fetch the page title and write it back to the card
- Save the result as a Markdown card in a local `links.md` file

You can then browse, search, tag, and annotate your link collection directly from Telegram. An optional `/triage <id>` command sends saved card metadata to GPT-5.6 for a focused assessment.

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

Edit `.env`:

```ini
BOT_TOKEN=your_telegram_bot_token_here
LINKS_FILE=links.md
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6
```

- `BOT_TOKEN` is required. Get one from [@BotFather](https://t.me/BotFather).
- `OPENAI_API_KEY` is only used by `/triage`. Without it, all other commands continue to work normally.
- `OPENAI_MODEL` defaults to `gpt-5.6`.

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
.env.example                              Environment template
.gitignore                                Prevents sensitive files from being committed
.github/ISSUE_TEMPLATE/                   Privacy-aware issue forms
docs/demo-script.md                       Build Week demo script
docs/release-notes-v0.1.0.md              First public release notes
LICENSE                                   MIT License
README.md                                 This file
links.example.md                          Example link collection
requirements.txt                          Python dependencies
tests/                                    pytest coverage
tg_bot_ignition.py                        Bot main program
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

After running `/triage <id>` successfully, the same card gains three additional fields:

```markdown
- AI 研判：<assessment>
- 价值判断：<why it matters>
- 下一步：<one next action>
```

Running `/triage` again on the same card replaces the previous three fields rather than appending duplicates.

## Title Fetching

When a new link is saved, the bot automatically tries to fetch the page title:

1. Save the card with title set to "待抓取"
2. Attempt to fetch the page title via HTTP
3. On success, write the real title back into the card
4. On failure, keep "待抓取" — you can retry later with `/fetch_title`

Normal web pages usually work directly. Platforms like X/Twitter or LinuxDo may require the Jina Reader fallback due to login walls or anti-scraping measures. The bot tries the fallback automatically.

## GPT-5.6 Metadata Triage

The `/triage <id>` command sends saved card metadata to GPT-5.6 and writes back a structured three-field result.

What is sent:

- title
- URL
- platform
- tag
- note
- status

What is **not** done:

- `/triage` does **not** fetch or send the full webpage content to OpenAI.
- `/triage` does **not** claim that GPT-5.6 has read the article.

How it works:

- Uses the OpenAI Responses API.
- Uses strict JSON Schema Structured Outputs.
- Requests are sent with `store=False`.
- Card metadata is explicitly marked as **untrusted data** — the model is instructed not to follow any instructions contained inside field values.
- Model output is validated for type, length, and Markdown safety before being written back.
- Updates use a same-directory temporary file and `os.replace` for atomic replacement.

If the OpenAI SDK, API key, permissions, or balance are missing, only `/triage` is affected. All other commands continue to work.

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
| `/triage <id>` | Ask GPT-5.6 to assess saved metadata and write back three fields |

## OpenAI Build Week Work

### Pre-existing foundation

- Telegram bot workflow
- local Markdown card storage
- URL collection and organization commands
- title fetching and fallback behavior

### Build Week improvements

- public repository cleanup
- public README and release documentation
- three-minute demo script
- safer title-fetching errors
- import-safe `run_bot`
- URL parsing and dedup tests
- privacy-aware Issue Forms
- GPT-5.6 metadata triage
- untrusted metadata boundaries
- atomic triage writeback
- mocked API tests

### How OpenAI tools are used

- **Codex** supported repository inspection, focused implementation, test creation, documentation, and review iterations.
- **GPT-5.6** powers the optional `/triage` workflow and returns an assessment, why it matters, and one next action.

## Test Status

**93 passed, 2 xfailed, 0 failed.**

The two `xfail` cases are known limitations explicitly recorded as strict expected failures:

- **Trailing punctuation may remain attached to an extracted URL** — the current URL regex includes trailing non-whitespace characters.
- **Substring matching may report a false duplicate** — the current duplicate check uses plain substring matching in the saved file.

OpenAI calls in tests are fully mocked. Running the test suite does not consume API credits and does not touch a real `links.md`.

## Safety and Privacy

- `.env` and the real `links.md` are excluded from version control.
- Do not commit tokens, API keys, cookies, sessions, private URLs, or personal archives.
- The bot communicates with the **Telegram Bot API**.
- Title fetching may request the target webpage or an optional fallback reader service.
- `/triage` only sends card metadata to OpenAI when the user actively issues the command.
- `/triage` requests are sent with `store=False`.
- This project does **not** claim zero retention or full offline operation.
- No analytics and no telemetry are included.
- This bot is a personal tool, not a multi-user service. Use it in private chats you control.

## Known Limitations

- URL trailing punctuation cleanup is pending.
- Duplicate detection still uses substring matching.
- Title fetching currently runs synchronously.
- The Markdown archive is designed mainly for personal-scale use.
- `/triage` assesses metadata only — it is not a full-page summary.

## Roadmap

- exact URL normalization and deduplication
- shared Markdown field safety
- full-page extraction followed by a future `/summarize`
- Obsidian-oriented export
- optional scheduled digest

## License

[MIT](LICENSE)
