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
            months = days / 30.44
            discount_factor = (1 + monthly_guess) ** months
            npv += cf / discount_factor
            if months > 0:
                derivative -= cf * months / (discount_factor * (1 + monthly_guess))
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

# Average equity balance utility (NAV-based)
def calculate_average_equity_balance_nav(unit_events, start_date, end_date):
    """
    Calculate average equity balance for NAV-based funds using FIFO cost basis.
    
    Args:
        unit_events (list): List of FundEvent objects (unit purchases/sales).
        start_date (date): Start date for the calculation period.
        end_date (date): End date for the calculation period (exclusive).
    
    Returns:
        float: The average equity balance over the period.
    
    Business context:
        Used for performance and risk calculations in NAV-based funds, accounting for unit-level cost basis.
    """
    if not unit_events:
        return 0
    from collections import deque
    daily_cost_basis = {}
    available_units = deque()
    current_date = start_date
    # Initialize daily cost basis for each day in the period (exclusive of end_date)
    while current_date < end_date:
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
            # Apply FIFO: remove units from the front of the queue
            while units_to_sell > 0 and available_units:
                available_units_count, cost_per_unit, purchase_date = available_units[0]
                units_from_this_purchase = min(units_to_sell, available_units_count)
                units_to_sell -= units_from_this_purchase
                remaining_units = available_units_count - units_from_this_purchase
                if remaining_units > 0:
                    available_units[0] = (remaining_units, cost_per_unit, purchase_date)
                else:
                    available_units.popleft()
        # Calculate current cost basis after each event
        current_cost_basis = sum(units * cost_per_unit for units, cost_per_unit, _ in available_units)
        current_date = event.event_date
        while current_date < end_date:
            daily_cost_basis[current_date] = current_cost_basis
            current_date += timedelta(days=1)
    total_cost_basis = sum(daily_cost_basis.values())
    total_days = len(daily_cost_basis)
    return total_cost_basis / total_days if total_days > 0 else 0

# Average equity balance utility (cost-based)
def calculate_average_equity_balance_cost(capital_events):
    """
    Calculate average equity balance for cost-based funds using weighted periods.
    
    Args:
        capital_events (list): List of FundEvent objects (capital calls/returns).
    
    Returns:
        float: The average equity balance over the period.
    
    Business context:
        Used for performance and risk calculations in cost-based funds, accounting for time-weighted capital.
    """
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
                current_equity += get_equity_change_for_event(event, event.fund.tracking_type)
            continue
        duration_days = (event.event_date - current_date).days
        weighted_equity = current_equity * duration_days
        total_weighted_equity += weighted_equity
        total_days += duration_days
        if hasattr(event, 'fund'):
            current_equity += get_equity_change_for_event(event, event.fund.tracking_type)
        current_date = event.event_date
    return total_weighted_equity / total_days if total_days > 0 else 0

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
    Calculate capital gains for NAV-based funds using FIFO method.
    
    Args:
        events (list): List of FundEvent objects (unit purchases/sales).
    
    Returns:
        float: Total capital gains.
    
    Business context:
        Used for tax calculations and performance reporting in NAV-based funds.
    """
    from collections import deque
    available_units = deque()
    total_capital_gains = 0
    
    for event in events:
        if event.event_type.name == 'UNIT_PURCHASE':
            units = event.units_purchased or 0
            cost_per_unit = event.unit_price or 0
            if units > 0 and cost_per_unit > 0:
                available_units.append((units, cost_per_unit))
        elif event.event_type.name == 'UNIT_SALE':
            units_to_sell = event.units_sold or 0
            sale_price_per_unit = event.unit_price or 0
            if units_to_sell > 0 and sale_price_per_unit > 0:
                # Apply FIFO: calculate capital gains for each unit sold
                remaining_units_to_sell = units_to_sell
                while remaining_units_to_sell > 0 and available_units:
                    available_units_count, cost_per_unit = available_units[0]
                    units_from_this_purchase = min(remaining_units_to_sell, available_units_count)
                    # Calculate capital gain for these units
                    capital_gain = units_from_this_purchase * (sale_price_per_unit - cost_per_unit)
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
        if event.event_type.name == 'DISTRIBUTION' and event.distribution_type and event.distribution_type.name == 'CAPITAL_GAINS':
            total_capital_gains += event.amount or 0
    return total_capital_gains

def orchestrate_nav_based_average_equity(unit_events):
    """
    Orchestrate average equity calculation for NAV-based funds.
    
    Args:
        unit_events (list): List of FundEvent objects (unit purchases/sales).
    
    Returns:
        float: Average equity balance.
    
    Business context:
        Used for performance calculations in NAV-based funds.
    """
    if not unit_events:
        return 0
    # Get date range from events
    dates = [event.event_date for event in unit_events]
    start_date = min(dates)
    end_date = max(dates) + timedelta(days=1)
    return calculate_average_equity_balance_nav(unit_events, start_date, end_date)

def orchestrate_cost_based_average_equity(capital_events):
    """
    Orchestrate average equity calculation for cost-based funds.
    
    Args:
        capital_events (list): List of FundEvent objects (capital calls/returns).
    
    Returns:
        float: Average equity balance.
    
    Business context:
        Used for performance calculations in cost-based funds.
    """
    return calculate_average_equity_balance_cost(capital_events)

def orchestrate_irr_base(cash_flow_events, start_date, include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, return_cashflows=False):
    """
    Orchestrate IRR calculation with various options for cash flow inclusion.
    
    Args:
        cash_flow_events (list): List of FundEvent objects (cash flows).
        start_date (date): Start date for IRR calculation.
        include_tax_payments (bool): Whether to include tax payment events.
        include_risk_free_charges (bool): Whether to include risk-free interest charges.
        include_fy_debt_cost (bool): Whether to include financial year debt cost events.
        return_cashflows (bool): Whether to return cash flow details.
    
    Returns:
        dict or float: IRR result or cash flow details if return_cashflows=True.
    
    Business context:
        Used for IRR calculations in Fund models with configurable cash flow inclusion.
    """
    # Filter events based on options
    filtered_events = []
    for event in cash_flow_events:
        include_event = False
        if event.event_type.name in ['UNIT_PURCHASE', 'UNIT_SALE', 'CAPITAL_CALL', 'RETURN_OF_CAPITAL', 'DISTRIBUTION']:
            include_event = True
        elif include_tax_payments and event.event_type.name == 'TAX_PAYMENT':
            include_event = True
        elif include_risk_free_charges and event.event_type.name == 'RISK_FREE_INTEREST_CHARGE':
            include_event = True
        elif include_fy_debt_cost and event.event_type.name == 'FY_DEBT_COST':
            include_event = True
        if include_event:
            filtered_events.append(event)
    
    # Sort events by date
    filtered_events.sort(key=lambda e: e.event_date)
    
    # Prepare cash flows for IRR calculation
    cash_flows = []
    days_from_start = []
    
    for event in filtered_events:
        amount = event.amount or 0
        # Adjust sign based on event type
        if event.event_type.name in ['UNIT_PURCHASE', 'CAPITAL_CALL']:
            amount = -abs(amount)  # Outflow
        elif event.event_type.name in ['UNIT_SALE', 'RETURN_OF_CAPITAL', 'DISTRIBUTION', 'FY_DEBT_COST']:
            amount = abs(amount)  # Inflow
        elif event.event_type.name == 'TAX_PAYMENT':
            amount = -abs(amount)  # Outflow
        elif event.event_type.name == 'RISK_FREE_INTEREST_CHARGE':
            amount = -abs(amount)  # Outflow
        
        cash_flows.append(amount)
        days = (event.event_date - start_date).days
        days_from_start.append(days)
    
    # Calculate IRR
    if len(cash_flows) < 2:
        return None
    
    irr_result = calculate_irr(cash_flows, days_from_start)
    
    if return_cashflows:
        return {
            'irr': irr_result,
            'cash_flows': cash_flows,
            'days_from_start': days_from_start,
            'events': filtered_events
        }
    else:
        return irr_result

def calculate_nav_event_amounts(unit_events):
    """Calculate amounts for unit purchases/sales and update units_owned and cost_of_units for NAV-based funds.
    This function ensures that:
    - Unit purchase/sale amounts = units * unit_price + brokerage_fee
    - units_owned is updated only after purchase/sale events (not NAV updates)
    - cost_of_units is calculated using FIFO for remaining units after each event
    
    Args:
        unit_events (list): List of FundEvent objects with UNIT_PURCHASE, UNIT_SALE, and NAV_UPDATE events
        
    Note: This function updates the event objects in place. No database operations are performed.
    """
    from src.fund.models import EventType
    
    # Calculate amounts for unit purchases/sales and update units_owned and cost_of_units
    cumulative_units = 0.0
    available_units = []  # FIFO queue: [(units, cost_per_unit, date), ...]
    
    for event in unit_events:
        if event.event_type == EventType.UNIT_PURCHASE:
            units = event.units_purchased or 0
            unit_price = event.unit_price or 0
            brokerage_fee = event.brokerage_fee or 0
            event.amount = (units * unit_price) + brokerage_fee
            
            # Add to FIFO queue
            if units > 0 and unit_price > 0:
                available_units.append((units, unit_price, event.event_date))
            
            cumulative_units += units
            event.units_owned = cumulative_units
            
            # Calculate cost of remaining units using FIFO
            total_cost = sum(units * cost for units, cost, _ in available_units)
            event.cost_of_units = total_cost
            
        elif event.event_type == EventType.UNIT_SALE:
            units = event.units_sold or 0
            unit_price = event.unit_price or 0
            brokerage_fee = event.brokerage_fee or 0
            event.amount = (units * unit_price) - brokerage_fee  # Negative for sales
            
            # Remove units from FIFO queue (FIFO order)
            remaining_units_to_sell = units
            while remaining_units_to_sell > 0 and available_units:
                oldest_units, oldest_cost, _ = available_units[0]
                if oldest_units <= remaining_units_to_sell:
                    # Sell all oldest units
                    available_units.pop(0)
                    remaining_units_to_sell -= oldest_units
                else:
                    # Sell partial oldest units
                    available_units[0] = (oldest_units - remaining_units_to_sell, oldest_cost, available_units[0][2])
                    remaining_units_to_sell = 0
            
            cumulative_units -= units
            event.units_owned = cumulative_units
            
            # Calculate cost of remaining units using FIFO
            total_cost = sum(units * cost for units, cost, _ in available_units)
            event.cost_of_units = total_cost
            
        # Do not update units_owned or cost_of_units for NAV_UPDATE events

def calculate_cumulative_units_and_cost_basis(unit_events, as_of_date=None):
    """
    Calculate cumulative units owned and total cost basis up to a given date.
    Shared utility for NAV-based calculations.
    
    Args:
        unit_events (list): List of FundEvent objects with UNIT_PURCHASE and UNIT_SALE events
        as_of_date (date, optional): Calculate as of this date. If None, calculates to the end.
    
    Returns:
        dict: {
            'cumulative_units': float,
            'total_cost_basis': float,
            'unit_purchases': list of (units, cost_per_unit, date),
            'unit_sales': list of (units, sale_price_per_unit, date)
        }
    """
    from src.fund.models import EventType
    
    cumulative_units = 0.0
    total_cost_basis = 0.0
    unit_purchases = []
    unit_sales = []
    
    for event in unit_events:
        # Stop if we've reached the as_of_date
        if as_of_date and event.event_date > as_of_date:
            break
            
        if event.event_type == EventType.UNIT_PURCHASE:
            units = event.units_purchased or 0
            unit_price = event.unit_price or 0
            if units > 0 and unit_price > 0:
                cumulative_units += units
                total_cost_basis += units * unit_price
                unit_purchases.append((units, unit_price, event.event_date))
                
        elif event.event_type == EventType.UNIT_SALE:
            units = event.units_sold or 0
            unit_price = event.unit_price or 0
            if units > 0:
                cumulative_units -= units
                unit_sales.append((units, unit_price, event.event_date))
    
    return {
        'cumulative_units': cumulative_units,
        'total_cost_basis': total_cost_basis,
        'unit_purchases': unit_purchases,
        'unit_sales': unit_sales
    }

def calculate_nav_based_cost_basis_for_irr(unit_events, as_of_date=None):
    """
    Calculate the cost basis for NAV-based funds up to a given date.
    This is used for IRR calculations where we need to know the total amount invested.
    
    Args:
        unit_events (list): List of FundEvent objects with UNIT_PURCHASE and UNIT_SALE events
        as_of_date (date, optional): Calculate as of this date. If None, calculates to the end.
    
    Returns:
        float: Total cost basis (sum of all unit purchases minus unit sales)
    """
    result = calculate_cumulative_units_and_cost_basis(unit_events, as_of_date)
    return result['total_cost_basis']

__all__ = [
    'calculate_irr',
    'calculate_average_equity_balance_nav',
    'calculate_average_equity_balance_cost',
    'calculate_debt_cost',
    'calculate_nav_based_capital_gains',
    'calculate_cost_based_capital_gains',
    'orchestrate_nav_based_average_equity',
    'orchestrate_cost_based_average_equity',
    'orchestrate_irr_base',
    'calculate_nav_event_amounts',
    'calculate_cumulative_units_and_cost_basis',
    'calculate_nav_based_cost_basis_for_irr',
] 