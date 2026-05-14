from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class CalculatorScope:
    country: str
    age_years: int
    power_hp: int


@dataclass(frozen=True)
class CalculatorInput:
    car_price_rub: Decimal
    export_cost_rub: Decimal
    commission_rub: Decimal
    broker_rub: Decimal
    logistics_rub: Decimal
    customs_rub: Decimal
    extra_costs_rub: Decimal


def validate_scope(scope: CalculatorScope) -> None:
    country = scope.country.strip().lower()
    if country not in {"рф", "россия"}:
        raise ValueError("scope_country_out_of_v1")
    if not (3 <= scope.age_years <= 5):
        raise ValueError("scope_age_out_of_v1")
    if scope.power_hp > 160:
        raise ValueError("scope_power_out_of_v1")


def calculate_total_rub(inp: CalculatorInput) -> tuple[Decimal, list[dict]]:
    items = [
        {
            "code": "car_price",
            "title": "Цена автомобиля",
            "amount_rub": str(inp.car_price_rub),
        },
        {
            "code": "extra_costs",
            "title": "Расходы по стране покупки",
            "amount_rub": str(inp.extra_costs_rub),
        },
        {"code": "export", "title": "Экспортные расходы", "amount_rub": str(inp.export_cost_rub)},
        {"code": "commission", "title": "Комиссия", "amount_rub": str(inp.commission_rub)},
        {"code": "broker", "title": "Брокер", "amount_rub": str(inp.broker_rub)},
        {
            "code": "customs",
            "title": "Таможенные платежи и сборы",
            "amount_rub": str(inp.customs_rub),
        },
        {
            "code": "logistics",
            "title": "Логистика до целевого города",
            "amount_rub": str(inp.logistics_rub),
        },
    ]
    total = sum(
        (
            inp.car_price_rub,
            inp.extra_costs_rub,
            inp.export_cost_rub,
            inp.commission_rub,
            inp.broker_rub,
            inp.customs_rub,
            inp.logistics_rub,
        ),
        Decimal("0"),
    )
    return total.quantize(Decimal("0.01")), items


def estimate_timestamp() -> datetime:
    return datetime.utcnow()
