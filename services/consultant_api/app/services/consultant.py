"""Логика Telegram-консультанта поверх rule-based ядра и внешнего сервиса.

Все «жёсткие» правила (бюджет, страна, мощность, не-текст, пост-квалификация,
прямые просьбы передать менеджеру) принимаются здесь и имеют приоритет над
сигналом внешнего сервиса формирования ответов.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.settings import settings

MANAGER_REQUEST_PATTERNS = [
    r"\bменеджер",
    r"\bоператор",
    r"\bживо(?:й|го|му)\b",
    r"\bчелове(?:к|ка|ку)\b",
    r"\bспециалист",
    r"\bпозов(?:ите|и)\b",
    r"\bсоедин(?:ите|и)\b",
    r"\bперезвон(?:ите|и)\b",
    r"\bсвяж(?:ите|и)сь\b",
]
_MANAGER_REQUEST_RE = re.compile("|".join(MANAGER_REQUEST_PATTERNS), re.IGNORECASE)


NEUTRAL_HANDOFF_TEXT = (
    "Передаю запрос профильному менеджеру — он свяжется с вами в чате и доведёт "
    "подбор до результата."
)

SERVICE_UNAVAILABLE_FALLBACK_TEXT = (
    "Сейчас оформляю передачу запроса профильному менеджеру. Он свяжется с вами в чате "
    "в ближайшее время."
)


SUPPORTED_COUNTRIES = {
    "рф", "россия", "russia", "rf",
    "рб", "беларусь", "belarus",
    "кз", "казахстан", "kz",
}
ELECTRIC_FUEL_TOKENS = {
    "электро", "электрический", "ev",
    "электромобиль", "tesla", "tesla.", "тесла",
}


@dataclass
class ConsultantDecision:
    """Решение слоя консультанта по входящему сообщению клиента."""

    action: str  # "respond" | "escalate"
    text: str
    reason: str = ""
    manager_note: str = ""


def is_manager_request(text: str) -> bool:
    """Прямая просьба клиента позвать менеджера/оператора/человека."""

    if not text:
        return False
    return bool(_MANAGER_REQUEST_RE.search(text))


def is_below_budget_threshold(collected: dict[str, Any] | None) -> bool:
    if not collected:
        return False
    budget = collected.get("budget_rub")
    return isinstance(budget, int) and budget < settings.budget_threshold_rub


def detect_non_standard_scope(
    collected: dict[str, Any] | None, text: str
) -> tuple[bool, str | None]:
    """Грубое определение нестандартного контура расчёта.

    Возвращает (True, reason_code) при выявлении явных триггеров: электромобиль,
    мощность > 160 л.с., доставка в страну вне РФ/РБ/КЗ, возраст вне 3–5 лет
    при ценовом вопросе. Иначе (False, None).
    """

    text_l = (text or "").lower()

    country = ""
    if collected:
        country = str(collected.get("delivery_country") or "").strip().lower()
    if country:
        country_token = re.sub(r"[^а-яa-z]+", "", country)
        if country_token and country_token not in SUPPORTED_COUNTRIES:
            return True, "country_not_supported"

    if any(token in text_l for token in ELECTRIC_FUEL_TOKENS):
        return True, "non_standard_scope"
    if collected:
        fuel = str(collected.get("fuel") or "").lower()
        if any(token in fuel for token in ELECTRIC_FUEL_TOKENS):
            return True, "non_standard_scope"

        power = collected.get("power_hp")
        if isinstance(power, int) and power > 160:
            return True, "non_standard_scope"

        age = collected.get("age_years")
        # Будем считать только явные «годы» (1..15), а не год выпуска (>=1900).
        if isinstance(age, int) and 1 <= age < 100 and (age < 3 or age > 5):
            asks_price = any(
                kw in text_l for kw in ("цена", "стоит", "под ключ", "сколько", "расч", "цены")
            )
            if asks_price:
                return True, "non_standard_scope"

    return False, None


def detect_non_text(message: dict[str, Any]) -> bool:
    """Поддерживаемые типы — только text/caption. Остальное — эскалация."""

    if not isinstance(message, dict):
        return False
    if message.get("text"):
        return False
    non_text_keys = (
        "photo",
        "voice",
        "video",
        "video_note",
        "audio",
        "document",
        "sticker",
        "animation",
        "location",
        "contact",
    )
    return any(key in message for key in non_text_keys)


def build_calculator_hint(collected: dict[str, Any] | None) -> str | None:
    """Короткая подсказка для модели о применимости калькулятора v1."""

    if not collected:
        return None
    country = str(collected.get("delivery_country") or "").strip().lower() if collected else ""
    age = collected.get("age_years")
    power = collected.get("power_hp")

    notes: list[str] = []
    if country and country not in SUPPORTED_COUNTRIES:
        notes.append(f"Страна доставки «{country}» вне поддерживаемого контура (РФ/РБ/КЗ).")
    if isinstance(age, int) and 1 <= age < 100 and (age < 3 or age > 5):
        notes.append(f"Возраст автомобиля {age} лет вне контура калькулятора (3–5 лет).")
    if isinstance(power, int) and power > 160:
        notes.append(f"Мощность {power} л.с. выше порога калькулятора (160 л.с.).")
    if not notes:
        return None
    notes.append(
        "Самостоятельный ценовой расчёт по такому набору не выполняется — нужно передать "
        "запрос профильному менеджеру."
    )
    return "\n".join(notes)


def make_escalation(reason: str, *, manager_note: str = "") -> ConsultantDecision:
    return ConsultantDecision(
        action="escalate",
        text=NEUTRAL_HANDOFF_TEXT,
        reason=reason,
        manager_note=manager_note,
    )
