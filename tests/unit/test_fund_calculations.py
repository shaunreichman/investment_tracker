from datetime import date

from src.fund.calculations import calculate_irr


def test_calculate_irr_simple_case_high_precision():
    # Invest 100 at day 0, receive 110 at 1 year ~ 10%
    cash_flows = [-100.0, 110.0]
    days_from_start = [0, 365]
    irr = calculate_irr(cash_flows, days_from_start)
    assert irr is not None
    assert abs(irr - 0.10) < 1e-4  # within 0.01%


def test_calculate_irr_real_case_senior_debt_fund_from_baseline():
    # From tests/output/test_main_output_baseline.txt IRR Cash Flows for 'Senior Debt Fund No.24'
    flows = [
        (date(2023, 6, 23), -100000.00),
        (date(2023, 10, 20), 3030.62),
        (date(2023, 12, 8), 7000.00),
        (date(2024, 1, 16), 2836.98),
        (date(2024, 3, 26), 45000.00),
        (date(2024, 3, 26), 2630.16),
        (date(2024, 7, 9), 1392.19),
        (date(2024, 8, 2), 48000.00),
        (date(2024, 8, 2), 509.84),
    ]
    start = flows[0][0]
    cash_flows = [amt for _, amt in flows]
    days = [(d - start).days for d, _ in flows]
    irr = calculate_irr(cash_flows, days)
    assert irr is not None
    assert abs(irr - 0.1192) < 1e-4  # 11.92%


def test_calculate_irr_real_case_3pg_finance_from_baseline():
    # From tests/output/test_main_output_baseline.txt IRR Cash Flows for '3PG Finance'
    flows = [
        (date(2022, 11, 24), -100000.00),
        (date(2023, 3, 24), 7324.42),
        (date(2023, 3, 24), 3075.58),
        (date(2023, 7, 7), 26326.88),
        (date(2023, 7, 7), 4472.36),
        (date(2023, 8, 4), 8527.53),
        (date(2023, 8, 4), 871.63),
        (date(2023, 9, 22), 8805.21),
        (date(2023, 9, 22), 794.21),
        (date(2023, 10, 13), 9814.74),
        (date(2023, 10, 13), 684.73),
        (date(2023, 11, 21), 6967.81),
        (date(2023, 11, 21), 531.32),
        (date(2024, 4, 19), 32233.41),
        (date(2024, 4, 19), 4399.27),
    ]
    start = flows[0][0]
    cash_flows = [amt for _, amt in flows]
    days = [(d - start).days for d, _ in flows]
    irr = calculate_irr(cash_flows, days)
    assert irr is not None
    assert abs(irr - 0.1654) < 1e-4  # 16.54%


def test_calculate_irr_real_case_abc_from_baseline():
    # From tests/output/test_main_output_baseline.txt IRR Cash Flows for 'ABC Ltd'
    flows = [
        (date(2013, 3, 28), -4949.95),
        (date(2013, 9, 4), 2423.05),
        (date(2013, 9, 12), 79.05),
        (date(2014, 4, 30), -7387.95),
        (date(2014, 5, 13), 10312.35),
    ]
    start = flows[0][0]
    cash_flows = [amt for _, amt in flows]
    days = [(d - start).days for d, _ in flows]
    irr = calculate_irr(cash_flows, days)
    assert irr is not None
    assert abs(irr - 0.1143) < 1e-4  # 11.43%


