"""
Health Check API Routes.

This module provides health check endpoints for production monitoring,
including system health, banking health, and performance metrics.
"""

from flask import Blueprint, jsonify, request
from src.api.database import get_db_session
from src.banking.services.banking_health_service import get_banking_health_service
import logging

# Create blueprint for health check routes
health_bp = Blueprint('health', __name__)

# Initialize health services
banking_health_service = get_banking_health_service()

logger = logging.getLogger(__name__)


@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Simple health status for load balancers and basic monitoring
    """
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": "2025-01-16T00:00:00Z",
            "service": "investment_tracker",
            "version": "1.0.0"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
