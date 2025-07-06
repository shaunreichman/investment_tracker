"""
Shared calculations module.

This module contains pure calculation functions that can be used across different domains.
These functions do not depend on database sessions and are purely mathematical.
"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
import math
from src.calculations import orchestrate_irr_base


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
            return rate * 100  # Convert to percentage
        
        if abs(npv_derivative) < 1e-15:
            break
            
        rate_new = rate - npv / npv_derivative
        
        # Prevent extreme values
        if rate_new < -0.99:
            rate_new = -0.99
        elif rate_new > 10:
            rate_new = 10
            
        if abs(rate_new - rate) < tolerance:
            return rate_new * 100  # Convert to percentage
            
        rate = rate_new
    
    return None


def get_equity_change_for_event(event, fund_type):
    """
    Calculate the equity change for a given event based on fund type.
    Args:
        event: FundEvent object
        fund_type (FundType): Type of fund (NAV_BASED or COST_BASED)
    Returns:
        float: Equity change amount
    """
    from src.fund.models import EventType, FundType

    if fund_type == FundType.NAV_BASED:
        if event.event_type == EventType.UNIT_PURCHASE:
            return event.amount or 0.0
        elif event.event_type == EventType.UNIT_SALE:
            return -(event.amount or 0.0)
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
    """Generate a human-readable explanation for the reconciliation differences.
    Returns a string.
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
            explanations.append(f"${net_diff:,.2f} more was received than expected")
        else:
            explanations.append(f"${abs(net_diff):,.2f} less was received than expected")
    
    if not explanations:
        return "Reconciliation matches exactly"
    
    return "; ".join(explanations)


def calculate_nav_event_amounts(nav_events, as_of_date=None):
    """
    Calculate NAV-based fund amounts from NAV update events.
    This is a pure function that takes a list of events and returns calculated amounts.
    
    Args:
        nav_events: List of FundEvent objects with NAV_UPDATE event_type
        as_of_date: Calculate as of this date. If None, calculates to the end.
    
    Returns:
        dict: Dictionary with 'current_units', 'current_unit_price', 'current_value'
    """
    if not nav_events:
        return {
            'current_units': 0.0,
            'current_unit_price': 0.0,
            'current_value': 0.0
        }
    
    # Filter events by date if specified
    if as_of_date:
        nav_events = [e for e in nav_events if e.event_date <= as_of_date]
    
    if not nav_events:
        return {
            'current_units': 0.0,
            'current_unit_price': 0.0,
            'current_value': 0.0
        }
    
    # Get the most recent NAV event
    latest_nav = max(nav_events, key=lambda e: e.event_date)
    
    current_units = latest_nav.units_owned or 0.0
    current_unit_price = latest_nav.nav_per_share or 0.0
    current_value = current_units * current_unit_price
    
    return {
        'current_units': current_units,
        'current_unit_price': current_unit_price,
        'current_value': current_value
    }


def get_unit_events_for_fund(unit_events, as_of_date=None):
    """
    Get unit events (purchases and sales) for NAV-based funds up to a given date.
    This is a pure function that filters a list of events.
    
    Args:
        unit_events: List of FundEvent objects with UNIT_PURCHASE and UNIT_SALE event_types
        as_of_date: Get events up to this date. If None, gets all events.
    
    Returns:
        list: Filtered list of unit events
    """
    from src.fund.models import EventType
    
    # Filter by event type
    unit_events = [e for e in unit_events if e.event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]]
    
    # Filter by date if specified
    if as_of_date:
        unit_events = [e for e in unit_events if e.event_date <= as_of_date]
    
    return unit_events


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


def calculate_cumulative_units_and_cost_basis(unit_events, as_of_date=None):
    """
    Calculate cumulative units and cost basis for NAV-based funds using FIFO method.
    This is a pure function for cost basis calculations.
    
    Args:
        unit_events (list): List of FundEvent objects with UNIT_PURCHASE and UNIT_SALE events
        as_of_date (date, optional): Calculate as of this date. If None, calculates to the end.
    
    Returns:
        dict: Dictionary with 'total_units', 'total_cost_basis', 'average_cost_per_unit'
    """
    from src.fund.models import EventType
    
    # Filter events by date if specified
    if as_of_date:
        unit_events = [e for e in unit_events if e.event_date <= as_of_date]
    
    # Filter to only unit events
    unit_events = [e for e in unit_events if e.event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]]
    
    # Sort by date
    unit_events.sort(key=lambda e: e.event_date)
    
    total_units = 0.0
    total_cost_basis = 0.0
    
    for event in unit_events:
        if event.event_type == EventType.UNIT_PURCHASE:
            units = event.units_purchased or 0.0
            cost = event.amount or 0.0
            total_units += units
            total_cost_basis += cost
        elif event.event_type == EventType.UNIT_SALE:
            units_sold = event.units_sold or 0.0
            if units_sold > total_units:
                # Can't sell more than we own
                units_sold = total_units
            
            if total_units > 0:
                # Calculate cost of units sold using FIFO
                cost_per_unit = total_cost_basis / total_units
                cost_of_units_sold = units_sold * cost_per_unit
                total_cost_basis -= cost_of_units_sold
            
            total_units -= units_sold
    
    average_cost_per_unit = total_cost_basis / total_units if total_units > 0 else 0.0
    
    return {
        'total_units': total_units,
        'total_cost_basis': total_cost_basis,
        'average_cost_per_unit': average_cost_per_unit
    } 