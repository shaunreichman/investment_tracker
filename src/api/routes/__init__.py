"""
API Routes Module.

This module provides the route blueprints for API operations,
including fund, company, dashboard, entity, banking, and tax routes.
"""

from src.api.routes.fund import fund
from src.api.routes.company import company
from src.api.routes.dashboard import dashboard
from src.api.routes.entity import entity
from src.api.routes.banking import banking
from src.api.routes.rate import rate

__all__ = [
    'fund',
    'company',
    'dashboard',
    'entity',
    'banking',
    'rate',
]
