from app.services.fx_rates import parse_cbr_daily_xml


def test_parse_cbr_daily_xml():
    xml = """<?xml version="1.0" encoding="windows-1251"?>
<ValCurs Date="14.05.2026" name="Foreign Currency Market">
  <Valute ID="R01235">
    <NumCode>840</NumCode>
    <CharCode>USD</CharCode>
    <Nominal>1</Nominal>
    <Name>US Dollar</Name>
    <Value>90,0000</Value>
  </Valute>
  <Valute ID="R01375">
    <NumCode>156</NumCode>
    <CharCode>CNY</CharCode>
    <Nominal>10</Nominal>
    <Name>Chinese Yuan</Name>
    <Value>125,0000</Value>
  </Valute>
</ValCurs>
"""
    d, items = parse_cbr_daily_xml(xml)
    assert str(d) == "2026-05-14"
    by_code = {i.char_code: i for i in items}
    assert str(by_code["USD"].rate_rub) == "90.000000"
    # 125 / 10 = 12.5
    assert str(by_code["CNY"].rate_rub) == "12.500000"

