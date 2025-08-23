"""
Shared calculations module.

This module contains pure calculation functions that can be used across different domains.
These functions do not depend on database sessions and are purely mathematical.
"""

from datetime import date
from typing import Optional





def get_financial_year_dates(financial_year, tax_jurisdiction="AU"):
    """
    Get the start and end dates for a financial year based on jurisdiction.
    Args:
        financial_year (str): Financial year string (e.g., '2023-24' or '2023').
        tax_jurisdiction (str): Jurisdiction code (e.g., 'AU').
    Returns:
        tuple: (start_date, end_date) as datetime.date objects.
    Raises:
        ValueError: If financial_year is None, empty, or invalid format.
    """
    # Validate input
    if financial_year is None:
        raise ValueError("Financial year cannot be None")
    if not financial_year:
        raise ValueError("Financial year cannot be empty")
    
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
        try:
            year = int(financial_year)
        except ValueError:
            raise ValueError(f"Invalid financial year format: {financial_year}")
        
        if tax_jurisdiction == "AU":
            fy_start = date(year, 7, 1)
            fy_end = date(year + 1, 6, 30)
        else:
            fy_start = date(year, 1, 1)
            fy_end = date(year, 12, 31)
    return fy_start, fy_end


__all__ = [
    'get_financial_year_dates',
] 