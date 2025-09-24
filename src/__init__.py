"""
Investment Tracker Package

A SQLAlchemy-based investment tracking system for managing investment companies, funds, and fund events.
"""

from banking.models import Bank, BankAccount
from entity.models import Entity
from fund.models import Fund, FundEvent, FundEventCashFlow, FundTaxStatement
from investment_company.models import InvestmentCompany, Contact
from rates.models import RiskFreeRate


__version__ = "1.0.0"
__author__ = "Investment Tracker"

__all__ = [
    'Bank',
    'BankAccount',
    'Entity',
    'Fund',
    'FundEvent',
    'FundEventCashFlow',
    'FundTaxStatement',
    'InvestmentCompany',
    'Contact',
    'RiskFreeRate',
] 