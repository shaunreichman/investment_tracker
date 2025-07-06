"""
Rates domain calculations.

This module contains rates-specific calculation functions.
"""


def get_risk_free_rate_for_date(target_date, risk_free_rates):
    """
    Get the risk-free rate for a specific date from a list of rates.
    Returns the most recent rate available on or before the target date, or None if not found.
    
    Args:
        target_date (date): The date to find a rate for
        risk_free_rates (list): List of RiskFreeRate objects, sorted by date
    
    Returns:
        float or None: The risk-free rate as a percentage, or None if not found
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


__all__ = [
    'get_risk_free_rate_for_date',
] 