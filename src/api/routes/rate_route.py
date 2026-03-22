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
from src.rates.enums.risk_free_rate_enums import RiskFreeRateType, SortFieldRiskFreeRate
from src.rates.enums.fx_rate_enums import SortFieldFxRate
from src.shared.enums.shared_enums import SortOrder


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
        'currencies': 'string_array',
        'rate_type': 'string',
        'rate_types': 'string_array',
        'start_date': 'date',
        'end_date': 'date',
        'sort_by': 'string',
        'sort_order': 'string'
    },
    enum_fields={
        'currency': Currency,
        'rate_type': RiskFreeRateType,
        'sort_by': SortFieldRiskFreeRate,
        'sort_order': SortOrder
    },
    array_element_enum_fields={
        'currencies': Currency,
        'rate_types': RiskFreeRateType
    },
    mutually_exclusive_groups=[
        ['currency', 'currencies'],
        ['rate_type', 'rate_types']
    ],
    sanitize=True
)
def get_risk_free_rates():
    """
    Get risk free rates.

    Query Parameters (all optional):
        currency (str): Filter by single currency (mutually exclusive with currencies)
        currencies (str): Filter by multiple currencies (mutually exclusive with currency)
        rate_type (str): Filter by single rate type (mutually exclusive with rate_types)
        rate_types (str): Filter by multiple rate types (mutually exclusive with rate_type)
        start_date (date): Filter by start date
        end_date (date): Filter by end date
        sort_by (str): Sort by (DATE, CURRENCY)
        sort_order (str): Sort order (ASC, DESC)

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
    field_ranges={
        'rate': {'min': -100.0, 'max': 10000.0}
    },
    enum_fields={
        'currency': Currency,
        'rate_type': RiskFreeRateType
    },
    sanitize=True
)
def create_risk_free_rate():
    """
    Create a risk free rate.

    Request Body:
        currency (str): ISO-4217 currency code (required)
        date (date): Date of the risk free rate (required)
        rate (float): Risk-free rate as percentage (required)
        rate_type (str): Type of rate (optional)
        source (str): Source of the rate data

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
        'end_date': 'date',
        'sort_by': 'string',
        'sort_order': 'string'
    },
    enum_fields={
        'from_currency': Currency,
        'to_currency': Currency,
        'sort_by': SortFieldFxRate,
        'sort_order': SortOrder
    },
    sanitize=True
)
def get_fx_rates():
    """
    Get all FX rates with optional search filters.

    Query Parameters (all optional):
        from_currency (str): Filter by from currency
        to_currency (str): Filter by to currency
        start_date (date): Filter by start date
        end_date (date): Filter by end date
        sort_by (str): Sort by (DATE, FROM_CURRENCY, TO_CURRENCY)
        sort_order (str): Sort order (ASC, DESC)

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

    Returns:
        Standardized response with FX rate data
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
        'fx_rate': {'max': 9999999999}
    },
    enum_fields={
        'from_currency': Currency,
        'to_currency': Currency
    },
    positive_numbers=['fx_rate'],
    sanitize=True
)
def create_fx_rate():
    """
    Create a new FX rate.

    Request Body:
        from_currency (str): ISO-4217 currency code (required)
        to_currency (str): ISO-4217 currency code (required)
        date (date): Date of the FX rate (required)
        fx_rate (float): FX rate (required)

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

    Returns:
        Standardized response with FX rate data
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