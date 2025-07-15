"""
Tax calculations module.

This module contains tax-specific calculation functions for tax statements and related models.
"""


def calculate_fy_debt_interest_deduction_total_deduction(fy_debt_interest_deduction_sum_of_daily_interest, fy_debt_interest_deduction_rate):
    """
    Calculate the tax benefit from interest expense deduction.
    
    Args:
        fy_debt_interest_deduction_sum_of_daily_interest (float): Total interest expense.
        fy_debt_interest_deduction_rate (float): Deduction rate as a percentage.
    
    Returns:
        float: The calculated tax benefit.
    """
    if fy_debt_interest_deduction_sum_of_daily_interest and fy_debt_interest_deduction_rate:
        return (fy_debt_interest_deduction_sum_of_daily_interest * fy_debt_interest_deduction_rate) / 100
    return 0.0


__all__ = [
    'calculate_fy_debt_interest_deduction_total_deduction',
] 