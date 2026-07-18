import pytest

import tg_bot_ignition
from tg_bot_ignition import is_duplicate_link


def test_file_not_exists_returns_false(tmp_path, monkeypatch):
    fake_links = tmp_path / "links.md"
    monkeypatch.setattr(tg_bot_ignition, "LINKS_FILE", fake_links)
    assert is_duplicate_link("https://example.com") is False


def test_empty_file_returns_false(tmp_path, monkeypatch):
    fake_links = tmp_path / "links.md"
    fake_links.write_text("", encoding="utf-8")
    monkeypatch.setattr(tg_bot_ignition, "LINKS_FILE", fake_links)
    assert is_duplicate_link("https://example.com") is False


def test_existing_url_returns_true(tmp_path, monkeypatch):
    fake_links = tmp_path / "links.md"
    fake_links.write_text("- 链接：https://example.com\n", encoding="utf-8")
    monkeypatch.setattr(tg_bot_ignition, "LINKS_FILE", fake_links)
    assert is_duplicate_link("https://example.com") is True


def test_url_in_multiple_cards(tmp_path, monkeypatch):
    fake_links = tmp_path / "links.md"
    content = (
        "## 2026-01-01\n\n- 链接：https://a.com\n\n---\n\n"
        "## 2026-01-02\n\n- 链接：https://b.com\n\n---\n\n"
        "## 2026-01-03\n\n- 链接：https://c.com\n\n---\n"
    )
    fake_links.write_text(content, encoding="utf-8")
    monkeypatch.setattr(tg_bot_ignition, "LINKS_FILE", fake_links)
    assert is_duplicate_link("https://b.com") is True


@pytest.mark.xfail(
    reason="当前 is_duplicate_link 用子串匹配，'example.com' 会误判为 'example.com.cn' 的重复",
    strict=True,
)
def test_substring_not_false_positive(tmp_path, monkeypatch):
    fake_links = tmp_path / "links.md"
    fake_links.write_text("- 链接：https://example.com.cn\n", encoding="utf-8")
    monkeypatch.setattr(tg_bot_ignition, "LINKS_FILE", fake_links)
    # 期望：完整 URL 不同应返回 False
    # 实际：子串 "example.com" 匹配了 "example.com.cn"，返回 True
    assert is_duplicate_link("https://example.com") is False
