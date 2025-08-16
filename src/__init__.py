"""
Investment Tracker Package

A SQLAlchemy-based investment tracking system for managing investment companies, funds, and fund events.
"""

# Entity domain
from src.entity.models import Entity
from src.entity.calculations import get_financial_years_for_fund_period

# Fund domain
from src.fund.models import Fund, FundEvent
from src.fund.enums import FundType, EventType, DistributionType, TaxPaymentType
from src.fund.calculations import (
    calculate_irr,
    calculate_debt_cost, calculate_nav_based_capital_gains, calculate_cost_based_capital_gains
)
from src.shared.calculations import orchestrate_irr_base

# Tax domain
from src.tax.models import TaxStatement

# Rates domain
from src.rates.models import RiskFreeRate
from src.rates.calculations import get_risk_free_rate_for_date

# Investment company domain
from src.investment_company.models import InvestmentCompany
from src.investment_company.calculations import calculate_total_funds_under_management, calculate_total_commitments

# Shared utilities
from src.shared.utils import with_session
from src.shared.calculations import *

__version__ = "1.0.0"
__author__ = "Investment Tracker"

__all__ = [
    # Entity
    'Entity', 'get_financial_years_for_fund_period',
    
    # Fund
    'Fund', 'FundEvent', 'FundType', 'EventType', 'DistributionType', 'TaxPaymentType',
    'calculate_irr',
    'calculate_debt_cost', 'calculate_nav_based_capital_gains', 'calculate_cost_based_capital_gains',
    'orchestrate_irr_base',
    
    # Tax
    'TaxStatement',
    
    # Rates
    'RiskFreeRate', 'get_risk_free_rate_for_date',
    
    # Investment Company
    'InvestmentCompany',
    'calculate_total_funds_under_management', 'calculate_total_commitments',
    
    # Shared
    'with_session',
    'get_equity_change_for_event', 'get_reconciliation_explanation',
    'get_financial_year_dates',
] 