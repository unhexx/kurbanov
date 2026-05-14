from __future__ import annotations

import re
from dataclasses import dataclass


RE_NUM = re.compile(r"(\d+)")


@dataclass(frozen=True)
class DialogField:
    key: str
    question: str


FIELDS: list[DialogField] = [
    DialogField("brand_model", "Какая марка и модель интересуют?"),
    DialogField(
        "age_years",
        "Какой возраст или год выпуска (например: 3–5 лет или 2021)?",
    ),
    DialogField("body_type", "Какой кузов (седан/кроссовер/лифтбек и т.д.)?"),
    DialogField("drive", "Какой привод (передний/полный/задний)?"),
    DialogField("engine_volume", "Какой объем двигателя (л)?"),
    DialogField("fuel", "Какое топливо (бензин/дизель/гибрид)?"),
    DialogField("transmission", "Какая КПП (автомат/вариатор/механика)?"),
    DialogField("mileage", "Какой пробег (примерно)?"),
    DialogField("color", "Цвет важен? Если да — какой?"),
    DialogField(
        "repair_elements",
        "Допустимы окрасы/ремонтные элементы? Если да — какие ограничения?",
    ),
    DialogField("budget_rub", "Какой бюджет (целевой и предельный) в рублях?"),
    DialogField("power_hp", "Какая мощность (л.с.) или ограничение по мощности?"),
    DialogField("options", "Какие опции обязательны (панорама/люк/CarPlay и т.д.)?"),
    DialogField("alternatives", "Рассматриваете альтернативные модели? Если да — какие?"),
    DialogField("delivery_country", "Страна доставки/оформления (РФ/РБ/КЗ)?"),
]


def _parse_int(text: str) -> int | None:
    m = RE_NUM.search(text.replace(" ", ""))
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def normalize_field_value(key: str, text: str) -> object:
    if key in {"budget_rub", "mileage", "power_hp"}:
        parsed = _parse_int(text)
        return parsed if parsed is not None else text.strip()
    if key == "age_years":
        parsed = _parse_int(text)
        return parsed if parsed is not None else text.strip()
    return text.strip()


def next_missing_field(collected: dict) -> DialogField | None:
    for f in FIELDS:
        if f.key not in collected or collected.get(f.key) in (None, ""):
            return f
    return None


def build_summary(collected: dict) -> str:
    parts = []
    for f in FIELDS:
        if f.key in collected:
            parts.append(f"{f.key}: {collected.get(f.key)}")
    return "\n".join(parts)
