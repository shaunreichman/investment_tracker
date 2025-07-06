"""
Entity domain calculations.

This module contains entity-specific calculation functions.
"""

from datetime import date


def get_financial_years_for_fund_period(start_date, end_date, entity):
    """
    Get all financial years between start and end dates.
    
    Args:
        start_date (date): Start date for the period
        end_date (date): End date for the period
        entity: Entity object with get_financial_year method
    
    Returns:
        set: Set of financial year strings
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


__all__ = [
    'get_financial_years_for_fund_period',
] 