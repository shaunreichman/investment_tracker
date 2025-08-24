from datetime import date

from src.tax.calculations import get_financial_year_dates


def test_get_financial_year_dates_au_range_parsing():
    start, end = get_financial_year_dates("2023-24", tax_jurisdiction="AU")
    assert start == date(2023, 7, 1)
    assert end == date(2024, 6, 30)


def test_get_financial_year_dates_au_single_year():
    start, end = get_financial_year_dates("2023", tax_jurisdiction="AU")
    assert start == date(2023, 7, 1)
    assert end == date(2024, 6, 30)


def test_get_financial_year_dates_calendar_jurisdiction():
    start, end = get_financial_year_dates("2023", tax_jurisdiction="US")
    assert start == date(2023, 1, 1)
    assert end == date(2023, 12, 31)


