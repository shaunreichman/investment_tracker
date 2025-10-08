"""
Health Check API Routes.

This module contains all health-check related API endpoints including
health check.
"""

from flask import Blueprint, jsonify
from src.api.controllers import HealthCheckController
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode

# Create blueprint for health check routes
health_check_bp = Blueprint('health_check', __name__)

# Initialize controller
health_check_controller = HealthCheckController()


@health_check_bp.route('/api/health-check', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Standardized response with API status
    """
    try:
        return health_check_controller.health_check()
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error in health check: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()
