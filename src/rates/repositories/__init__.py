"""
Rates Repositories.

This module provides the data access layer abstraction for the rates system.
Repositories handle all database operations and provide a clean interface
for business logic components to interact with data.
"""

from src.rates.repositories.risk_free_rate_repository import RiskFreeRateRepository

__all__ = [
    'RiskFreeRateRepository',
]