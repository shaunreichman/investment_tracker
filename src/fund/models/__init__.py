"""
Fund Models Package.

This package contains the new, clean fund models with professional architecture.
Models handle only data persistence and basic validation, with business logic
delegated to services through the orchestrator.
"""

from .domain_event import DomainEvent
from .fund_event_cash_flow import FundEventCashFlow
from .fund_event import FundEvent
from .fund import Fund

__all__ = [
    'DomainEvent',
    'FundEventCashFlow', 
    'FundEvent',
    'Fund',
]

# Version information
__version__ = '2.0.0'

# Architecture information
__architecture__ = 'service-oriented'
__pattern__ = 'event-driven'
__responsibility__ = 'data-persistence-only'
