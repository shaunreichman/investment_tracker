"""
Fund calculations module.

This module contains fund-specific calculation functions that use the shared calculations.
"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..shared.calculations import (
    calculate_irr,
    get_equity_change_for_event,
    get_risk_free_rate_for_date,
    get_financial_years_for_fund_period,
    calculate_nav_event_amounts,
    get_unit_events_for_fund,
    calculate_nav_based_cost_basis_for_irr,
    calculate_cumulative_units_and_cost_basis
)
from .models import Fund, FundEvent, EventType, FundType, DistributionType


def calculate_average_equity_balance_nav(fund_events, start_date, end_date):
    """
    Calculate average equity balance for NAV-based funds.
    This is a pure function that takes events and returns the average equity balance.
    
    Args:
        fund_events: List of FundEvent objects for the fund
        start_date: Start date for calculation
        end_date: End date for calculation
    
    Returns:
        float: Average equity balance over the period
    """
    if not fund_events:
        return 0.0
    
    # Sort events by date
    fund_events.sort(key=lambda e: e.event_date)
    
    # Filter events to the period (exclusive end date)
    period_events = [e for e in fund_events if start_date <= e.event_date < end_date]
    
    if not period_events:
        return 0.0
    
    # Calculate equity balance at each event
    current_equity = 0.0
    total_weighted_equity = 0.0
    last_date = start_date
    
    for event in period_events:
        # Calculate weighted equity for the period since last event
        days_since_last = (event.event_date - last_date).days
        if days_since_last > 0:
            total_weighted_equity += current_equity * days_since_last
        
        # Update equity for this event
        current_equity += get_equity_change_for_event(event, FundType.NAV_BASED)
        last_date = event.event_date
    
    # Add final period to end_date
    days_to_end = (end_date - last_date).days
    if days_to_end > 0:
        total_weighted_equity += current_equity * days_to_end
    
    total_days = (end_date - start_date).days
    if total_days == 0:
        return current_equity
    
    return total_weighted_equity / total_days


def calculate_average_equity_balance_cost(fund_events, start_date, end_date):
    """
    Calculate average equity balance for cost-based funds.
    This is a pure function that takes events and returns the average equity balance.
    
    Args:
        fund_events: List of FundEvent objects for the fund
        start_date: Start date for calculation
        end_date: End date for calculation
    
    Returns:
        float: Average equity balance over the period
    """
    if not fund_events:
        return 0.0
    
    # Sort events by date
    fund_events.sort(key=lambda e: e.event_date)
    
    # Filter events to the period (exclusive end date)
    period_events = [e for e in fund_events if start_date <= e.event_date < end_date]
    
    if not period_events:
        return 0.0
    
    # Calculate equity balance at each event
    current_equity = 0.0
    total_weighted_equity = 0.0
    last_date = start_date
    
    for event in period_events:
        # Calculate weighted equity for the period since last event
        days_since_last = (event.event_date - last_date).days
        if days_since_last > 0:
            total_weighted_equity += current_equity * days_since_last
        
        # Update equity for this event
        current_equity += get_equity_change_for_event(event, FundType.COST_BASED)
        last_date = event.event_date
    
    # Add final period to end_date
    days_to_end = (end_date - last_date).days
    if days_to_end > 0:
        total_weighted_equity += current_equity * days_to_end
    
    total_days = (end_date - start_date).days
    if total_days == 0:
        return current_equity
    
    return total_weighted_equity / total_days


def calculate_debt_cost(fund_events, start_date, end_date):
    """
    Calculate debt cost for real IRR calculations.
    This is a pure function that takes events and returns the debt cost.
    
    Args:
        fund_events: List of FundEvent objects for the fund
        start_date: Start date for calculation
        end_date: End date for calculation
    
    Returns:
        float: Total debt cost over the period
    """
    if not fund_events:
        return 0.0
    
    # Filter to debt cost events in the period
    debt_events = [
        e for e in fund_events 
        if e.event_type == EventType.FY_DEBT_COST 
        and start_date <= e.event_date < end_date
    ]
    
    return sum(e.amount or 0.0 for e in debt_events)


def calculate_nav_based_capital_gains(fund_events, as_of_date=None):
    """
    Calculate capital gains for NAV-based funds.
    This is a pure function that takes events and returns capital gains.
    
    Args:
        fund_events: List of FundEvent objects for the fund
        as_of_date: Calculate as of this date. If None, calculates to the end.
    
    Returns:
        float: Total capital gains
    """
    if not fund_events:
        return 0.0
    
    # Filter to unit sale events
    unit_sales = [e for e in fund_events if e.event_type == EventType.UNIT_SALE]
    
    if as_of_date:
        unit_sales = [e for e in unit_sales if e.event_date <= as_of_date]
    
    if not unit_sales:
        return 0.0
    
    # Calculate capital gains for each sale
    total_capital_gains = 0.0
    
    for sale in unit_sales:
        # Get all unit purchases before this sale
        purchases = [
            e for e in fund_events 
            if e.event_type == EventType.UNIT_PURCHASE 
            and e.event_date <= sale.event_date
        ]
        
        if not purchases:
            continue
        
        # Calculate cost basis for units sold
        units_sold = sale.units_sold or 0.0
        sale_proceeds = sale.amount or 0.0
        
        # Simple average cost method for now
        total_units_purchased = sum(p.units_purchased or 0.0 for p in purchases)
        total_cost = sum(p.amount or 0.0 for p in purchases)
        
        if total_units_purchased > 0:
            avg_cost_per_unit = total_cost / total_units_purchased
            cost_basis = units_sold * avg_cost_per_unit
            capital_gain = sale_proceeds - cost_basis
            total_capital_gains += capital_gain
    
    return total_capital_gains


def calculate_cost_based_capital_gains(fund_events, as_of_date=None):
    """
    Calculate capital gains for cost-based funds.
    This is a pure function that takes events and returns capital gains.
    
    Args:
        fund_events: List of FundEvent objects for the fund
        as_of_date: Calculate as of this date. If None, calculates to the end.
    
    Returns:
        float: Total capital gains
    """
    if not fund_events:
        return 0.0
    
    # For cost-based funds, capital gains are distributions of type CAPITAL_GAIN
    capital_gain_distributions = [
        e for e in fund_events 
        if e.event_type == EventType.DISTRIBUTION 
        and e.distribution_type == DistributionType.CAPITAL_GAIN
    ]
    
    if as_of_date:
        capital_gain_distributions = [e for e in capital_gain_distributions if e.event_date <= as_of_date]
    
    return sum(e.amount or 0.0 for e in capital_gain_distributions)


def orchestrate_nav_based_average_equity(fund_events, start_date, end_date):
    """
    Orchestrate average equity calculation for NAV-based funds.
    This is a pure function that delegates to the specific calculation.
    
    Args:
        fund_events: List of FundEvent objects for the fund
        start_date: Start date for calculation
        end_date: End date for calculation
    
    Returns:
        float: Average equity balance over the period
    """
    return calculate_average_equity_balance_nav(fund_events, start_date, end_date)


def orchestrate_cost_based_average_equity(fund_events, start_date, end_date):
    """
    Orchestrate average equity calculation for cost-based funds.
    This is a pure function that delegates to the specific calculation.
    
    Args:
        fund_events: List of FundEvent objects for the fund
        start_date: Start date for calculation
        end_date: End date for calculation
    
    Returns:
        float: Average equity balance over the period
    """
    return calculate_average_equity_balance_cost(fund_events, start_date, end_date)


def orchestrate_irr_base(fund_events, start_date, end_date):
    """
    Orchestrate IRR calculation base logic.
    This is a pure function that prepares cash flows for IRR calculation.
    
    Args:
        fund_events: List of FundEvent objects for the fund
        start_date: Start date for calculation
        end_date: End date for calculation
    
    Returns:
        tuple: (cash_flows, days_from_start) for IRR calculation
    """
    if not fund_events:
        return [], []
    
    # Sort events by date
    fund_events.sort(key=lambda e: e.event_date)
    
    # Filter events to the period
    period_events = [e for e in fund_events if start_date <= e.event_date <= end_date]
    
    cash_flows = []
    days_from_start = []
    
    for event in period_events:
        # Determine cash flow amount based on event type
        if event.event_type in [EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE]:
            # Outflow (negative)
            amount = -(event.amount or 0.0)
        elif event.event_type in [EventType.RETURN_OF_CAPITAL, EventType.UNIT_SALE, EventType.DISTRIBUTION]:
            # Inflow (positive)
            amount = event.amount or 0.0
        else:
            # Skip other event types for IRR
            continue
        
        if amount != 0:
            cash_flows.append(amount)
            days = (event.event_date - start_date).days
            days_from_start.append(days)
    
    return cash_flows, days_from_start


# Tax calculation functions (these will be moved to tax domain later)
def net_income(gross_income, expenses):
    """Calculate net income from gross income and expenses."""
    return gross_income - expenses


def tax_payable(net_income, tax_rate):
    """Calculate tax payable from net income and tax rate."""
    return net_income * (tax_rate / 100)


def interest_tax_benefit(interest_expense, tax_rate):
    """Calculate tax benefit from interest expense."""
    return interest_expense * (tax_rate / 100) 