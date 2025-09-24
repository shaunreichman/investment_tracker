"""
Investment Tracker Package

A SQLAlchemy-based investment tracking system for managing investment companies, funds, and fund events.
"""

# Entity domain
from src.entity.models import Entity
from src.entity.calculations import get_financial_years_for_fund_period

# Fund domain
from src.fund.models import Fund, FundEvent
from src.fund.enums import FundTrackingType, EventType, DistributionType, TaxPaymentType


# Tax domain
from src.tax.models import TaxStatement

# Rates domain
from src.rates.models import RiskFreeRate
from src.rates.calculations import get_risk_free_rate_for_date

# Investment company domain
from src.investment_company.models import InvestmentCompany

# Shared utilities
from src.shared.utils import with_session


__version__ = "1.0.0"
__author__ = "Investment Tracker"

__all__ = [
    # Entity
    'Entity', 'get_financial_years_for_fund_period',
    
    # Fund
    'Fund', 'FundEvent', 'FundTrackingType', 'EventType', 'DistributionType', 'TaxPaymentType',

    
    # Tax
    'TaxStatement',
    
    # Rates
    'RiskFreeRate', 'get_risk_free_rate_for_date',
    
    # Investment Company
    'InvestmentCompany',
    
    # Shared
    'with_session',


] 