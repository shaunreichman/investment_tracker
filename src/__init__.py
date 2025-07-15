"""
Investment Tracker Package

A SQLAlchemy-based investment tracking system for managing investment companies, funds, and fund events.
"""

# Entity domain
from .entity.models import Entity
from .entity.calculations import get_financial_years_for_fund_period

# Fund domain
from .fund.models import Fund, FundEvent, FundType, EventType, DistributionType, TaxPaymentType
from .fund.calculations import (
    calculate_irr, calculate_average_equity_balance_nav, calculate_average_equity_balance_cost,
    calculate_debt_cost, calculate_nav_based_capital_gains, calculate_cost_based_capital_gains,
    orchestrate_irr_base,
)

# Tax domain
from .tax.models import TaxStatement
from .tax.calculations import tax_payable, calculate_fy_debt_interest_deduction_total_deduction

# Rates domain
from .rates.models import RiskFreeRate
from .rates.calculations import get_risk_free_rate_for_date

# Investment company domain
from .investment_company.models import InvestmentCompany
from .investment_company.calculations import calculate_total_funds_under_management, calculate_total_commitments

# Shared utilities
from .shared.utils import with_session
from .shared.calculations import *

__version__ = "1.0.0"
__author__ = "Investment Tracker"

__all__ = [
    # Entity
    'Entity', 'get_financial_years_for_fund_period',
    
    # Fund
    'Fund', 'FundEvent', 'FundType', 'EventType', 'DistributionType', 'TaxPaymentType',
    'calculate_irr', 'calculate_average_equity_balance_nav', 'calculate_average_equity_balance_cost',
    'calculate_debt_cost', 'calculate_nav_based_capital_gains', 'calculate_cost_based_capital_gains',
    'orchestrate_irr_base',
    
    # Tax
    'TaxStatement', 'tax_payable', 'calculate_fy_debt_interest_deduction_total_deduction',
    
    # Rates
    'RiskFreeRate', 'get_risk_free_rate_for_date',
    
    # Investment Company
    'InvestmentCompany',
    'calculate_total_funds_under_management', 'calculate_total_commitments',
    
    # Shared
    'with_session',
    'get_equity_change_for_event', 'get_reconciliation_explanation',
    'get_unit_events_for_fund', 'get_financial_year_dates',
] 