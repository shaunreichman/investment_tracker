"""
Investment company domain module.

This module contains investment company models and related functionality.
"""

from .models import InvestmentCompany
from .calculations import calculate_total_funds_under_management, calculate_total_commitments

__all__ = [
    'InvestmentCompany',
    'calculate_total_funds_under_management',
    'calculate_total_commitments',
] 