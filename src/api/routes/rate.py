"""
Rate API Routes.

This module provides enterprise-grade REST API endpoints for rate operations,
with standardized response formats, comprehensive error handling, and performance optimization.

All endpoints use middleware validation for input data.
All endpoints use the rate controller with DTO responses.
"""

from flask import Blueprint, jsonify, request
from src.api.controllers.rate_controller import RateController
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response
from src.api.middleware.validation import validate_request
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode
from src.shared.enums.shared_enums import Currency
from src.rates.enums.risk_free_rate_enums import RiskFreeRateType


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
@validate_request(
    field_types={
        'currency': 'string',
        'rate_type': 'string',
        'start_date': 'date',
        'end_date': 'date'
    },
    enum_fields={
        'currency': Currency,
        'rate_type': RiskFreeRateType
    },
    sanitize=True
)
def get_risk_free_rates():
    """
    Get risk free rates.

    Query Parameters (all optional):
        currency (str): Filter by currency
        rate_type (str): Filter by rate type
        start_date (date): Filter by start date
        end_date (date): Filter by end date

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
@validate_request(
    required_fields=['currency', 'date', 'rate'],
    field_types={
        'currency': 'string',
        'date': 'date',
        'rate': 'float',
        'rate_type': 'string',
        'source': 'string'
    },
    field_lengths={'date': {'min': 10, 'max': 10}},
    enum_fields={
        'currency': Currency,
        'rate_type': RiskFreeRateType
    },
    sanitize=True
)
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
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting risk free rate {risk_free_rate_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################################################
# FX RATE ENDPOINTS
###############################################################################

###############################################
# Get FX Rates
###############################################

@rate_bp.route('/api/fx-rates', methods=['GET'])
@validate_request(
    field_types={
        'from_currency': 'string',
        'to_currency': 'string',
        'start_date': 'date',
        'end_date': 'date'
    },
    enum_fields={
        'from_currency': Currency,
        'to_currency': Currency
    },
    sanitize=True
)
def get_fx_rates():
    """
    Get all FX rates with optional search filters.

    Query Parameters (all optional):
        from_currency (str): Filter by from currency
        to_currency (str): Filter by to currency

    Returns:
        Standardized response with FX rates data
    """
    try:
        dto = rate_controller.get_fx_rates()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting FX rates: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()
    
@rate_bp.route('/api/fx-rates/<int:fx_rate_id>', methods=['GET'])
def get_fx_rate_by_id(fx_rate_id):
    """
    Get an FX rate by its ID.

    Path Parameters:
        fx_rate_id (int): ID of the FX rate to retrieve
    """
    try:
        dto = rate_controller.get_fx_rate_by_id(fx_rate_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting FX rate {fx_rate_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create FX Rate
###############################################

@rate_bp.route('/api/fx-rates', methods=['POST'])
@validate_request(
    required_fields=['from_currency', 'to_currency', 'date', 'fx_rate'],
    field_types={
        'from_currency': 'string',
        'to_currency': 'string',
        'date': 'date',
        'fx_rate': 'float'
    },
    field_ranges={
        'fx_rate': {'min': 0, 'max': 9999999999}
    },
    enum_fields={
        'from_currency': Currency,
        'to_currency': Currency
    },
    sanitize=True
)
def create_fx_rate():
    """
    Create a new FX rate.

    Returns:
        Standardized response with FX rate data
    """
    try:
        dto = rate_controller.create_fx_rate()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating FX rate: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete FX Rate
###############################################

@rate_bp.route('/api/fx-rates/<int:fx_rate_id>', methods=['DELETE'])
def delete_fx_rate(fx_rate_id):
    """
    Delete an FX rate.

    Path Parameters:
        fx_rate_id (int): ID of the FX rate to delete
    """
    try:
        dto = rate_controller.delete_fx_rate(fx_rate_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting FX rate {fx_rate_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()