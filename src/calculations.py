"""
Calculation utilities for investment tracker.

This module provides core financial calculation utilities used throughout the investment tracker system, including:
- Internal Rate of Return (IRR) calculations with daily/monthly precision
- Average equity balance calculations for both NAV-based and cost-based funds
- Debt cost (opportunity cost) calculations using risk-free rates

These utilities are used by Fund and related models to support performance measurement, tax calculations, and reporting.
"""

from datetime import date, timedelta
import numpy as np
import numpy_financial as npf

# IRR calculation utility
def calculate_irr(cash_flows, days_from_start, tolerance=1e-10, max_iterations=200):
    """
    Calculate monthly IRR using daily precision with the Newton-Raphson method.
    
    Args:
        cash_flows (list[float]): List of cash flow amounts (negative for outflows, positive for inflows).
        days_from_start (list[int]): List of days from the start date for each cash flow.
        tolerance (float): Convergence tolerance for the root-finding algorithm.
        max_iterations (int): Maximum number of iterations to attempt.
    
    Returns:
        float or None: The monthly IRR as a decimal (e.g., 0.01 for 1%), or None if not computable.
    
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
            return monthly_guess
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
        end_date (date): End date for the calculation period.
    
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
    # Initialize daily cost basis for each day in the period
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
        while current_date <= end_date:
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
                # Calculate opportunity cost for this sub-period
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

def get_equity_change_for_event(event, fund_type):
    """
    Calculate how much an event changes a fund's equity balance.
    Args:
        event: An object with event_type and amount attributes (and units for unit events).
        fund_type: The type of fund (e.g., FundType.NAV_BASED or FundType.COST_BASED).
    Returns:
        float: Signed change in equity (positive for inflows, negative for outflows).
    """
    from .models import EventType
    if event.event_type == EventType.CAPITAL_CALL:
        return event.amount or 0
    elif event.event_type == EventType.RETURN_OF_CAPITAL:
        return -(event.amount or 0)
    elif event.event_type == EventType.UNIT_PURCHASE:
        return event.amount or 0
    elif event.event_type == EventType.UNIT_SALE:
        return -(event.amount or 0)
    elif event.event_type == EventType.DISTRIBUTION:
        return -(event.amount or 0)
    elif event.event_type == EventType.TAX_PAYMENT:
        return -(event.amount or 0)
    elif event.event_type == EventType.MANAGEMENT_FEE:
        return -(event.amount or 0)
    elif event.event_type == EventType.CARRIED_INTEREST:
        return -(event.amount or 0)
    elif event.event_type == EventType.FY_DEBT_COST:
        return event.amount or 0
    elif event.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE:
        return -(event.amount or 0)
    elif event.event_type == EventType.NAV_UPDATE:
        # NAV updates don't change equity balance, they just update the NAV
        return 0
    else:
        return 0

def calculate_nav_based_capital_gains(events):
    """
    Calculate capital gains for NAV-based funds using FIFO on unit sales.
    Args:
        events: List of event objects with event_type, units_purchased, units_sold, unit_price, and event_date.
    Returns:
        float: Total capital gains.
    """
    from .models import EventType
    
    # Use shared utility to get purchase and sale data
    result = calculate_cumulative_units_and_cost_basis(events)
    unit_purchases = result['unit_purchases']
    unit_sales = result['unit_sales']
    
    # FIFO calculation
    total_capital_gains = 0
    available_units = []  # List of (units, cost_basis_per_unit, date)
    
    # Sort all events by date for FIFO processing
    all_events = sorted(events, key=lambda x: x.event_date)
    
    for event in all_events:
        if event.event_type == EventType.UNIT_PURCHASE:
            units = event.units_purchased or 0
            cost_per_unit = event.unit_price or 0
            if units > 0 and cost_per_unit > 0:
                available_units.append((units, cost_per_unit, event.event_date))
        elif event.event_type == EventType.UNIT_SALE:
            units_to_sell = event.units_sold or 0
            sale_price_per_unit = event.unit_price or 0
            while units_to_sell > 0 and available_units:
                available_units_count, cost_per_unit, purchase_date = available_units[0]
                units_from_this_purchase = min(units_to_sell, available_units_count)
                # Calculate capital gain for these units
                capital_gain = (sale_price_per_unit - cost_per_unit) * units_from_this_purchase
                total_capital_gains += capital_gain
                # Update available units
                units_to_sell -= units_from_this_purchase
                remaining_units = available_units_count - units_from_this_purchase
                if remaining_units > 0:
                    available_units[0] = (remaining_units, cost_per_unit, purchase_date)
                else:
                    available_units.pop(0)
    return total_capital_gains

def calculate_cost_based_capital_gains(events):
    """
    Calculate capital gains for cost-based funds from explicit capital gain events.
    Args:
        events: List of event objects with event_type and amount attributes.
    Returns:
        float: Total capital gains (sum of relevant events).
    """
    from .models import EventType
    # Sum all DISTRIBUTION events (or filter by a more specific type if needed)
    return sum(e.amount or 0 for e in events if e.event_type == EventType.DISTRIBUTION)

def orchestrate_nav_based_average_equity(unit_events):
    """
    Orchestrate average equity calculation for NAV-based funds.
    Args:
        unit_events (list): List of FundEvent-like objects with event_date attribute.
    Returns:
        float: Average equity balance over the period.
    """
    if not unit_events:
        return 0
    start_date = min(event.event_date for event in unit_events)
    end_date = max(event.event_date for event in unit_events)
    from datetime import date
    # If the fund is still active, end_date could be today (handled by caller if needed)
    return calculate_average_equity_balance_nav(unit_events, start_date, end_date)

def orchestrate_cost_based_average_equity(capital_events):
    """
    Orchestrate average equity calculation for cost-based funds.
    Args:
        capital_events (list): List of FundEvent-like objects.
    Returns:
        float: Average equity balance over the period.
    """
    if not capital_events:
        return 0
    return calculate_average_equity_balance_cost(capital_events)

def orchestrate_irr_base(cash_flow_events, start_date, include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, return_cashflows=False):
    """
    Orchestrate IRR calculation for a fund, given a list of cash flow events and options.
    Args:
        cash_flow_events (list): List of events with event_type, amount, event_date, and description.
        start_date (date): The start date for IRR calculation.
        include_tax_payments (bool): Whether to include tax payment events.
        include_risk_free_charges (bool): Whether to include risk-free charge events.
        include_fy_debt_cost (bool): Whether to include FY debt cost events.
        return_cashflows (bool): Whether to return cash flow details for reporting.
    Returns:
        float or dict: IRR as a float, or dict with cash flow details if return_cashflows is True.
    """
    from .models import EventType
    # Define event types to include
    event_types = [
        EventType.CAPITAL_CALL,
        EventType.UNIT_PURCHASE,
        EventType.RETURN_OF_CAPITAL,
        EventType.DISTRIBUTION,
        EventType.MANAGEMENT_FEE,
        EventType.CARRIED_INTEREST
    ]
    if include_fy_debt_cost:
        event_types.append(EventType.FY_DEBT_COST)
    if include_tax_payments:
        event_types.append(EventType.TAX_PAYMENT)
    if include_risk_free_charges:
        event_types.append(EventType.DAILY_RISK_FREE_INTEREST_CHARGE)
    # Filter events
    filtered_events = [e for e in cash_flow_events if e.event_type in event_types]
    if not filtered_events:
        if return_cashflows:
            return {'cash_flows': [], 'days_from_start': [], 'labels': [], 'irr': None}
        return None
    # Prepare cash flows with daily precision
    cash_flows = []
    days_from_start = []
    labels = []
    for event in filtered_events:
        days = (event.event_date - start_date).days
        days_from_start.append(days)
        label = f"{event.event_type.value} | {event.event_date} | {event.amount:,.2f}"
        if getattr(event, 'description', None):
            label += f" | {event.description}"
        labels.append(label)
        # Handle each event type appropriately
        if event.event_type == EventType.CAPITAL_CALL:
            cash_flows.append(-event.amount)
        elif event.event_type == EventType.RETURN_OF_CAPITAL:
            cash_flows.append(event.amount)
        elif event.event_type == EventType.DISTRIBUTION:
            cash_flows.append(event.amount)
        elif event.event_type == EventType.TAX_PAYMENT:
            cash_flows.append(-event.amount)
        elif event.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE:
            cash_flows.append(-event.amount)
        elif event.event_type == EventType.MANAGEMENT_FEE:
            cash_flows.append(-event.amount)
        elif event.event_type == EventType.CARRIED_INTEREST:
            cash_flows.append(-event.amount)
        elif event.event_type == EventType.FY_DEBT_COST:
            cash_flows.append(event.amount)
        else:
            from .calculations import get_equity_change_for_event
            cash_flows.append(-get_equity_change_for_event(event, None))
    # Add final value as last cash flow (if needed, handled by caller)
    try:
        monthly_irr = calculate_irr(cash_flows, days_from_start)
        if monthly_irr is None:
            if return_cashflows:
                return {'cash_flows': cash_flows, 'days_from_start': days_from_start, 'labels': labels, 'irr': None}
            return None
        annual_irr = (1 + monthly_irr) ** 12 - 1
        if return_cashflows:
            return {'cash_flows': cash_flows, 'days_from_start': days_from_start, 'labels': labels, 'irr': annual_irr}
        return annual_irr
    except Exception:
        if return_cashflows:
            return {'cash_flows': cash_flows, 'days_from_start': days_from_start, 'labels': labels, 'irr': None}
        return None

def net_income(total_income, non_resident_withholding_tax_from_statement):
    """
    Calculate net income after non-resident withholding tax from statement.
    Args:
        total_income (float): Total income.
        non_resident_withholding_tax_from_statement (float): Tax withheld from statement.
    Returns:
        float: Net income.
    """
    return (total_income or 0.0) - (non_resident_withholding_tax_from_statement or 0.0)

def tax_payable(total_interest_income, interest_taxable_rate, non_resident_withholding_tax_from_statement):
    """
    Calculate tax payable as (total_interest_income * interest_taxable_rate / 100) - non_resident_withholding_tax_from_statement.
    Args:
        total_interest_income (float): Total interest income.
        interest_taxable_rate (float): Taxable rate as a percentage.
        non_resident_withholding_tax_from_statement (float): Tax withheld from statement.
    Returns:
        float: Tax payable (never negative).
    """
    if interest_taxable_rate and total_interest_income and interest_taxable_rate != 0 and total_interest_income > 0:
        total_tax_liability = total_interest_income * (interest_taxable_rate / 100)
        return max(0, total_tax_liability - (non_resident_withholding_tax_from_statement or 0.0))
    return 0.0

def interest_tax_benefit(total_interest_expense, interest_deduction_rate):
    """
    Calculate the tax benefit from interest expense deduction.
    Args:
        total_interest_expense (float): Total interest expense.
        interest_deduction_rate (float): Deduction rate as a percentage.
    Returns:
        float: Tax benefit.
    """
    if total_interest_expense and interest_deduction_rate:
        return (total_interest_expense * interest_deduction_rate) / 100
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

def calculate_nav_event_amounts(fund_id, session):
    """Calculate amounts for unit purchases/sales and shares_owned for NAV updates.
    This function ensures that:
    - Unit purchase/sale amounts = units * unit_price + brokerage_fee
    - NAV update shares_owned = cumulative units from all unit events up to that date
    
    Note: This function does NOT commit the session - the calling method should handle commits.
    """
    from models import FundEvent, EventType
    
    # Get all unit events for this fund
    unit_events = get_unit_events_for_fund(fund_id, session, include_nav_updates=True)
    
    # Calculate amounts for unit purchases/sales
    for event in unit_events:
        if event.event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]:
            if event.event_type == EventType.UNIT_PURCHASE:
                units = event.units_purchased or 0
                unit_price = event.unit_price or 0
                brokerage_fee = event.brokerage_fee or 0
                event.amount = (units * unit_price) + brokerage_fee
            elif event.event_type == EventType.UNIT_SALE:
                units = event.units_sold or 0
                unit_price = event.unit_price or 0
                brokerage_fee = event.brokerage_fee or 0
                event.amount = (units * unit_price) - brokerage_fee  # Negative for sales
    
    # Calculate shares_owned for NAV updates using shared utility
    cumulative_units = 0.0
    for event in unit_events:
        if event.event_type == EventType.UNIT_PURCHASE:
            cumulative_units += event.units_purchased or 0
        elif event.event_type == EventType.UNIT_SALE:
            cumulative_units -= event.units_sold or 0
        elif event.event_type == EventType.NAV_UPDATE:
            event.shares_owned = cumulative_units

def get_unit_events_for_fund(fund_id, session, include_nav_updates=False):
    """
    Get all unit purchase/sale events for a fund, optionally including NAV updates.
    Shared utility for NAV-based calculations.
    
    Args:
        fund_id (int): The fund ID
        session: Database session
        include_nav_updates (bool): Whether to include NAV_UPDATE events in the query
    
    Returns:
        list: List of FundEvent objects ordered by event_date
    """
    from models import FundEvent, EventType
    
    event_types = [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]
    if include_nav_updates:
        event_types.append(EventType.NAV_UPDATE)
    
    return session.query(FundEvent).filter(
        FundEvent.fund_id == fund_id,
        FundEvent.event_type.in_(event_types)
    ).order_by(FundEvent.event_date).all()

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
    from models import EventType
    
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

def calculate_nav_based_cost_basis_for_irr(fund_id, session, as_of_date=None):
    """
    Calculate the cost basis for NAV-based funds up to a given date.
    This is used for IRR calculations where we need to know the total amount invested.
    
    Args:
        fund_id (int): The fund ID
        session: Database session
        as_of_date (date, optional): Calculate as of this date. If None, calculates to the end.
    
    Returns:
        float: Total cost basis (sum of all unit purchases minus unit sales)
    """
    unit_events = get_unit_events_for_fund(fund_id, session, include_nav_updates=False)
    result = calculate_cumulative_units_and_cost_basis(unit_events, as_of_date)
    return result['total_cost_basis'] 