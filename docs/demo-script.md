# AI Link Radar Bot — Build Week Demo Script

**Total time: ~3 minutes**

---

## Opening (0:00 – 0:20)

**Narration:**

> We all collect links throughout the day — articles, research, tools, inspiration. Most of them end up lost in Telegram chats, browser tabs, or sticky notes. AI Link Radar Bot turns your Telegram into a personal link inbox. Send it any URL, and it saves a structured Markdown card with the title, platform, and status — ready for your next AI workflow.

**Screen:** Show the Telegram chat with the bot.

---

## Step 1 — Send a URL (0:20 – 0:45)

**Action:**
Type and send this message in the Telegram chat:

```
https://example.com/article
```

**Narration:**

> I just dropped a link into the chat. The bot receives it immediately.

**Screen:** Show the message appearing in Telegram.

---

## Step 2 — Bot saves a Markdown card (0:45 – 1:15)

**Action:**
The bot replies automatically. Show the card that appears:

```
## 2026-07-17 10:30:00

- 标题：Example Article Title
- 来源：@example_user
- 平台：example.com
- 链接：https://example.com/article
- 标签：#待分类
- 状态：待脱水
- 备注：待补充
```

**Narration:**

> The bot instantly creates a structured Markdown card. It deduplicates — if I send the same link again, it won't be saved twice. It detects the platform automatically. And here's the key part: it fetches the page title and writes it back into the card, so I don't have to do that manually.

---

## Step 3 — Platform detection and title fetching (1:15 – 1:45)

**Action:**
Send a second URL:

```
https://x.com/example/status/1234567890
```

**Narration:**

> Now I'm sending a Twitter link. The bot identifies it as `x.com` and tries to fetch the title. For X and other platforms with login walls, the bot uses a fallback reader to improve success rates. If both fail, the card still saves — the title stays as "待抓取" and I can retry later with `/fetch_title`.

**Screen:** Show the saved card with the detected platform.

---

## Step 4 — Browse with /recent (1:45 – 2:10)

**Action:**
Type `/recent` and send.

**Narration:**

> I can quickly check what I've saved recently with `/recent`. It shows the last three links by default — titles, platforms, and URLs at a glance.

**Screen:** Show the `/recent` response listing both saved links.

---

## Step 5 — Search and filter (2:10 – 2:40)

**Action:**
Type `/platforms` and send.

**Narration:**

> `/platforms` shows me a breakdown by source — how many links from X, from blogs, from news sites. I can also search across all cards with `/search` or browse a specific platform with `/platform`.

**Action:**
Type `/search example` and send.

**Narration:**

> Search scans titles, tags, platforms, and notes — so I can find that one article I saved last week without scrolling through a long list.

**Screen:** Show the search results.

---

## Closing (2:40 – 3:00)

**Narration:**

> AI Link Radar Bot is a lightweight personal tool — no cloud storage, no analytics, everything stays on your machine in a local Markdown file. It's designed to be the first step in a personal AI information workflow: collect links, organize them, and eventually feed them into an AI summarizer or note-taking system like Obsidian.
>
> This is my project for OpenAI Build Week, in the Work & Productivity track. The code is open source. Thanks for watching.

**Screen:** Show the GitHub repo page with the README.

---

## Example URLs for the demo

| URL | Platform |
|---|---|
| `https://example.com/article` | example.com |
| `https://x.com/example/status/1234567890` | x.com |

## Commands used in the demo

| Command | What it does |
|---|---|
| (send any URL) | Bot saves a Markdown card |
| `/recent` | Show last 3 saved links |
| `/platforms` | Show link counts per platform |
| `/search <keyword>` | Search across all card fields |
| `/fetch_title <id>` | Retry title fetching for a specific link |
