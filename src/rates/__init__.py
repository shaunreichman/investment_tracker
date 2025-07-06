"""
Rates domain module.

This module contains rates models and related functionality.
"""

from .models import RiskFreeRate
from .calculations import get_risk_free_rate_for_date

__all__ = [
    'RiskFreeRate',
    'get_risk_free_rate_for_date',
] 