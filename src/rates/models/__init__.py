"""
Rates Models.

This module provides the rates-related model classes,
representing interest rates and risk-free rates in the system.
"""

from src.rates.models.risk_free_rate import RiskFreeRate
from src.rates.models.fx_rate import FxRate

__all__ = [
    'RiskFreeRate',
    'FxRate',
]