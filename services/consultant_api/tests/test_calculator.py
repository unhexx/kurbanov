from decimal import Decimal

import pytest

from app.services.calculator import (
    CalculatorInput,
    CalculatorScope,
    calculate_total_rub,
    validate_scope,
)


def test_validate_scope_ok():
    validate_scope(CalculatorScope(country="РФ", age_years=4, power_hp=150))


@pytest.mark.parametrize(
    "scope",
    [
        CalculatorScope(country="КЗ", age_years=4, power_hp=150),
        CalculatorScope(country="РФ", age_years=2, power_hp=150),
        CalculatorScope(country="Россия", age_years=4, power_hp=170),
    ],
)
def test_validate_scope_errors(scope):
    with pytest.raises(ValueError):
        validate_scope(scope)


def test_calculate_total_rub():
    total, items = calculate_total_rub(
        CalculatorInput(
            car_price_rub=Decimal("1000000"),
            export_cost_rub=Decimal("10000"),
            commission_rub=Decimal("50000"),
            broker_rub=Decimal("85000"),
            logistics_rub=Decimal("200000"),
            customs_rub=Decimal("300000"),
            extra_costs_rub=Decimal("0"),
        )
    )
    assert total == Decimal("1645000.00")
    assert len(items) >= 7
