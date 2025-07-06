"""
Investment Tracker Package

A SQLAlchemy-based investment tracking system for managing investment companies, funds, and fund events.
"""

# Entity domain
from .entity.models import Entity
from .entity.calculations import get_financial_years_for_fund_period
from .entity.creation import create_entity, get_entity_by_name, get_all_entities

# Fund domain
from .fund.models import Fund, FundEvent, FundType, EventType, DistributionType, TaxPaymentType
from .fund.calculations import (
    calculate_irr, calculate_average_equity_balance_nav, calculate_average_equity_balance_cost,
    calculate_debt_cost, calculate_nav_based_capital_gains, calculate_cost_based_capital_gains,
    orchestrate_nav_based_average_equity, orchestrate_cost_based_average_equity, orchestrate_irr_base,
    calculate_nav_event_amounts, calculate_cumulative_units_and_cost_basis, calculate_nav_based_cost_basis_for_irr
)
from .fund.creation import *

# Tax domain
from .tax.models import TaxStatement
from .tax.calculations import net_income, tax_payable, interest_tax_benefit
from .tax.creation import *

# Rates domain
from .rates.models import RiskFreeRate
from .rates.calculations import get_risk_free_rate_for_date
from .rates.creation import *

# Investment company domain
from .investment_company.models import InvestmentCompany
from .investment_company.calculations import *
from .investment_company.creation import *

# Shared utilities
from .shared.utils import with_session
from .shared.calculations import *

__version__ = "1.0.0"
__author__ = "Investment Tracker"

__all__ = [
    # Entity
    'Entity', 'get_financial_years_for_fund_period', 'create_entity', 'get_entity_by_name', 'get_all_entities',
    
    # Fund
    'Fund', 'FundEvent', 'FundType', 'EventType', 'DistributionType', 'TaxPaymentType',
    'calculate_irr', 'calculate_average_equity_balance_nav', 'calculate_average_equity_balance_cost',
    'calculate_debt_cost', 'calculate_nav_based_capital_gains', 'calculate_cost_based_capital_gains',
    'orchestrate_nav_based_average_equity', 'orchestrate_cost_based_average_equity', 'orchestrate_irr_base',
    'calculate_nav_event_amounts', 'calculate_cumulative_units_and_cost_basis', 'calculate_nav_based_cost_basis_for_irr',
    'FundCreationMixin', 'FundUpdateMixin',
    
    # Tax
    'TaxStatement', 'net_income', 'tax_payable', 'interest_tax_benefit',
    'create_or_update_tax_statement', 'create_tax_payment_events',
    
    # Rates
    'RiskFreeRate', 'get_risk_free_rate_for_date',
    'create_risk_free_rate', 'get_risk_free_rates_for_currency', 'get_all_risk_free_rates',
    
    # Investment Company
    'InvestmentCompany',
    'calculate_total_funds_under_management', 'calculate_total_commitments',
    'create_investment_company', 'get_investment_company_by_name', 'get_all_investment_companies',
    
    # Shared
    'with_session',
    'get_equity_change_for_event', 'get_reconciliation_explanation',
    'get_unit_events_for_fund', 'get_financial_year_dates',
] 