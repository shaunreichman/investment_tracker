"""
Health Check API Routes.

This module contains all health-check related API endpoints including
health check.
"""

from flask import Blueprint
from src.api.controllers import HealthCheckController

# Create blueprint for health check routes
health_check_bp = Blueprint('health_check', __name__)

# Initialize controller
health_check_controller = HealthCheckController()


@health_check_bp.route('/api/health-check', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return health_check_controller.health_check()
