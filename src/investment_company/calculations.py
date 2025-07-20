"""
Investment company domain calculations.

This module contains investment company-specific calculation functions.
"""


def calculate_total_funds_under_management(investment_company, session):
    """
    Calculate the total number of funds managed by an investment company.
    
    Args:
        investment_company: InvestmentCompany object
        session: Database session
    
    Returns:
        int: Total number of funds
    """
    return len(investment_company.funds)


def calculate_total_commitments(investment_company, session):
    """
    Calculate the total commitments across all funds managed by an investment company.
    
    Args:
        investment_company: InvestmentCompany object
        session: Database session
    
    Returns:
        float: Total commitments across all funds
    """
    total_commitments = 0.0
    for fund in investment_company.funds:
        if fund.commitment_amount:
            total_commitments += fund.commitment_amount
    return total_commitments


__all__ = [
    'calculate_total_funds_under_management',
    'calculate_total_commitments',
] 