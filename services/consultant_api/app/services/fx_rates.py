from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from xml.etree import ElementTree

import httpx


@dataclass(frozen=True)
class FxRateItem:
    char_code: str
    nominal: int
    rate_rub: Decimal


def _parse_decimal(value: str) -> Decimal:
    # CBR uses comma as decimal separator in XML.
    return Decimal(value.replace(",", ".").strip())


def parse_cbr_daily_xml(xml_text: str) -> tuple[date, list[FxRateItem]]:
    root = ElementTree.fromstring(xml_text)
    date_attr = root.attrib.get("Date") or root.attrib.get("date")
    if not date_attr:
        raise ValueError("Missing Date attribute in CBR XML")
    # dd.mm.yyyy
    rate_date = datetime.strptime(date_attr, "%d.%m.%Y").date()

    items: list[FxRateItem] = []
    for valute in root.findall("Valute"):
        code = (valute.findtext("CharCode") or "").strip()
        nominal = int((valute.findtext("Nominal") or "1").strip())
        value = _parse_decimal(valute.findtext("Value") or "0")
        if not code:
            continue
        # Value is for Nominal units; normalize to 1 unit
        rate_per_one = (value / Decimal(nominal)).quantize(Decimal("0.000001"))
        items.append(FxRateItem(char_code=code, nominal=nominal, rate_rub=rate_per_one))
    return rate_date, items


def fetch_cbr_daily_xml(url: str) -> str:
    with httpx.Client(timeout=15.0) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text

