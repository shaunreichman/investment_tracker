"""
Tax calculations module.

This module contains tax-specific calculation functions for tax statements and related models.
"""


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
    'tax_payable',
    'calculate_fy_debt_interest_deduction_total_deduction',
] 