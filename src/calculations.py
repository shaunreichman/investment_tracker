"""
Calculation utilities for investment tracker.
Includes IRR, average equity balance, and debt cost calculations.
"""

from datetime import date, timedelta
import numpy as np
import numpy_financial as npf

# IRR calculation utility
def calculate_irr(cash_flows, days_from_start, tolerance=1e-10, max_iterations=200):
    """Calculate monthly IRR using daily precision with Newton-Raphson method."""
    # Initial guess: simple rate of return
    total_investment = abs(cash_flows[0]) if cash_flows[0] < 0 else 0
    total_return = sum(cf for cf in cash_flows[1:] if cf > 0)
    if total_investment == 0:
        return None
    simple_return = (total_return - total_investment) / total_investment
    monthly_guess = (1 + simple_return) ** (1/12) - 1
    monthly_guess = max(-0.99, min(monthly_guess, 2.0))
    for iteration in range(max_iterations):
        npv = 0
        derivative = 0
        for i, (cf, days) in enumerate(zip(cash_flows, days_from_start)):
            months = days / 30.44
            discount_factor = (1 + monthly_guess) ** months
            npv += cf / discount_factor
            if months > 0:
                derivative -= cf * months / (discount_factor * (1 + monthly_guess))
        if abs(npv) < tolerance:
            return monthly_guess
        if abs(derivative) < 1e-12:
            break
        monthly_guess = monthly_guess - npv / derivative
        if monthly_guess < -0.99 or monthly_guess > 2.0:
            return None
    return None

# Average equity balance utility (NAV-based)
def calculate_average_equity_balance_nav(unit_events, start_date, end_date):
    """Calculate average equity balance for NAV-based funds using FIFO cost basis."""
    if not unit_events:
        return 0
    from collections import deque
    daily_cost_basis = {}
    available_units = deque()
    current_date = start_date
    while current_date <= end_date:
        daily_cost_basis[current_date] = 0
        current_date += timedelta(days=1)
    for event in unit_events:
        if event.event_type.name == 'UNIT_PURCHASE':
            units = event.units_purchased or 0
            cost_per_unit = event.unit_price or 0
            if units > 0 and cost_per_unit > 0:
                available_units.append((units, cost_per_unit, event.event_date))
        elif event.event_type.name == 'UNIT_SALE':
            units_to_sell = event.units_sold or 0
            while units_to_sell > 0 and available_units:
                available_units_count, cost_per_unit, purchase_date = available_units[0]
                units_from_this_purchase = min(units_to_sell, available_units_count)
                units_to_sell -= units_from_this_purchase
                remaining_units = available_units_count - units_from_this_purchase
                if remaining_units > 0:
                    available_units[0] = (remaining_units, cost_per_unit, purchase_date)
                else:
                    available_units.popleft()
        current_cost_basis = sum(units * cost_per_unit for units, cost_per_unit, _ in available_units)
        current_date = event.event_date
        while current_date <= end_date:
            daily_cost_basis[current_date] = current_cost_basis
            current_date += timedelta(days=1)
    total_cost_basis = sum(daily_cost_basis.values())
    total_days = len(daily_cost_basis)
    return total_cost_basis / total_days if total_days > 0 else 0

# Average equity balance utility (cost-based)
def calculate_average_equity_balance_cost(capital_events):
    """Calculate average equity balance for cost-based funds using weighted periods."""
    if not capital_events:
        return 0
    total_weighted_equity = 0
    total_days = 0
    current_equity = 0
    current_date = None
    for i, event in enumerate(capital_events):
        if i == 0:
            current_date = event.event_date
            if hasattr(event, 'fund'):
                current_equity += event.fund._get_equity_change_for_event(event)
            continue
        duration_days = (event.event_date - current_date).days
        weighted_equity = current_equity * duration_days
        total_weighted_equity += weighted_equity
        total_days += duration_days
        if hasattr(event, 'fund'):
            current_equity += event.fund._get_equity_change_for_event(event)
        current_date = event.event_date
    return total_weighted_equity / total_days if total_days > 0 else 0

# Debt cost calculation utility
def calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency):
    """Calculate debt cost (opportunity cost) using daily/period-by-period accuracy."""
    events = [e for e in events if e.event_date >= start_date and e.event_date <= end_date]
    events.sort(key=lambda e: e.event_date)
    rate_periods = []
    for i, rate in enumerate(risk_free_rates):
        rate_start = rate.rate_date
        if i + 1 < len(risk_free_rates):
            rate_end = risk_free_rates[i + 1].rate_date
        else:
            rate_end = end_date + timedelta(days=1)
        rate_periods.append((rate_start, rate_end, rate.rate))
    equity_periods = []
    current_equity = 0
    last_date = start_date
    for event in events:
        if event.event_date > last_date:
            equity_periods.append((last_date, event.event_date, current_equity))
        if hasattr(event, 'fund'):
            equity_change = event.fund._get_equity_change_for_event(event)
        else:
            equity_change = 0
        current_equity += equity_change
        last_date = event.event_date
    if last_date < end_date:
        equity_periods.append((last_date, end_date, current_equity))
    total_debt_cost = 0
    total_days = 0
    weighted_rfr_sum = 0
    weighted_equity_days = 0
    for eq_start, eq_end, equity in equity_periods:
        period_start = eq_start
        while period_start < eq_end:
            rate = None
            for r_start, r_end, r_value in rate_periods:
                if r_start <= period_start < r_end:
                    rate = r_value
                    sub_period_end = min(eq_end, r_end)
                    break
            if rate is None:
                rate = rate_periods[-1][2]
                sub_period_end = eq_end
            days = (sub_period_end - period_start).days
            if days > 0 and equity != 0:
                cost = equity * (rate / 100) * (days / 365.25)
                total_debt_cost += cost
                weighted_rfr_sum += rate * days * equity
                weighted_equity_days += days * equity
                total_days += days
            period_start = sub_period_end
    avg_risk_free_rate = weighted_rfr_sum / weighted_equity_days if weighted_equity_days > 0 else 0
    avg_equity = sum((eq[2] * (eq[1] - eq[0]).days for eq in equity_periods)) / total_days if total_days > 0 else 0
    investment_duration_years = total_days / 365.25
    debt_cost_percentage = (total_debt_cost / avg_equity) * 100 if avg_equity else 0
    return {
        'total_debt_cost': total_debt_cost,
        'average_risk_free_rate': avg_risk_free_rate,
        'debt_cost_percentage': debt_cost_percentage,
        'investment_duration_years': investment_duration_years,
        'average_equity': avg_equity,
        'total_days': total_days
    } 