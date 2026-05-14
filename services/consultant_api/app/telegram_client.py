from __future__ import annotations

import httpx

from app.settings import settings


def send_message(chat_id: int, text: str) -> None:
    if not settings.telegram_bot_token:
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    with httpx.Client(timeout=15.0) as client:
        client.post(url, json=payload)

