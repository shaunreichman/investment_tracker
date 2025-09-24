"""
Tax API Routes.

This module contains all tax-related API endpoints including
tax statement management for funds.

All endpoints use middleware validation for input data.
"""

from flask import Blueprint, jsonify
from src.api.controllers.tax_controller import TaxController

from src.api.middleware.validation import validate_tax_statement_data
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response

# Create blueprint for tax routes
tax_bp = Blueprint('tax', __name__)

# Initialize controller
tax_controller = TaxController()

################################################################################
# TAX STATEMENT ENDPOINTS
################################################################################

###############################################
# Get tax statement
###############################################

@tax_bp.route('/api/funds/<int:fund_id>/tax-statements', methods=['GET'])
def get_tax_statement_for_fund(fund_id):
    """
    Get a tax statement for a fund
    """
    try:
        dto = tax_controller.get_tax_statement_for_fund(fund_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting tax statement for fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@tax_bp.route('/api/tax-statements/<int:tax_statement_id>', methods=['GET'])
def get_tax_statement(tax_statement_id):
    """
    Get a tax statement by ID
    """
    try:
        dto = tax_controller.get_tax_statement(tax_statement_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting tax statement {tax_statement_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create tax statement
###############################################

@tax_bp.route('/api/funds/<int:fund_id>/tax-statements', methods=['POST'])
@validate_tax_statement_data
def create_tax_statement(fund_id):
    """
    Create a new tax statement for a fund
    """
    try:
        dto = tax_controller.create_tax_statement(fund_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating tax statement for fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete tax statement
###############################################

@tax_bp.route('/api/tax-statements/<int:tax_statement_id>', methods=['DELETE'])
def delete_tax_statement(tax_statement_id):
    """
    Delete a tax statement by ID
    """
    try:
        dto = tax_controller.delete_tax_statement(tax_statement_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting tax statement {tax_statement_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Get fund financial years
###############################################

@tax_bp.route('/api/funds/<int:fund_id>/financial-years', methods=['GET'])
def get_fund_financial_years(fund_id):
    """
    Get all financial years from fund start date to current date
    """
    try:
        dto = tax_controller.get_fund_financial_years(fund_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting financial years for fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()
