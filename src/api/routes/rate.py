"""
Rate API Routes.

This module provides enterprise-grade REST API endpoints for rate operations,
with standardized response formats, comprehensive error handling, and performance optimization.

All endpoints use the rate controller with DTO responses.
"""

from flask import Blueprint, jsonify, request
from src.api.controllers.rate_controller import RateController
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response
from src.api.middleware.validation import validate_request
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode


# Create blueprint for enhanced rate routes
rate_bp = Blueprint('rate', __name__)

# Initialize rate controller
rate_controller = RateController()


###############################################################################
# RATE ENDPOINTS
###############################################################################

###############################################
# Get Risk Free Rates
###############################################

@rate_bp.route('/api/risk-free-rates', methods=['GET'])
def get_risk_free_rates():
    """
    Get risk free rates.

    Returns:
        Standardized response with risk free rates data
    """
    try:
        dto = rate_controller.get_risk_free_rates()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting risk free rates: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@rate_bp.route('/api/risk-free-rates/<int:risk_free_rate_id>', methods=['GET'])
def get_risk_free_rate_by_id(risk_free_rate_id):
    """
    Get a risk free rate by its ID.

    Path Parameters:
        risk_free_rate_id (int): ID of the risk free rate to retrieve
    
    Returns:
        Standardized response with risk free rate data
    """
    try:
        dto = rate_controller.get_risk_free_rate_by_id(risk_free_rate_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting risk free rate {risk_free_rate_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create Risk Free Rate
###############################################

@rate_bp.route('/api/risk-free-rates', methods=['POST'])
def create_risk_free_rate():
    """
    Create a risk free rate.

    Returns:
        Standardized response with risk free rate data
    """
    try:
        dto = rate_controller.create_risk_free_rate()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating risk free rate: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete Risk Free Rate
###############################################

@rate_bp.route('/api/risk-free-rates/<int:risk_free_rate_id>', methods=['DELETE'])
def delete_risk_free_rate(risk_free_rate_id):
    """
    Delete a risk free rate.

    Path Parameters:
        risk_free_rate_id (int): ID of the risk free rate to delete
    
    Returns:
        Standardized response with risk free rate data
    """
    try:
        dto = rate_controller.delete_risk_free_rate(risk_free_rate_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting risk free rate {risk_free_rate_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()