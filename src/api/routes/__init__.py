"""
API Routes Module.

This module provides the route blueprints for API operations,
including fund, company, health check, entity, banking, and tax routes.
"""

from src.api.routes.fund_route import fund_bp
from src.api.routes.company_route import company_bp
from src.api.routes.health_check_route import health_check_bp
from src.api.routes.entity_route import entity_bp
from src.api.routes.banking_route import banking_bp
from src.api.routes.rate_route import rate_bp

__all__ = [
    'fund_bp',
    'company_bp',
    'health_check_bp',
    'entity_bp',
    'banking_bp',
    'rate_bp',
]
