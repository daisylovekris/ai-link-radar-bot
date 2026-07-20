# AI Link Radar Bot — OpenAI Build Week Demo Script

**Total time: ~2 minutes 55 seconds**

---

## Recording Rules

- Use only synthetic or public demonstration data.
- The final recording uses a funded OpenAI Platform key to run `/triage` once for real.
- Do not show `.env`, API keys, private Telegram content, or a personal `links.md`.
- Do not fabricate GPT-5.6 success results.
- Set the YouTube video to public.
- Total runtime is under 3 minutes.

---

## Opening — 0:00–0:15

**Narration:**

> We all collect links throughout the day — articles, research, tools, inspiration. AI Link Radar Bot turns Telegram into a personal information inbox: send a URL, keep a readable local archive, and ask GPT-5.6 for a focused next step when needed.

**Screen:** Show the Telegram chat with the bot.

---

## Save a URL — 0:15–0:40

**Action:**
Type and send this message in the Telegram chat:

```
https://example.com
```

**Narration:**

> I just dropped a link into the chat. The bot receives it immediately, runs a duplicate check, detects the platform, and saves a structured Markdown card. It also tries to fetch the page title. If title fetching fails, the card is still saved — I can retry later with `/fetch_title`.

**Screen:** Show the message appearing in Telegram and the bot's reply.

---

## Show the Markdown Card — 0:40–1:00

**Action:**
Show the saved card:

```
## 2026-07-17 10:30:00

- 标题：Example Article Title
- 来源：@example_user
- 平台：example.com
- 链接：https://example.com
- 标签：#待分类
- 状态：待脱水
- 备注：待补充
```

**Narration:**

> This is a structured Markdown card. It includes the title, source, platform, link, tag, status, and note. The archive itself is stored locally in a single Markdown file.

**Screen:** Show the card in the local Markdown file.

---

## GPT-5.6 Metadata Triage — 1:00–1:45

**Action:**
Type `/triage 1` and send.

The values below show the format only. Use the actual GPT-5.6 result in the final recording.

**Screen:** Show the three fields written back to the card:

```
- AI 研判：Example article about demonstration workflows
- 价值判断：Useful as a reference for structured output demos
- 下一步：Bookmark for future Build Week walkthroughs
```

**Narration:**

> This is the GPT-5.6 feature in the product. I ran `/triage 1`, and the bot wrote back three fields: an assessment, why it matters, and one next action. It only sent the card metadata — title, URL, platform, tag, note, and status. It did not read the full webpage. The metadata is treated as untrusted data, so the model is instructed not to follow any instructions inside field values. The response uses Structured Outputs with a strict JSON schema, and the request is sent with `store=False`. The result is validated and then written back atomically.

**Screen:** Show the updated card with the three new fields.

---

## Browse and Search — 1:45–2:15

**Action:**
Type `/recent` and send.

**Narration:**

> I can quickly check what I've saved recently with `/recent`.

**Action:**
Type `/search example` and send.

**Narration:**

> And I can search across all cards with `/search`.

**Screen:** Show the `/recent` and `/search` responses.

---

## Explain OpenAI Tool Usage — 2:15–2:40

**Screen:** Show the GitHub repository page, `tests/` directory, closed Issues, and recent commits.

**Narration:**

> This project used two OpenAI tools. Codex supported repository inspection, focused implementation, test creation, documentation, and review iterations. GPT-5.6 powers the optional `/triage` workflow. The current test suite shows 93 passed, 2 xfailed, 0 failed.

**Screen:** Show the test output and the repository structure.

---

## Closing — 2:40–2:55

**Narration:**

> AI Link Radar Bot is a small, privacy-aware productivity tool: collect a URL, keep a readable local archive, and ask GPT-5.6 for a focused next step when needed. It is open source and built for the Work & Productivity track.

**Screen:** Show the GitHub repo page with the README.

---

## Example URLs for the demo

| URL | Platform |
|---|---|
| `https://example.com` | example.com |

## Commands used in the demo

| Command | What it does |
|---|---|
| (send any URL) | Bot saves a Markdown card |
| `/triage <id>` | GPT-5.6 metadata triage, writes back three fields |
| `/recent` | Show recently saved links |
| `/search <keyword>` | Search across all card fields |

---

## Final Recording Checklist

- synthetic archive
- one real GPT-5.6 request
- secrets hidden
- metadata-only statement
- Codex usage explained
- GPT-5.6 usage explained
- 93 passed, 2 xfailed, 0 failed shown
- under 3 minutes
- public YouTube
- Devpost contains the repository URL and Codex `/feedback` Session ID
