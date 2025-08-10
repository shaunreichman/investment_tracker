"""
Fund calculations module.

This module contains fund-specific calculation functions that use the shared calculations.
"""

from datetime import date, timedelta
import numpy as np
import numpy_financial as npf
from src.shared.calculations import get_equity_change_for_event

# IRR calculation utility
def calculate_irr(cash_flows, days_from_start, tolerance=1e-10, max_iterations=200):
    """
    Calculate annual IRR using daily precision with the Newton-Raphson method.
    
    Args:
        cash_flows (list[float]): List of cash flow amounts (negative for outflows, positive for inflows).
        days_from_start (list[int]): List of days from the start date for each cash flow.
        tolerance (float): Convergence tolerance for the root-finding algorithm.
        max_iterations (int): Maximum number of iterations to attempt.
    
    Returns:
        float or None: The annual IRR as a decimal (e.g., 0.12 for 12%), or None if not computable.
    
    Business context:
        Used for IRR calculations in Fund models, supporting daily-precision cash flows and non-uniform timing.
    """
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
            # Use daily compounding for better precision with long periods
            years = days / 365.25
            discount_factor = (1 + monthly_guess) ** (years * 12)
            npv += cf / discount_factor
            if years > 0:
                derivative -= cf * years * 12 / (discount_factor * (1 + monthly_guess))
        if abs(npv) < tolerance:
            # Convert monthly IRR to annual IRR
            annual_irr = (1 + monthly_guess) ** 12 - 1
            return annual_irr
        if abs(derivative) < 1e-12:
            break
        monthly_guess = monthly_guess - npv / derivative
        if monthly_guess < -0.99 or monthly_guess > 2.0:
            return None
    return None

# Debt cost calculation utility
def calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency):
    """
    Calculate debt cost (opportunity cost) using daily/period-by-period accuracy.
    
    Args:
        events (list): List of FundEvent objects (capital movements).
        risk_free_rates (list): List of RiskFreeRate objects, sorted by date.
        start_date (date): Start date for the calculation period.
        end_date (date): End date for the calculation period.
        currency (str): Currency code for the calculation.
    
    Returns:
        dict: {
            'total_debt_cost': float,  # Total opportunity cost over the period
            'average_risk_free_rate': float,  # Weighted average risk-free rate
            'debt_cost_percentage': float,  # Debt cost as a percentage of average equity
            'investment_duration_years': float,  # Duration in years
            'average_equity': float,  # Average equity over the period
            'total_days': int  # Number of days in the period
        }
    
    Business context:
        Used for real IRR calculations in Fund models, to account for the opportunity cost of capital.
    """
    # Filter events to the relevant period
    events = [e for e in events if e.event_date >= start_date and e.event_date <= end_date]
    events.sort(key=lambda e: e.event_date)
    # Build periods for each risk-free rate
    rate_periods = []
    for i, rate in enumerate(risk_free_rates):
        rate_start = rate.rate_date
        if i + 1 < len(risk_free_rates):
            rate_end = risk_free_rates[i + 1].rate_date
        else:
            rate_end = end_date + timedelta(days=1)
        rate_periods.append((rate_start, rate_end, rate.rate))
    # Build equity periods between events
    equity_periods = []
    current_equity = 0
    last_date = start_date
    for event in events:
        if event.event_date > last_date:
            equity_periods.append((last_date, event.event_date, current_equity))
        if hasattr(event, 'fund'):
            equity_change = get_equity_change_for_event(event, event.fund.tracking_type)
        else:
            equity_change = 0
        current_equity += equity_change
        last_date = event.event_date
    if last_date < end_date:
        equity_periods.append((last_date, end_date, current_equity))
    total_debt_cost = 0
    total_weighted_rate = 0
    total_days = 0
    total_weighted_equity = 0
    # Calculate debt cost for each equity period
    for equity_start, equity_end, equity_amount in equity_periods:
        period_days = (equity_end - equity_start).days
        if period_days <= 0:
            continue
        # Find applicable risk-free rate for this period
        applicable_rate = None
        for rate_start, rate_end, rate_value in rate_periods:
            if rate_start <= equity_start and equity_end <= rate_end:
                applicable_rate = rate_value
                break
        if applicable_rate is None:
            continue
        # Calculate debt cost for this period
        period_debt_cost = equity_amount * (applicable_rate / 100) * (period_days / 365.25)
        total_debt_cost += period_debt_cost
        total_weighted_rate += applicable_rate * period_days
        total_days += period_days
        total_weighted_equity += equity_amount * period_days
    # Calculate summary statistics
    # Handle single day periods - ensure at least 1 day
    if start_date == end_date:
        total_days = max(total_days, 1)
    
    average_risk_free_rate = total_weighted_rate / total_days if total_days > 0 else 0
    average_equity = total_weighted_equity / total_days if total_days > 0 else 0
    debt_cost_percentage = (total_debt_cost / average_equity * 100) if average_equity > 0 else 0
    investment_duration_years = total_days / 365.25
    return {
        'total_debt_cost': total_debt_cost,
        'average_risk_free_rate': average_risk_free_rate,
        'debt_cost_percentage': debt_cost_percentage,
        'investment_duration_years': investment_duration_years,
        'average_equity': average_equity,
        'total_days': total_days
    }

def calculate_nav_based_capital_gains(events):
    """
    Calculate capital gains for NAV-based funds using FIFO method, including brokerage fees.
    - Purchase: cost base per unit = (units * unit_price + brokerage_fee) / units
    - Sale: proceeds per unit = unit_price - (brokerage_fee / units_sold)
    Args:
        events (list): List of FundEvent objects (unit purchases/sales).
    Returns:
        float: Total capital gains.
    Business context:
        Used for tax calculations and performance reporting in NAV-based funds.
    """
    from collections import deque
    available_units = deque()  # Each entry: (units, cost_per_unit)
    total_capital_gains = 0
    for event in events:
        if event.event_type.name == 'UNIT_PURCHASE':
            units = event.units_purchased or 0
            unit_price = event.unit_price or 0
            brokerage_fee = getattr(event, 'brokerage_fee', 0.0) or 0.0
            if units > 0 and unit_price > 0:
                # Apportion brokerage per unit and add to cost base
                cost_per_unit = unit_price + (brokerage_fee / units)
                available_units.append((units, cost_per_unit))
        elif event.event_type.name == 'UNIT_SALE':
            units_to_sell = event.units_sold or 0
            sale_price_per_unit = event.unit_price or 0
            sale_brokerage_fee = getattr(event, 'brokerage_fee', 0.0) or 0.0
            if units_to_sell > 0 and sale_price_per_unit > 0:
                # Apportion sale brokerage per unit
                proceeds_per_unit = sale_price_per_unit - (sale_brokerage_fee / units_to_sell)
                remaining_units_to_sell = units_to_sell
                while remaining_units_to_sell > 0 and available_units:
                    available_units_count, cost_per_unit = available_units[0]
                    units_from_this_purchase = min(remaining_units_to_sell, available_units_count)
                    # Calculate capital gain for these units
                    capital_gain = units_from_this_purchase * (proceeds_per_unit - cost_per_unit)
                    total_capital_gains += capital_gain
                    remaining_units_to_sell -= units_from_this_purchase
                    # Update or remove from available units
                    if units_from_this_purchase == available_units_count:
                        available_units.popleft()
                    else:
                        available_units[0] = (available_units_count - units_from_this_purchase, cost_per_unit)
    return total_capital_gains

def calculate_cost_based_capital_gains(events):
    """
    Calculate capital gains for cost-based funds.
    
    Args:
        events (list): List of FundEvent objects (capital calls/returns).
    
    Returns:
        float: Total capital gains.
    
    Business context:
        Used for tax calculations and performance reporting in cost-based funds.
    """
    # For cost-based funds, capital gains are typically distributions
    total_capital_gains = 0
    for event in events:
        if event.event_type.name == 'DISTRIBUTION' and event.distribution_type and event.distribution_type.name == 'CAPITAL_GAIN':
            total_capital_gains += event.amount or 0
    return total_capital_gains

__all__ = [
    'calculate_irr',
    'calculate_debt_cost',
    'calculate_nav_based_capital_gains',
    'calculate_cost_based_capital_gains',
] 