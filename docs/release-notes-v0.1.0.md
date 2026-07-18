# AI Link Radar Bot v0.1.0

## Overview

AI Link Radar Bot is a lightweight Telegram tool that turns chat into a personal link inbox. A user sends a URL to the bot. The bot recognizes the link, deduplicates it against the local collection, detects the platform, attempts to fetch the page title, and saves everything as a structured Markdown card on the local machine. The collection can then be browsed, searched, tagged, and annotated with notes and workflow status directly from Telegram.

This is the first public release.

## Highlights

### Core functionality

- **Telegram URL collection** — The bot accepts any message containing a URL and turns it into a structured card.
- **Local Markdown card storage** — Each link is stored as a Markdown block in a single local file. The storage is file-based, local-first, and designed for personal use.
- **Substring-based duplicate detection** — Before saving, the bot checks whether the URL already appears as a substring in the saved file. This prevents many accidental duplicates but can occasionally flag a shorter URL as a duplicate of a longer one. See Known limitations.
- **Platform detection** — The source host is parsed and tagged automatically (e.g. `x.com`, `github.com`, `bbc.com`).
- **Automatic title fetching** — The bot visits the target page and writes the title into the saved card.
- **Jina Reader fallback** — When a direct fetch fails, the bot retries through an optional fallback reader for pages with login walls or anti-scraping behavior.
- **Safe title-fetching failure classification** — Fetch failures are classified into readable categories (timeout, 403, 404, no title, fallback failure) without breaking the save flow.

### Commands

- `/recent` — Recently saved links
- `/todo` — Pending (unprocessed) cards
- `/todo_links` — Pending link list
- `/done_links` — Processed link list
- `/done <id>` / `/undo <id>` — Toggle processed status
- `/platforms` and `/platform <name>` — Browse by source platform
- `/search <keyword>` — Search across card fields
- `/card <id>` — View full card
- `/tag <id> <tag>` / `/note <id> <text>` — Annotate cards
- `/fetch_title <id>` — Retry title fetch for a specific card
- `/stats` / `/health` / `/help` — Status and documentation

### Distribution and contribution

- **Privacy-aware GitHub Issue Forms** — Bug reports, feature requests, and documentation forms all include explicit safety reminders. Blank issues are disabled.
- **Build Week demo script** — A three-minute walkthrough with narration and screen cues.
- **pytest coverage** — URL parsing, platform detection, card parsing, and deduplication are covered. The bot module is import-safe under test.

## Build Week improvements

This release was prepared during OpenAI Build Week in the Work & Productivity track.

### Pre-existing project foundation

The following existed before Build Week and are part of the original project design:

- Telegram bot workflow
- Markdown card storage and archive semantics
- Command set and local collection behavior (recent, todo, done, platform, search, tag, note)
- Duplicate detection and platform detection
- Title fetching with fallback

### OpenAI Build Week improvements

The following were added or improved during Build Week to prepare a public, reviewable release:

- **Public repository cleanup** — Sensitive paths and personal archives were excluded from the repository.
- **Public-facing README** — Installation, project structure, card format, title fetching behavior, command table, safety and privacy, and roadmap.
- **Three-minute demo script** — `docs/demo-script.md` with timing, narration, and screen cues.
- **Safer title-fetching error handling** — A safe failure classification function and handler-level exception boundaries were added. The existing fallback order was preserved.
- **Import-safe run_bot entry point** — The polling loop was extracted into a `run_bot()` function and guarded with `if __name__ == "__main__"`. The module can now be imported without starting polling, which enables testing and future reuse.
- **URL parsing and deduplication tests** — `tests/test_url_parsing.py` and `tests/test_dedup.py` cover regex behavior, platform detection, card parsing, and deduplicate logic using temporary files and monkeypatching. Fake credentials are injected through `tests/conftest.py`.
- **Privacy-aware GitHub Issue Forms** — `.github/ISSUE_TEMPLATE/` contains three forms, all with safety reminders and a required privacy confirmation checkbox.
- **Release documentation** — This document.

## Test status

**20 passed, 2 xfailed, 0 failed.**

The two `xfail` cases are known limitations explicitly recorded as strict expected failures:

- **Trailing punctuation may remain attached to extracted URLs** — The current URL regex includes trailing non-whitespace characters. A sentence-ending period immediately after a URL is treated as part of the URL. This is covered by `tests/test_url_parsing.py::test_url_trailing_punctuation`.
- **Substring matching may cause a false duplicate result** — The current duplicate check uses plain substring matching in the saved file. A shorter URL may be incorrectly flagged as a duplicate when it is a substring of a different, longer URL. This is covered by `tests/test_dedup.py::test_substring_not_false_positive`.

Both are strict `xfail`: if either is fixed in the future, the test suite will surface the change as an unexpected pass.

## Installation

1. Clone the repository and change into the project directory.
2. Create a Python virtual environment and activate it.
3. Install dependencies from `requirements.txt`.
4. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
5. Edit `.env` and set `BOT_TOKEN` to a valid Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather)).
6. Run the bot:
   ```bash
   python tg_bot_ignition.py
   ```

Stop the bot with `Ctrl + C`.

## Known limitations

- **Title fetching depends on target page behavior.** Not every page returns a parseable HTML title.
- **X / Twitter, LinuxDo, login walls, and anti-bot pages** may fail both the direct fetch and the fallback reader.
- **Title fetching currently runs synchronously.** A slow or unresponsive target page can block the bot's response to that message.
- **URL trailing punctuation cleanup remains pending.** See the test status section.
- **Duplicate matching still uses text substring behavior.** See the test status section.
- **Local Markdown storage is designed mainly for personal use.** The storage model is a single file and does not include locking, sharding, or multi-user access control.

## Safety and privacy

- The real `.env` file is excluded from version control.
- The real `links.md` file (the user's actual link archive) is excluded from version control.
- No tokens, cookies, sessions, private URLs, or personal archives should be committed.
- The bot communicates with the **Telegram Bot API** to send and receive messages.
- Title fetching may request the **target website** and, when the direct fetch fails, an **optional fallback reader service**. Users should be aware that these requests are made from the machine running the bot.

## Upgrade notes

v0.1.0 is the first public release. There are no prior public versions to upgrade from and no migration steps are required.

## License

MIT License.
