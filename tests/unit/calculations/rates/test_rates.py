from datetime import date

from src.rates.calculations import get_risk_free_rate_for_date


class Rate:
    def __init__(self, rate_date, rate):
        self.rate_date = rate_date
        self.rate = rate


def test_get_risk_free_rate_for_date_empty():
    assert get_risk_free_rate_for_date(date(2024, 1, 1), []) is None


def test_get_risk_free_rate_for_date_selects_latest_on_or_before():
    rates = [
        Rate(date(2024, 1, 1), 3.0),
        Rate(date(2024, 3, 1), 3.5),
        Rate(date(2024, 6, 1), 4.0),
    ]
    assert get_risk_free_rate_for_date(date(2024, 2, 1), rates) == 3.0
    assert get_risk_free_rate_for_date(date(2024, 3, 1), rates) == 3.5
    assert get_risk_free_rate_for_date(date(2024, 9, 1), rates) == 4.0


