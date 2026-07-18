import html
import os
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("没有找到 BOT_TOKEN，请检查 .env 文件。")

bot = telebot.TeleBot(BOT_TOKEN)

print("[系统状态] TG 机器人已启动，正在监听链接并保存为 Markdown...")

X_LINK_PATTERN = re.compile(
    r"https?://(?:www\.)?(?:x\.com|twitter\.com)/[^\s]+"
)

ANY_LINK_PATTERN = re.compile(r"https?://[^\s]+")

LINKS_FILE = Path(os.getenv("LINKS_FILE", "links.md"))


def is_duplicate_link(link: str) -> bool:
    if not LINKS_FILE.exists():
        return False

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    return link in saved_text


def get_platform_from_link(link: str) -> str:
    parsed_url = urlparse(link)
    platform = parsed_url.netloc.lower()

    if platform.startswith("www."):
        platform = platform.removeprefix("www.")

    return platform or "unknown"


def save_link(link: str, username: str | None) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = username or "unknown"
    platform = get_platform_from_link(link)

    markdown_card = f"""## {now}

- 标题：待抓取
- 来源：@{user}
- 平台：{platform}
- 链接：{link}
- 标签：#待分类
- 状态：待脱水
- 备注：待补充

---

"""

    with LINKS_FILE.open("a", encoding="utf-8") as file:
        file.write(markdown_card)


def count_saved_links() -> int:
    if not LINKS_FILE.exists():
        return 0

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    return saved_text.count("- 链接：")


def get_recent_links(limit: int = 3) -> list[str]:
    if not LINKS_FILE.exists():
        return []

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    cards = [card.strip() for card in saved_text.split("---") if card.strip()]
    return cards[-limit:]


def get_all_links() -> list[str]:
    if not LINKS_FILE.exists():
        return []

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    cards = [card.strip() for card in saved_text.split("---") if card.strip()]
    return cards


def get_card_by_index(card_index: int) -> tuple[bool, str]:
    all_cards = get_all_links()

    if not all_cards:
        return False, "当前 links.md 里还没有保存任何链接。"

    if card_index < 1 or card_index > len(all_cards):
        return False, f"序号无效。当前全部链接共有 {len(all_cards)} 条，请输入 /card 1 到 /card {len(all_cards)}。"

    return True, all_cards[card_index - 1]


def parse_command_limit(
    message_text: str | None,
    default: int = 3,
    maximum: int = 10,
) -> tuple[int, str | None]:
    if not message_text:
        return default, None

    parts = message_text.split()

    if len(parts) < 2:
        return default, None

    try:
        limit = int(parts[1])
    except ValueError:
        return default, f"数量无效，已按默认 {default} 条显示。"

    if limit < 1:
        return default, f"数量不能小于 1，已按默认 {default} 条显示。"

    if limit > maximum:
        return maximum, f"最多只能显示 {maximum} 条，已按 {maximum} 条显示。"

    return limit, None


def parse_command_page(message_text: str | None, default: int = 1) -> tuple[int, str | None]:
    if not message_text:
        return default, None

    parts = message_text.split()

    if len(parts) < 2:
        return default, None

    try:
        page = int(parts[1])
    except ValueError:
        return default, f"页码无效，已显示第 {default} 页。"

    if page < 1:
        return default, f"页码不能小于 1，已显示第 {default} 页。"

    return page, None


def get_todo_links() -> list[str]:
    if not LINKS_FILE.exists():
        return []

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    cards = [card.strip() for card in saved_text.split("---") if card.strip()]
    return [card for card in cards if "- 状态：待脱水" in card]


def get_done_links() -> list[str]:
    if not LINKS_FILE.exists():
        return []

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    cards = [card.strip() for card in saved_text.split("---") if card.strip()]
    return [card for card in cards if "- 状态：已脱水" in card]


def extract_link_from_card(card: str) -> str:
    for line in card.splitlines():
        if line.startswith("- 链接："):
            return line.replace("- 链接：", "", 1).strip()

    return ""


def extract_platform_from_card(card: str) -> str:
    for line in card.splitlines():
        if line.startswith("- 平台："):
            return line.replace("- 平台：", "", 1).strip()

    link = extract_link_from_card(card)

    if link:
        return get_platform_from_link(link)

    return "unknown"


def extract_title_from_card(card: str) -> str:
    for line in card.splitlines():
        if line.startswith("- 标题："):
            return line.replace("- 标题：", "", 1).strip()

    return "待抓取"


def search_cards(keyword: str) -> list[tuple[int, str]]:
    all_cards = get_all_links()
    normalized_keyword = keyword.lower()

    return [
        (index + 1, card)
        for index, card in enumerate(all_cards)
        if normalized_keyword in card.lower()
    ]


def get_platform_stats() -> dict[str, int]:
    all_cards = get_all_links()
    platform_counts: dict[str, int] = {}

    for card in all_cards:
        platform = extract_platform_from_card(card)
        platform_counts[platform] = platform_counts.get(platform, 0) + 1

    return dict(sorted(platform_counts.items()))


def get_links_by_platform(platform_name: str) -> list[str]:
    all_cards = get_all_links()
    normalized_platform = platform_name.lower().removeprefix("www.")

    return [
        card
        for card in all_cards
        if extract_platform_from_card(card).lower().removeprefix("www.") == normalized_platform
    ]


def get_indexed_links_by_platform(platform_name: str) -> list[tuple[int, str]]:
    all_cards = get_all_links()
    normalized_platform = platform_name.lower().removeprefix("www.")

    return [
        (index + 1, card)
        for index, card in enumerate(all_cards)
        if extract_platform_from_card(card).lower().removeprefix("www.") == normalized_platform
    ]


def classify_title_fetch_failure(message: str) -> str:
    lower = message.lower()

    if "timed out" in lower or "timeout" in lower:
        return "请求超时"

    if "403" in lower or "forbidden" in lower:
        return "页面拒绝访问"

    if "404" in lower or "not found" in lower:
        return "页面不存在"

    if "没有在网页中找到标题" in lower or "没有找到标题" in lower or "没有返回内容" in lower:
        return "页面中没有可识别标题"

    return "网络或页面访问异常"


def extract_title_from_html(page_html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", page_html, flags=re.IGNORECASE | re.DOTALL)

    if not match:
        return ""

    title = match.group(1)
    title = re.sub(r"\s+", " ", title).strip()
    return html.unescape(title)


def build_jina_reader_urls(link: str) -> list[str]:
    normalized_link = re.sub(r"^https?://", "", link).strip()
    return [f"https://r.jina.ai/http://{normalized_link}"]


def extract_title_from_jina_markdown(markdown_text: str) -> str:
    title_match = re.search(r"^Title:\s*(.+)$", markdown_text, flags=re.MULTILINE)

    if title_match:
        return title_match.group(1).strip()

    heading_match = re.search(r"^#\s+(.+)$", markdown_text, flags=re.MULTILINE)

    if heading_match:
        return heading_match.group(1).strip()

    return ""


def fetch_title_with_jina(link: str) -> tuple[bool, str]:
    last_error = "Jina Reader 没有返回可用内容。"

    for jina_url in build_jina_reader_urls(link):
        try:
            response = requests.get(jina_url, timeout=20)
            response.raise_for_status()
        except requests.RequestException as error:
            last_error = f"Jina Reader 抓取失败：{error}"
            continue

        title = extract_title_from_jina_markdown(response.text)

        if title:
            return True, title

        last_error = "Jina Reader 返回了内容，但没有找到标题。"

    return False, last_error


def fetch_page_title_with_fallback(link: str) -> tuple[bool, str]:
    success, result = fetch_page_title(link)

    if success:
        return True, result

    first_error = result
    jina_success, jina_result = fetch_title_with_jina(link)

    if jina_success:
        return True, jina_result

    return False, f"普通抓取失败：{first_error}\nJina Reader 兜底失败：{jina_result}"


def fetch_page_title(link: str) -> tuple[bool, str]:
    try:
        response = requests.get(
            link,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            },
        )
        response.raise_for_status()
    except requests.RequestException as error:
        return False, f"抓取失败：{error}"

    title = extract_title_from_html(response.text)

    if not title:
        return False, "没有在网页中找到标题。"

    return True, title


def update_card_title(card_index: int) -> tuple[bool, str]:
    if not LINKS_FILE.exists():
        return False, "当前 links.md 不存在。"

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    cards = [card.strip() for card in saved_text.split("---") if card.strip()]

    if not cards:
        return False, "当前 links.md 里还没有保存任何链接。"

    if card_index < 1 or card_index > len(cards):
        return False, f"序号无效。当前全部链接共有 {len(cards)} 条，请输入 /fetch_title 1 到 /fetch_title {len(cards)}。"

    target_index = card_index - 1
    target_card = cards[target_index]
    link = extract_link_from_card(target_card)

    if not link:
        return False, "这张卡片里没有找到链接。"

    success, result = fetch_page_title_with_fallback(link)

    if not success:
        return False, result

    if "- 标题：" in target_card:
        updated_card = re.sub(r"^- 标题：.*$", f"- 标题：{result}", target_card, count=1, flags=re.MULTILINE)
    else:
        updated_card = target_card + f"\n- 标题：{result}"

    cards[target_index] = updated_card
    updated_text = "\n\n---\n\n".join(cards) + "\n\n---\n"
    LINKS_FILE.write_text(updated_text, encoding="utf-8")

    return True, result


def update_card_title_by_link(link: str, new_title: str) -> bool:
    if not LINKS_FILE.exists():
        return False

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    cards = [card.strip() for card in saved_text.split("---") if card.strip()]

    for index, card in enumerate(cards):
        for line in card.splitlines():
            if line.startswith("- 链接：") and line.replace("- 链接：", "", 1).strip() == link:
                if "- 标题：" in card:
                    updated = re.sub(
                        r"^- 标题：.*$",
                        f"- 标题：{new_title}",
                        card,
                        count=1,
                        flags=re.MULTILINE,
                    )
                    cards[index] = updated
                    LINKS_FILE.write_text(
                        "\n\n---\n\n".join(cards) + "\n\n---\n",
                        encoding="utf-8",
                    )
                return True

    return False


def update_card_status(
    card_index: int,
    old_status: str,
    new_status: str,
    command_name: str,
) -> tuple[bool, str]:
    if not LINKS_FILE.exists():
        return False, "当前 links.md 不存在。"

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    cards = [card.strip() for card in saved_text.split("---") if card.strip()]
    target_indexes = [index for index, card in enumerate(cards) if f"- 状态：{old_status}" in card]

    if not target_indexes:
        return False, f"当前没有状态为“{old_status}”的链接。"

    if card_index < 1 or card_index > len(target_indexes):
        return False, f"序号无效。当前状态为“{old_status}”的链接共有 {len(target_indexes)} 条，请输入 /{command_name} 1 到 /{command_name} {len(target_indexes)}。"

    target_index = target_indexes[card_index - 1]
    target_card = cards[target_index]
    updated_card = target_card.replace(f"- 状态：{old_status}", f"- 状态：{new_status}", 1)
    cards[target_index] = updated_card

    updated_text = "\n\n---\n\n".join(cards) + "\n\n---\n"
    LINKS_FILE.write_text(updated_text, encoding="utf-8")

    link = extract_link_from_card(updated_card)
    return True, link


def parse_status_index(message_text: str | None, command_name: str) -> tuple[int | None, str | None]:
    if not message_text:
        return None, f"请指定要标记的序号，例如：/{command_name} 1"

    parts = message_text.split()

    if len(parts) < 2:
        return None, f"请指定要标记的序号，例如：/{command_name} 1"

    try:
        index = int(parts[1])
    except ValueError:
        return None, f"序号无效，请输入数字，例如：/{command_name} 1"

    if index < 1:
        return None, f"序号不能小于 1，请输入 /{command_name} 1 或更大的数字。"

    return index, None


def parse_card_index(message_text: str | None) -> tuple[int | None, str | None]:
    return parse_status_index(message_text, "card")


def parse_fetch_title_index(message_text: str | None) -> tuple[int | None, str | None]:
    return parse_status_index(message_text, "fetch_title")


def parse_platform_command(message_text: str | None) -> tuple[str | None, int, str | None]:
    if not message_text:
        return None, 1, "请指定平台名，例如：/platform linux.do"

    parts = message_text.split()

    if len(parts) < 2 or not parts[1].strip():
        return None, 1, "请指定平台名，例如：/platform linux.do"

    platform_name = parts[1].strip().lower().removeprefix("www.")

    if len(parts) < 3:
        return platform_name, 1, None

    try:
        page = int(parts[2])
    except ValueError:
        return platform_name, 1, "页码无效，已显示第 1 页。"

    if page < 1:
        return platform_name, 1, "页码不能小于 1，已显示第 1 页。"

    return platform_name, page, None


def parse_search_command(message_text: str | None) -> tuple[str | None, str | None]:
    if not message_text:
        return None, "请填写搜索关键词，例如：/search AI工具"

    parts = message_text.split(maxsplit=1)

    if len(parts) < 2 or not parts[1].strip():
        return None, "请填写搜索关键词，例如：/search AI工具"

    return parts[1].strip(), None


def parse_note_command(message_text: str | None) -> tuple[int | None, str | None, str | None]:
    if not message_text:
        return None, None, "请指定链接序号和备注内容，例如：/note 1 这条值得后续脱水。"

    parts = message_text.split(maxsplit=2)

    if len(parts) < 2:
        return None, None, "请指定链接序号和备注内容，例如：/note 1 这条值得后续脱水。"

    try:
        index = int(parts[1])
    except ValueError:
        return None, None, "序号无效，请输入数字，例如：/note 1 这条值得后续脱水。"

    if index < 1:
        return None, None, "序号不能小于 1，请输入 /note 1 或更大的数字。"

    if len(parts) < 3 or not parts[2].strip():
        return None, None, "请填写备注内容，例如：/note 1 这条值得后续脱水。"

    return index, parts[2].strip(), None


def update_card_note(card_index: int, note: str) -> tuple[bool, str]:
    if not LINKS_FILE.exists():
        return False, "当前 links.md 不存在。"

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    cards = [card.strip() for card in saved_text.split("---") if card.strip()]

    if not cards:
        return False, "当前 links.md 里还没有保存任何链接。"

    if card_index < 1 or card_index > len(cards):
        return False, f"序号无效。当前全部链接共有 {len(cards)} 条，请输入 /note 1 到 /note {len(cards)}。"

    target_index = card_index - 1
    target_card = cards[target_index]

    if "- 备注：" in target_card:
        updated_card = re.sub(r"^- 备注：.*$", f"- 备注：{note}", target_card, count=1, flags=re.MULTILINE)
    else:
        updated_card = target_card + f"\n- 备注：{note}"

    cards[target_index] = updated_card
    updated_text = "\n\n---\n\n".join(cards) + "\n\n---\n"
    LINKS_FILE.write_text(updated_text, encoding="utf-8")

    link = extract_link_from_card(updated_card)
    return True, link


def parse_tag_command(message_text: str | None) -> tuple[int | None, str | None, str | None]:
    if not message_text:
        return None, None, "请指定链接序号和标签，例如：/tag 1 #AI工具"

    parts = message_text.split(maxsplit=2)

    if len(parts) < 2:
        return None, None, "请指定链接序号和标签，例如：/tag 1 #AI工具"

    try:
        index = int(parts[1])
    except ValueError:
        return None, None, "序号无效，请输入数字，例如：/tag 1 #AI工具"

    if index < 1:
        return None, None, "序号不能小于 1，请输入 /tag 1 或更大的数字。"

    if len(parts) < 3 or not parts[2].strip():
        return None, None, "请填写标签，例如：/tag 1 #AI工具"

    tag = parts[2].strip()

    if not tag.startswith("#"):
        tag = f"#{tag}"

    return index, tag, None


def update_card_tag(card_index: int, tag: str) -> tuple[bool, str]:
    if not LINKS_FILE.exists():
        return False, "当前 links.md 不存在。"

    saved_text = LINKS_FILE.read_text(encoding="utf-8")
    cards = [card.strip() for card in saved_text.split("---") if card.strip()]

    if not cards:
        return False, "当前 links.md 里还没有保存任何链接。"

    if card_index < 1 or card_index > len(cards):
        return False, f"序号无效。当前全部链接共有 {len(cards)} 条，请输入 /tag 1 到 /tag {len(cards)}。"

    target_index = card_index - 1
    target_card = cards[target_index]

    if "- 标签：" in target_card:
        updated_card = re.sub(r"^- 标签：.*$", f"- 标签：{tag}", target_card, count=1, flags=re.MULTILINE)
    else:
        updated_card = target_card + f"\n- 标签：{tag}"

    cards[target_index] = updated_card
    updated_text = "\n\n---\n\n".join(cards) + "\n\n---\n"
    LINKS_FILE.write_text(updated_text, encoding="utf-8")

    link = extract_link_from_card(updated_card)
    return True, link


@bot.message_handler(commands=["stats"])
def handle_stats(message):
    total = count_saved_links()
    todo_total = len(get_todo_links())
    done_total = total - todo_total

    completion_rate = (done_total / total * 100) if total else 0

    stats_text = f"""当前 links.md 统计：

- 全部链接：{total} 条
- 待脱水：{todo_total} 条
- 已处理：{done_total} 条
- 完成率：{completion_rate:.1f}%"""

    bot.reply_to(message, stats_text)


@bot.message_handler(commands=["health"])
def handle_health(message):
    bot.reply_to(message, "机器人在线，正在工作。")


@bot.message_handler(commands=["help"])
def handle_help(message):
    help_text = """我是你的链接收集小助手。

【保存】
直接发送链接，我会自动保存成 Markdown 卡片到本地 links.md。
卡片包含：标题、来源、平台、链接、标签、状态、备注。
重复链接不会重复写入。

【常用命令】
/health
检查机器人是否在线。

/stats
查看当前 links.md 的链接统计，包括全部链接、待脱水数量、已处理数量和完成率。

/recent
查看最近保存的 3 条链接。
也可以指定数量，例如：/recent 5
最多显示 10 条。
异常示例：/recent abc、/recent 0、/recent 999

/todo
查看待脱水链接的完整 Markdown 卡片。
默认显示第 1 页，每页最多 5 条。
也可以指定页码，例如：/todo 2
异常示例：/todo abc、/todo 0、/todo 999

/todo_links
查看待脱水链接的简洁列表，只显示链接。
默认显示第 1 页，每页最多 10 条。
也可以指定页码，例如：/todo_links 2
异常示例：/todo_links abc、/todo_links 0、/todo_links 999

/done
把指定待脱水链接标记为已脱水。
例如：/done 3
序号对应 /todo_links 里的待脱水链接序号。

/done_links
查看已脱水链接的简洁列表，只显示链接。
默认显示第 1 页，每页最多 10 条。
也可以指定页码，例如：/done_links 2

/all_links
查看全部链接的简洁列表，只显示链接。
默认显示第 1 页，每页最多 10 条。
也可以指定页码，例如：/all_links 2

/platforms
查看当前素材箱里各个平台的链接数量。

/platform
查看指定平台的链接简洁列表。
例如：/platform linux.do
也可以指定页码，例如：/platform x.com 2

/search
搜索素材箱里的卡片。
例如：/search AI工具
会返回匹配到的全局序号、标题、平台和链接。

/card
查看指定链接的完整 Markdown 卡片。
例如：/card 1
序号对应 /all_links 里的全部链接序号。

/tag
给指定链接添加或更新标签。
例如：/tag 3 #AI工具
序号对应 /all_links 里的全部链接序号。

/fetch_title
尝试抓取指定链接的网页标题，并写回卡片。
普通抓取失败时，会尝试用 Jina Reader 兜底。
例如：/fetch_title 1
序号对应 /all_links 里的全部链接序号。

/note
给指定链接添加或更新备注。
例如：/note 3 这条适合后续脱水成 AI 工具卡。
序号对应 /all_links 里的全部链接序号。

/undo
把指定已脱水链接恢复为待脱水。
例如：/undo 1
序号对应 /done_links 里的已脱水链接序号。

/help
查看这份使用说明。

如果输入了不存在的命令，我会提示你使用 /help 查看可用命令。"""

    bot.reply_to(message, help_text)


@bot.message_handler(commands=["recent"])
def handle_recent(message):
    limit, warning = parse_command_limit(message.text, default=3, maximum=10)
    recent_cards = get_recent_links(limit=limit)

    if not recent_cards:
        bot.reply_to(message, "当前 links.md 里还没有保存任何链接。")
        return

    recent_text = f"最近保存的 {len(recent_cards)} 条链接：\n\n" + "\n\n---\n\n".join(recent_cards)

    if warning:
        recent_text = warning + "\n\n" + recent_text

    bot.reply_to(message, recent_text)


@bot.message_handler(commands=["todo"])
def handle_todo(message):
    todo_cards = get_todo_links()

    if not todo_cards:
        bot.reply_to(message, "当前没有待脱水的链接。")
        return

    total = len(todo_cards)
    page_size = 5
    page, warning = parse_command_page(message.text, default=1)
    total_pages = (total + page_size - 1) // page_size

    if page > total_pages:
        bot.reply_to(message, f"当前只有 {total_pages} 页待脱水链接，请输入 /todo 1 到 /todo {total_pages}。")
        return

    start = (page - 1) * page_size
    end = start + page_size
    visible_cards = todo_cards[start:end]

    todo_text = (
        f"当前共有 {total} 条待脱水链接，正在显示第 {page}/{total_pages} 页：\n\n"
        + "\n\n---\n\n".join(visible_cards)
    )

    if page < total_pages:
        todo_text += f"\n\n下一页：/todo {page + 1}"

    if warning:
        todo_text = warning + "\n\n" + todo_text

    bot.reply_to(message, todo_text)


@bot.message_handler(commands=["todo_links"])
def handle_todo_links(message):
    todo_cards = get_todo_links()

    if not todo_cards:
        bot.reply_to(message, "当前没有待脱水的链接。")
        return

    total = len(todo_cards)
    page_size = 10
    page, warning = parse_command_page(message.text, default=1)
    total_pages = (total + page_size - 1) // page_size

    if page > total_pages:
        bot.reply_to(message, f"当前只有 {total_pages} 页待脱水链接，请输入 /todo_links 1 到 /todo_links {total_pages}。")
        return

    start = (page - 1) * page_size
    end = start + page_size
    visible_cards = todo_cards[start:end]
    visible_links = [extract_link_from_card(card) for card in visible_cards]
    visible_links = [link for link in visible_links if link]

    link_lines = [f"{start + index + 1}. {link}" for index, link in enumerate(visible_links)]
    reply_text = (
        f"当前共有 {total} 条待脱水链接，正在显示第 {page}/{total_pages} 页：\n\n"
        + "\n".join(link_lines)
    )

    if page < total_pages:
        reply_text += f"\n\n下一页：/todo_links {page + 1}"

    if warning:
        reply_text = warning + "\n\n" + reply_text

    bot.reply_to(message, reply_text)


@bot.message_handler(commands=["done_links"])
def handle_done_links(message):
    done_cards = get_done_links()

    if not done_cards:
        bot.reply_to(message, "当前没有已脱水的链接。")
        return

    total = len(done_cards)
    page_size = 10
    page, warning = parse_command_page(message.text, default=1)
    total_pages = (total + page_size - 1) // page_size

    if page > total_pages:
        bot.reply_to(message, f"当前只有 {total_pages} 页已脱水链接，请输入 /done_links 1 到 /done_links {total_pages}。")
        return

    start = (page - 1) * page_size
    end = start + page_size
    visible_cards = done_cards[start:end]
    visible_links = [extract_link_from_card(card) for card in visible_cards]
    visible_links = [link for link in visible_links if link]

    link_lines = [f"{start + index + 1}. {link}" for index, link in enumerate(visible_links)]
    reply_text = (
        f"当前共有 {total} 条已脱水链接，正在显示第 {page}/{total_pages} 页：\n\n"
        + "\n".join(link_lines)
    )

    if page < total_pages:
        reply_text += f"\n\n下一页：/done_links {page + 1}"

    if warning:
        reply_text = warning + "\n\n" + reply_text

    bot.reply_to(message, reply_text)


@bot.message_handler(commands=["all_links"])
def handle_all_links(message):
    all_cards = get_all_links()

    if not all_cards:
        bot.reply_to(message, "当前 links.md 里还没有保存任何链接。")
        return

    total = len(all_cards)
    page_size = 10
    page, warning = parse_command_page(message.text, default=1)
    total_pages = (total + page_size - 1) // page_size

    if page > total_pages:
        bot.reply_to(message, f"当前只有 {total_pages} 页全部链接，请输入 /all_links 1 到 /all_links {total_pages}。")
        return

    start = (page - 1) * page_size
    end = start + page_size
    visible_cards = all_cards[start:end]
    visible_links = [extract_link_from_card(card) for card in visible_cards]
    visible_links = [link for link in visible_links if link]

    link_lines = [f"{start + index + 1}. {link}" for index, link in enumerate(visible_links)]
    reply_text = (
        f"当前共有 {total} 条链接，正在显示第 {page}/{total_pages} 页：\n\n"
        + "\n".join(link_lines)
    )

    if page < total_pages:
        reply_text += f"\n\n下一页：/all_links {page + 1}"

    if warning:
        reply_text = warning + "\n\n" + reply_text

    bot.reply_to(message, reply_text)


@bot.message_handler(commands=["platforms"])
def handle_platforms(message):
    platform_counts = get_platform_stats()

    if not platform_counts:
        bot.reply_to(message, "当前 links.md 里还没有保存任何链接。")
        return

    lines = [f"- {platform}：{count} 条" for platform, count in platform_counts.items()]
    reply_text = "当前素材箱平台统计：\n\n" + "\n".join(lines)
    bot.reply_to(message, reply_text)


@bot.message_handler(commands=["platform"])
def handle_platform(message):
    platform_name, page, warning = parse_platform_command(message.text)

    if warning and not platform_name:
        bot.reply_to(message, warning)
        return

    indexed_platform_cards = get_indexed_links_by_platform(platform_name)

    if not indexed_platform_cards:
        bot.reply_to(message, f"当前没有平台为 {platform_name} 的链接。可以输入 /platforms 查看已有平台。")
        return

    total = len(indexed_platform_cards)
    page_size = 10
    total_pages = (total + page_size - 1) // page_size

    if page > total_pages:
        bot.reply_to(message, f"当前平台 {platform_name} 只有 {total_pages} 页链接，请输入 /platform {platform_name} 1 到 /platform {platform_name} {total_pages}。")
        return

    start = (page - 1) * page_size
    end = start + page_size
    visible_cards = indexed_platform_cards[start:end]
    link_lines = []

    for global_index, card in visible_cards:
        link = extract_link_from_card(card)

        if link:
            link_lines.append(f"全局#{global_index}. {link}")
    reply_text = (
        f"平台 {platform_name} 共有 {total} 条链接，正在显示第 {page}/{total_pages} 页：\n\n"
        f"提示：这里显示的是全局序号，可直接用于 /card、/note、/tag、/fetch_title。\n\n"
        + "\n".join(link_lines)
    )

    if page < total_pages:
        reply_text += f"\n\n下一页：/platform {platform_name} {page + 1}"

    if warning:
        reply_text = warning + "\n\n" + reply_text

    bot.reply_to(message, reply_text)


@bot.message_handler(commands=["search"])
def handle_search(message):
    keyword, warning = parse_search_command(message.text)

    if warning:
        bot.reply_to(message, warning)
        return

    search_results = search_cards(keyword)

    if not search_results:
        bot.reply_to(message, f"没有找到包含“{keyword}”的卡片。")
        return

    lines = []

    for global_index, card in search_results[:10]:
        title = extract_title_from_card(card)
        platform = extract_platform_from_card(card)
        link = extract_link_from_card(card)
        lines.append(f"全局#{global_index}｜{platform}\n标题：{title}\n链接：{link}")

    reply_text = f"找到 {len(search_results)} 条包含“{keyword}”的卡片，最多显示前 10 条：\n\n" + "\n\n".join(lines)
    bot.reply_to(message, reply_text)


@bot.message_handler(commands=["card"])
def handle_card(message):
    card_index, warning = parse_card_index(message.text)

    if warning:
        bot.reply_to(message, warning)
        return

    success, result = get_card_by_index(card_index)

    if not success:
        bot.reply_to(message, result)
        return

    bot.reply_to(message, f"第 {card_index} 条链接的完整卡片：\n\n{result}")


@bot.message_handler(commands=["tag"])
def handle_tag(message):
    card_index, tag, warning = parse_tag_command(message.text)

    if warning:
        bot.reply_to(message, warning)
        return

    success, result = update_card_tag(card_index, tag)

    if not success:
        bot.reply_to(message, result)
        return

    bot.reply_to(message, f"已更新第 {card_index} 条链接的标签：\n{tag}\n\n链接：{result}")


@bot.message_handler(commands=["fetch_title"])
def handle_fetch_title(message):
    try:
        card_index, warning = parse_fetch_title_index(message.text)

        if warning:
            bot.reply_to(message, warning)
            return

        success, result = update_card_title(card_index)

        if not success:
            reason = classify_title_fetch_failure(result)
            print(f"[标题抓取失败] {result}")
            bot.reply_to(message, f"标题抓取失败（{reason}）。请稍后重试。")
            return

        bot.reply_to(message, f"已更新第 {card_index} 条链接的标题：\n{result}")
    except Exception as exc:
        print(f"[handle_fetch_title 异常] {type(exc).__name__}: {exc}")
        bot.reply_to(message, "标题抓取发生异常，请稍后重试。")


@bot.message_handler(commands=["note"])
def handle_note(message):
    card_index, note, warning = parse_note_command(message.text)

    if warning:
        bot.reply_to(message, warning)
        return

    success, result = update_card_note(card_index, note)

    if not success:
        bot.reply_to(message, result)
        return

    bot.reply_to(message, f"已更新第 {card_index} 条链接的备注：\n{note}\n\n链接：{result}")


@bot.message_handler(commands=["done"])
def handle_done(message):
    card_index, warning = parse_status_index(message.text, "done")

    if warning:
        bot.reply_to(message, warning)
        return

    success, result = update_card_status(card_index, "待脱水", "已脱水", "done")

    if not success:
        bot.reply_to(message, result)
        return

    bot.reply_to(message, f"已将第 {card_index} 条待脱水链接标记为已脱水：\n{result}")


@bot.message_handler(commands=["undo"])
def handle_undo(message):
    card_index, warning = parse_status_index(message.text, "undo")

    if warning:
        bot.reply_to(message, warning)
        return

    success, result = update_card_status(card_index, "已脱水", "待脱水", "undo")

    if not success:
        bot.reply_to(message, result)
        return

    bot.reply_to(message, f"已将第 {card_index} 条已脱水链接恢复为待脱水：\n{result}")


@bot.message_handler(func=lambda message: bool(message.text) and message.text.startswith("/"))
def handle_unknown_command(message):
    bot.reply_to(message, "这个命令我还不会。可以输入 /help 查看当前支持的命令。")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        text = message.text or ""

        match = X_LINK_PATTERN.search(text) or ANY_LINK_PATTERN.search(text)

        if match:
            link = match.group(0)
            username = message.from_user.username

            if is_duplicate_link(link):
                print("\n[重复链接]")
                print(f"来自: {username}")
                print(f"链接: {link}")

                bot.reply_to(message, "这条链接已经保存过啦，不重复写入。")
                return

            save_link(link, username)

            print("\n[识别到链接]")
            print(f"来自: {username}")
            print(f"链接: {link}")
            print(f"已保存到: {LINKS_FILE}")

            fetch_success, fetch_result = fetch_page_title_with_fallback(link)

            if fetch_success:
                update_card_title_by_link(link, fetch_result)
                bot.reply_to(message, f"已保存链接，标题：{fetch_result}")
            else:
                reason = classify_title_fetch_failure(fetch_result)
                print(f"[标题抓取失败] {fetch_result}")
                bot.reply_to(message, f"已保存 URL，但自动抓取标题失败（{reason}）。稍后可用 /fetch_title 重试。")
        else:
            print("\n[收到非链接消息]")
            print(f"内容: {text}")

            bot.reply_to(message, "宝宝，请发一个链接给我。")
    except Exception as exc:
        print(f"[handle_message 异常] {type(exc).__name__}: {exc}")
        bot.reply_to(message, "消息处理发生异常，本次内容可能未完整处理，请稍后重试。")


while True:
    try:
        bot.polling(non_stop=True, timeout=10, long_polling_timeout=20)
    except requests.exceptions.ReadTimeout:
        print("[网络提示] Telegram 连接超时，5 秒后自动重试...")
        time.sleep(5)
    except requests.exceptions.ConnectionError:
        print("[网络提示] Telegram 连接中断，5 秒后自动重试...")
        time.sleep(5)
    except requests.exceptions.SSLError:
        print("[网络提示] Telegram SSL 连接波动，5 秒后自动重试...")
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n[系统状态] 收到停止指令，机器人已关闭。")
        break