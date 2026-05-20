from __future__ import annotations

import httpx

from app.settings import settings

# Telegram ограничивает текст сообщения 4096 символами.
TELEGRAM_MESSAGE_LIMIT = 4096


def send_message(chat_id: int, text: str) -> None:
    """Отправить сообщение в Telegram, при необходимости разбив на части.

    Деление выполняется по границе абзаца → строки → пробела, чтобы избежать
    разрыва слов и сохранить читабельность. Если токен бота не задан,
    отправка молча пропускается (используется в тестах и локальной разработке).
    """

    if not settings.telegram_bot_token:
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    with httpx.Client(timeout=15.0) as client:
        for chunk in _split_for_telegram(text, TELEGRAM_MESSAGE_LIMIT):
            client.post(url, json={"chat_id": chat_id, "text": chunk})


def _split_for_telegram(text: str, limit: int) -> list[str]:
    if not text:
        return [""]
    if len(text) <= limit:
        return [text]

    parts: list[str] = []
    remaining = text
    while len(remaining) > limit:
        cut = _find_cut_point(remaining, limit)
        parts.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip()
    if remaining:
        parts.append(remaining)
    return [p for p in parts if p]


def _find_cut_point(text: str, limit: int) -> int:
    window = text[:limit]
    for sep in ("\n\n", "\n", ". ", " "):
        idx = window.rfind(sep)
        if idx > limit // 2:
            return idx + len(sep)
    return limit
