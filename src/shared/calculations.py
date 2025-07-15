"""
Shared calculations module.

This module contains pure calculation functions that can be used across different domains.
These functions do not depend on database sessions and are purely mathematical.
"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
import math


def calculate_irr(cash_flows, days_from_start, tolerance=1e-10, max_iterations=200):
    """
    Calculate IRR using daily cash flows and a root-finding algorithm.
    
    Args:
        cash_flows: List of (amount, days_from_start) tuples
        days_from_start: List of days from start for each cash flow
        tolerance: Tolerance for convergence
        max_iterations: Maximum number of iterations
        
    Returns:
        float: IRR as a percentage, or None if calculation fails
    """
    if not cash_flows or len(cash_flows) < 2:
        return None
    
    # Initial guess: simple rate based on total return
    total_invested = sum(cf for cf in cash_flows if cf < 0)
    total_returned = sum(cf for cf in cash_flows if cf > 0)
    
    if total_invested == 0 or total_returned == 0:
        return None
    
    # Simple annualized return as initial guess
    total_days = max(days_from_start) if days_from_start else 365
    simple_return = (total_returned / abs(total_invested)) - 1
    initial_guess = ((1 + simple_return) ** (365.25 / total_days)) - 1
    
    rate = initial_guess
    
    for iteration in range(max_iterations):
        npv = 0
        npv_derivative = 0
        
        for i, (cf, days) in enumerate(zip(cash_flows, days_from_start)):
            if days == 0:
                npv += cf
            else:
                discount_factor = (1 + rate) ** (days / 365.25)
                npv += cf / discount_factor
                
                if days > 0:
                    npv_derivative -= (cf * days) / (365.25 * discount_factor * (1 + rate))
        
        if abs(npv) < tolerance:
            return rate  # Return as decimal, not percentage
        
        if abs(npv_derivative) < 1e-15:
            break
            
        rate_new = rate - npv / npv_derivative
        
        # Prevent extreme values
        if rate_new < -0.99:
            rate_new = -0.99
        elif rate_new > 10:
            rate_new = 10
            
        if abs(rate_new - rate) < tolerance:
            return rate_new  # Return as decimal, not percentage
            
        rate = rate_new
    
    return None


def get_equity_change_for_event(event, fund_type):
    """
    Calculate the equity change for a given event based on fund type.
    For NAV_BASED funds, exclude brokerage from equity (use units * unit_price).
    Args:
        event: FundEvent object
        fund_type (FundType): Type of fund (NAV_BASED or COST_BASED)
    Returns:
        float: Equity change amount
    """
    from src.fund.models import EventType, FundType

    if fund_type == FundType.NAV_BASED:
        if event.event_type == EventType.UNIT_PURCHASE:
            # Exclude brokerage: equity is units * unit_price
            return (event.units_purchased or 0.0) * (event.unit_price or 0.0)
        elif event.event_type == EventType.UNIT_SALE:
            # Exclude brokerage: equity is units * unit_price
            return -((event.units_sold or 0.0) * (event.unit_price or 0.0))
    elif fund_type == FundType.COST_BASED:
        if event.event_type == EventType.CAPITAL_CALL:
            return event.amount or 0.0
        elif event.event_type == EventType.RETURN_OF_CAPITAL:
            return -(event.amount or 0.0)
    return 0.0


def get_risk_free_rate_for_date(target_date, risk_free_rates):
    """Get the risk-free rate for a specific date from a list of rates.
    Returns the most recent rate available on or before the target date, or None if not found.
    """
    if not risk_free_rates:
        return None
    
    # Find the most recent rate that's <= target_date
    applicable_rate = None
    for rate in risk_free_rates:
        if rate.rate_date <= target_date:
            applicable_rate = rate
        else:
            break
    
    return applicable_rate.rate if applicable_rate else None


def get_financial_years_for_fund_period(start_date, end_date, entity):
    """Get all financial years between start and end dates.
    Returns a set of financial year strings. No database operations.
    """
    financial_years = set()
    current_date = start_date
    while current_date <= end_date:
        fy = entity.get_financial_year(current_date)
        financial_years.add(fy)
        # Move to next month
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)
    return financial_years


def get_reconciliation_explanation(gross_diff, tax_diff, net_diff):
    """
    Generate a human-readable explanation for the reconciliation differences.
    
    Args:
        gross_diff (float): Difference in gross amounts
        tax_diff (float): Difference in tax amounts  
        net_diff (float): Difference in net amounts
    
    Returns:
        str: Human-readable explanation of the differences
    """
    explanations = []
    
    if abs(gross_diff) > 0.01:  # Allow for small rounding differences
        if gross_diff > 0:
            explanations.append(f"${gross_diff:,.2f} of interest was accrued but not yet distributed")
        else:
            explanations.append(f"${abs(gross_diff):,.2f} more was distributed than reported in tax statement")
    
    if abs(tax_diff) > 0.01:
        if tax_diff > 0:
            explanations.append(f"${tax_diff:,.2f} more tax was withheld than actually deducted")
        else:
            explanations.append(f"${abs(tax_diff):,.2f} less tax was withheld than actually deducted")
    
    if abs(net_diff) > 0.01:
        if net_diff > 0:
            explanations.append(f"${net_diff:,.2f} more net income reported than actually received")
        else:
            explanations.append(f"${abs(net_diff):,.2f} more net income received than reported")
    
    if not explanations:
        explanations.append("Tax statement matches actual distributions perfectly")
    
    return "; ".join(explanations)


def get_unit_events_for_fund(unit_events, as_of_date=None):
    """
    Filter unit events up to a given date.
    
    Args:
        unit_events: List of FundEvent objects
        as_of_date: Filter events up to this date. If None, includes all events.
    
    Returns:
        list: Filtered list of unit events
    """
    if as_of_date is None:
        return unit_events
    
    return [e for e in unit_events if e.event_date <= as_of_date]


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





def tax_payable(interest_income_amount, interest_income_tax_rate, interest_non_resident_withholding_tax_from_statement):
    """
    Calculate tax payable as (interest_income_amount * interest_income_tax_rate / 100) - interest_non_resident_withholding_tax_from_statement.
    Args:
        interest_income_amount (float): Total interest income.
        interest_income_tax_rate (float): Taxable rate as a percentage.
        interest_non_resident_withholding_tax_from_statement (float): Tax withheld from statement.
    Returns:
        float: Tax payable (never negative).
    """
    if interest_income_tax_rate and interest_income_amount and interest_income_tax_rate != 0 and interest_income_amount > 0:
        total_tax_liability = interest_income_amount * (interest_income_tax_rate / 100)
        return max(0, total_tax_liability - (interest_non_resident_withholding_tax_from_statement or 0.0))
    return 0.0


def get_financial_year_dates(financial_year, tax_jurisdiction="AU"):
    """
    Get the start and end dates for a financial year based on jurisdiction.
    Args:
        financial_year (str): Financial year string (e.g., '2023-24' or '2023').
        tax_jurisdiction (str): Jurisdiction code (e.g., 'AU').
    Returns:
        tuple: (start_date, end_date) as datetime.date objects.
    """
    from datetime import date
    if '-' in financial_year:
        start_year, end_year = financial_year.split('-')
        start_year = int(start_year)
        if len(end_year) == 2:
            end_year = int(f"20{end_year}")
        else:
            end_year = int(end_year)
        if tax_jurisdiction == "AU":
            fy_start = date(start_year, 7, 1)
            fy_end = date(end_year, 6, 30)
        else:
            fy_start = date(start_year, 1, 1)
            fy_end = date(start_year, 12, 31)
    else:
        year = int(financial_year)
        if tax_jurisdiction == "AU":
            fy_start = date(year, 7, 1)
            fy_end = date(year + 1, 6, 30)
        else:
            fy_start = date(year, 1, 1)
            fy_end = date(year, 12, 31)
    return fy_start, fy_end


def interest_tax_benefit(interest_income, tax_rate=0.45):
    """Calculate the tax benefit from interest income.
    
    Args:
        interest_income (float): Interest income amount
        tax_rate (float): Tax rate as decimal (default 0.45 for 45%)
        
    Returns:
        float: Tax benefit amount
    """
    return interest_income * tax_rate


def orchestrate_irr_base(cash_flow_events, start_date, include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, return_cashflows=False):
    """Orchestrate IRR calculation with configurable cash flow inclusion.
    This is a shared calculation function that can be used by any domain.
    
    Args:
        cash_flow_events (list): List of FundEvent objects
        start_date (date): Start date for IRR calculation
        include_tax_payments (bool): Whether to include tax payment events
        include_risk_free_charges (bool): Whether to include risk-free interest charges
        include_fy_debt_cost (bool): Whether to include FY debt cost events
        return_cashflows (bool): Whether to return cash flow details
        
    Returns:
        float or dict: IRR value or dict with cash flow details
    """
    from src.fund.models import EventType
    
    # Filter events based on options
    filtered_events = []
    for event in cash_flow_events:
        include_event = False
        if event.event_type.name in ['UNIT_PURCHASE', 'UNIT_SALE', 'CAPITAL_CALL', 'RETURN_OF_CAPITAL', 'DISTRIBUTION']:
            include_event = True
        elif include_tax_payments and event.event_type.name == 'TAX_PAYMENT':
            include_event = True
        elif include_risk_free_charges and event.event_type.name == 'DAILY_RISK_FREE_INTEREST_CHARGE':
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
        elif event.event_type.name == 'DAILY_RISK_FREE_INTEREST_CHARGE':
            amount = -abs(amount)  # Outflow
        
        cash_flows.append(amount)
        days = (event.event_date - start_date).days
        days_from_start.append(days)
    
    # Calculate IRR
    if len(cash_flows) < 2:
        return None
    
    # Import the IRR calculation function from fund calculations
    from src.fund.calculations import calculate_irr
    irr_result = calculate_irr(cash_flows, days_from_start)
    
    if return_cashflows:
        # Generate labels from event descriptions
        labels = []
        for event in filtered_events:
            if event.description:
                labels.append(f"{event.event_type.value} | {event.event_date} | {event.amount:,.2f} | {event.description}")
            else:
                labels.append(f"{event.event_type.value} | {event.event_date} | {event.amount:,.2f}")
        
        return {
            'irr': irr_result,
            'cash_flows': cash_flows,
            'days_from_start': days_from_start,
            'events': filtered_events,
            'labels': labels
        }
    else:
        return irr_result


__all__ = [
    'calculate_irr',
    'get_equity_change_for_event',
    'get_risk_free_rate_for_date',
    'get_financial_years_for_fund_period',
    'get_reconciliation_explanation',
    'get_unit_events_for_fund',
    'calculate_cumulative_units_and_cost_basis',

    'tax_payable',
    'interest_tax_benefit',
    'get_financial_year_dates',
    'orchestrate_irr_base',
] 