from __future__ import annotations

from app.telegram_client import TELEGRAM_MESSAGE_LIMIT, _split_for_telegram


def test_split_short_message_stays_one_chunk():
    text = "Короткое сообщение."
    chunks = _split_for_telegram(text, TELEGRAM_MESSAGE_LIMIT)
    assert chunks == [text]


def test_split_long_message_splits_on_paragraphs():
    paragraph = "Это абзац ответа консультанта. " * 50
    text = (paragraph + "\n\n") * 30
    chunks = _split_for_telegram(text, 4096)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c) <= 4096


def test_split_no_separator_falls_back_to_hard_cut():
    text = "Х" * 10000
    chunks = _split_for_telegram(text, 4096)
    assert len(chunks) == 3
    # Сумма должна сохранять все символы
    assert sum(len(c) for c in chunks) == len(text)
