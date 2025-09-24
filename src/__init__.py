"""
Investment Tracker Package

A SQLAlchemy-based investment tracking system for managing investment companies, funds, and fund events.
"""

from src.banking.models import Bank, BankAccount
from src.entity.models import Entity
from src.fund.models import Fund, FundEvent, FundEventCashFlow, FundTaxStatement
from src.investment_company.models import InvestmentCompany, Contact
from src.rates.models import RiskFreeRate


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