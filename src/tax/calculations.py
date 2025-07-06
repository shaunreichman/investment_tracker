"""
Tax calculations module.

This module contains tax-specific calculation functions for tax statements and related models.
"""

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


__all__ = [
    'net_income',
    'tax_payable',
    'interest_tax_benefit',
] 