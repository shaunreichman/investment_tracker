"""
Rates domain module.

This module contains all rates-related models and business logic.
Rates include risk-free rates and other financial rates used in calculations.
"""

from .models import RiskFreeRate

__all__ = [
    'RiskFreeRate',
] 