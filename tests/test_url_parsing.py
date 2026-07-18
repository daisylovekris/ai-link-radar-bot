import pytest

from tg_bot_ignition import (
    ANY_LINK_PATTERN,
    X_LINK_PATTERN,
    extract_link_from_card,
    extract_platform_from_card,
    extract_title_from_card,
    get_platform_from_link,
)


# ── URL 正则匹配 ──────────────────────────────────────────────


def test_single_plain_url():
    text = "https://example.com/article"
    match = X_LINK_PATTERN.search(text) or ANY_LINK_PATTERN.search(text)
    assert match is not None
    assert match.group(0) == "https://example.com/article"


def test_url_inside_text():
    text = "看看这个 https://example.com/article 不错吧"
    match = X_LINK_PATTERN.search(text) or ANY_LINK_PATTERN.search(text)
    assert match is not None
    assert match.group(0) == "https://example.com/article"


def test_multiple_urls_returns_first():
    """当前逻辑用 search() 只匹配第一个 URL。"""
    text = "https://a.com https://b.com"
    match = X_LINK_PATTERN.search(text) or ANY_LINK_PATTERN.search(text)
    assert match is not None
    assert match.group(0) == "https://a.com"


def test_x_com_detected_first():
    text = "https://x.com/user/status/123 https://example.com"
    match = X_LINK_PATTERN.search(text) or ANY_LINK_PATTERN.search(text)
    assert match is not None
    assert "x.com" in match.group(0)


def test_twitter_com_detected_first():
    text = "https://twitter.com/user/status/123 https://example.com"
    match = X_LINK_PATTERN.search(text) or ANY_LINK_PATTERN.search(text)
    assert match is not None
    assert "twitter.com" in match.group(0)


def test_empty_string_no_match():
    match = X_LINK_PATTERN.search("") or ANY_LINK_PATTERN.search("")
    assert match is None


def test_plain_text_no_match():
    match = X_LINK_PATTERN.search("hello world") or ANY_LINK_PATTERN.search("hello world")
    assert match is None


@pytest.mark.xfail(
    reason="当前 URL 正则会把尾部标点包含进匹配结果，待后续修复",
    strict=True,
)
def test_url_trailing_punctuation():
    text = "https://example.com/article."
    match = X_LINK_PATTERN.search(text) or ANY_LINK_PATTERN.search(text)
    assert match is not None
    assert match.group(0) == "https://example.com/article"


# ── 平台识别 ──────────────────────────────────────────────────


def test_platform_example_com():
    assert get_platform_from_link("https://example.com/article") == "example.com"


def test_platform_x_com():
    assert get_platform_from_link("https://x.com/user/status/123") == "x.com"


def test_platform_twitter_com():
    assert get_platform_from_link("https://twitter.com/user/status/123") == "twitter.com"


def test_platform_www_stripped():
    assert get_platform_from_link("https://www.example.com/article") == "example.com"


def test_platform_subdomain():
    assert get_platform_from_link("https://blog.example.com/post") == "blog.example.com"


# ── Markdown 卡片解析 ──────────────────────────────────────────


SAMPLE_CARD = """\
## 2026-05-10 04:16:26

- 标题：示例文章标题
- 来源：@test_user
- 平台：x.com
- 链接：https://x.com/example/status/1234567890
- 标签：#待分类
- 状态：待脱水
- 备注：待补充"""


def test_extract_link_from_card():
    assert extract_link_from_card(SAMPLE_CARD) == "https://x.com/example/status/1234567890"


def test_extract_platform_from_card():
    assert extract_platform_from_card(SAMPLE_CARD) == "x.com"


def test_extract_title_from_card():
    assert extract_title_from_card(SAMPLE_CARD) == "示例文章标题"


def test_extract_title_missing():
    card = "- 链接：https://example.com\n- 平台：example.com"
    assert extract_title_from_card(card) == "待抓取"
