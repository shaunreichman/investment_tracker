"""
Investment Tracker Package

A SQLAlchemy-based investment tracking system for managing investment companies, funds, and fund events.
"""

from .models import (
    InvestmentCompany, 
    Fund, 
    FundEvent, 
    Base, 
    EventType
)
from .database import (
    init_database,
    get_database_session,
    get_global_session,
    close_global_session,
    create_database_engine
)

__version__ = "1.0.0"
__author__ = "Investment Tracker"

__all__ = [
    'InvestmentCompany',
    'Fund',
    'FundEvent', 
    'Base',
    'EventType',
    'init_database',
    'get_database_session',
    'get_global_session',
    'close_global_session',
    'create_database_engine'
] 