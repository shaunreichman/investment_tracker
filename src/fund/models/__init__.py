"""
Fund Models Package.

This package contains the new, clean fund models with professional architecture.
Models handle only data persistence and basic validation, with business logic
delegated to services through the orchestrator.
"""

# Import enums first to ensure they're registered with SQLAlchemy
from src.fund.enums import (
    FundType,
    FundStatus,
    EventType,
    DistributionType,
    CashFlowDirection,
    TaxPaymentType,
    GroupType
)

# Import fund models
from src.fund.models.domain_event import DomainEvent, DomainFundEvent, FundFieldChange
from src.fund.models.fund_event_cash_flow import FundEventCashFlow
from src.fund.models.fund_event import FundEvent
from src.fund.models.fund import Fund

__all__ = [
    'DomainEvent',
    'DomainFundEvent',
    'FundFieldChange',
    'FundEventCashFlow', 
    'FundEvent',
    'Fund',
    # Also export enums for convenience
    'FundType',
    'FundStatus',
    'EventType',
    'DistributionType',
    'CashFlowDirection',
    'TaxPaymentType',
    'GroupType'
]

# Version information
__version__ = '2.0.0'

# Architecture information
__architecture__ = 'service-oriented'
__pattern__ = 'event-driven'
__responsibility__ = 'data-persistence-only'
