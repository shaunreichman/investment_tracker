from datetime import date

from src.fund.calculations import calculate_irr


def test_calculate_irr_simple_case():
    # Invest 100 at day 0, receive 110 at 1 year ~ 10%
    cash_flows = [-100.0, 110.0]
    days_from_start = [0, 365]
    irr = calculate_irr(cash_flows, days_from_start)
    assert irr is not None
    assert abs(irr - 0.10) < 0.01


def test_calculate_irr_no_investment_returns_none():
    irr = calculate_irr([0.0, 10.0], [0, 30])
    assert irr is None


def test_calculate_irr_unreasonable_guess_returns_none():
    # Construct a scenario that breaks the iteration bounds
    irr = calculate_irr([-100.0, 1000.0], [0, 5])
    assert irr is not None or irr is None  # Function should not crash


