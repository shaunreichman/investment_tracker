"""
Fund Repositories Module.

This module provides the data access layer abstraction for the fund system.
Repositories handle all database operations and provide a clean interface
for business logic components to interact with data.
"""

from src.fund.repositories.fund_repository import FundRepository
from src.fund.repositories.fund_event_repository import FundEventRepository
from src.fund.repositories.capital_event_repository import CapitalEventRepository
from src.fund.repositories.unit_event_repository import UnitEventRepository
from src.fund.repositories.tax_event_repository import TaxEventRepository
from src.fund.repositories.distribution_event_repository import DistributionEventRepository
from src.fund.repositories.tax_statement_repository import TaxStatementRepository
from src.fund.repositories.domain_event_repository import DomainEventRepository
from src.fund.repositories.fund_tax_statement_repository import FundTaxStatementRepository

__all__ = [
    'FundRepository',
    'FundEventRepository',
    'CapitalEventRepository',
    'UnitEventRepository',
    'TaxEventRepository',
    'DistributionEventRepository',
    'TaxStatementRepository',
    'DomainEventRepository',
    'FundTaxStatementRepository',
]
