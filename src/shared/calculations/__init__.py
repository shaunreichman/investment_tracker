"""
Shared calculation utilities.

This package contains pure calculation logic that can be reused
across different domains (fund, company, etc.).
"""

from src.shared.calculations.irr_calculator import IRRCalculator

__all__ = [
    'IRRCalculator',
]