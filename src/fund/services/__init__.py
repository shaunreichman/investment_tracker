"""
Fund services package.

This package contains business logic services extracted from the Fund model
to provide clean separation of concerns and improved testability.
"""

from .fund_calculation_service import FundCalculationService

__all__ = [
    'FundCalculationService',
]
