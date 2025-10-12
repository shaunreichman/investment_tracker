"""
Investment Tracker Package

A SQLAlchemy-based investment tracking system for managing  companies, funds, and fund events.
"""

from src.banking.models import Bank, BankAccount
from src.entity.models import Entity
from src.fund.models import Fund, FundEvent, FundEventCashFlow, FundTaxStatement
from src.company.models import Company, Contact
from src.rates.models import RiskFreeRate, FxRate


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
    'Company',
    'Contact',
    'RiskFreeRate',
    'FxRate',
] 