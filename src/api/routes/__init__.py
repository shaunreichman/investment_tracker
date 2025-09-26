"""
API Routes Module.

This module provides the route blueprints for API operations,
including fund, company, health check, entity, banking, and tax routes.
"""

from src.api.routes.fund import fund_bp
from src.api.routes.company import company_bp
from src.api.routes.health_check import health_check_bp
from src.api.routes.entity import entity_bp
from src.api.routes.banking import banking_bp
from src.api.routes.rate import rate_bp

__all__ = [
    'fund_bp',
    'company_bp',
    'health_check_bp',
    'entity_bp',
    'banking_bp',
    'rate_bp',
]
