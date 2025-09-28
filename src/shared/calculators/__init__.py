"""
Shared calculators utilities.

This package contains pure calculation logic that can be reused
across different domains (fund, company, etc.).
"""

from src.shared.calculators.irr_calculator import IRRCalculator
from src.shared.calculators.duration_months_calculator import DurationMonthsCalculator

__all__ = [
    'IRRCalculator',
    'DurationMonthsCalculator',
]