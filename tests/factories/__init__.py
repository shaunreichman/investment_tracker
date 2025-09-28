"""
Test Factories Package.

This package provides a centralized, organized approach to test data generation
that mirrors the backend model structure and follows enterprise best practices.

Architecture:
- Domain-separated factory modules
- Centralized imports and exports
- Dynamic session management
- Model consistency validation
- Automated factory discovery

Usage:
    from tests.factories import FundFactory, EntityFactory, set_session
    
    # Set up session
    set_session(db_session)
    
    # Create test data
    fund = FundFactory()
    entity = EntityFactory()
"""

# Import base classes and utilities
from .base import (
    SessionedFactory,
    set_session,
    get_session,
    validate_factory_model_consistency,
    validate_all_factories
)

# Import fund factories
from .fund_factories import (
    FundFactory,
    FundEventFactory,
    FundEventCashFlowFactory,
    FundTaxStatementFactory
)

# Import entity factories
from .entity_factories import EntityFactory

# Import banking factories
from .banking_factories import BankFactory, BankAccountFactory

# Import investment company factories
from .investment_company_factories import InvestmentCompanyFactory, ContactFactory

# Import rates factories
from .rates_factories import RiskFreeRateFactory

# Export all factories and utilities
__all__ = [
    # Base classes and utilities
    'SessionedFactory',
    'set_session',
    'get_session',
    'validate_factory_model_consistency',
    'validate_all_factories',
    
    # Fund factories
    'FundFactory',
    'FundEventFactory',
    'FundEventCashFlowFactory',
    'FundTaxStatementFactory',
    
    # Entity factories
    'EntityFactory',
    
    # Banking factories
    'BankFactory',
    'BankAccountFactory',
    
    # Investment company factories
    'InvestmentCompanyFactory',
    'ContactFactory',
    
    # Rates factories
    'RiskFreeRateFactory',
]
