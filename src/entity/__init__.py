"""
Entity domain module.

This module contains all entity-related models and business logic.
Entities represent investors (individuals or companies) who invest in funds.
"""

from .models import Entity, InvestmentCompany, RiskFreeRate

__all__ = [
    'Entity',
    'InvestmentCompany', 
    'RiskFreeRate'
] 