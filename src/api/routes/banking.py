"""
Banking API Routes.

This module provides enterprise-grade REST API endpoints for banking operations,
with standardized response formats, comprehensive error handling, and performance optimization.

All endpoints use the banking controller with DTO responses.
"""

from flask import Blueprint, jsonify, request
from src.api.controllers.banking_controller import BankingController
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response
from src.api.middleware.validation import (
    validate_bank_data, 
    validate_bank_account_data,
    validate_request
)
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode

# Create blueprint for enhanced banking routes
banking_bp = Blueprint('banking', __name__)

# Initialize banking controller
banking_controller = BankingController()


@banking_bp.route('/api/v2/banks/<int:bank_id>', methods=['GET'])
def get_bank(bank_id):
    """
    Get a bank by ID.
    
    Path Parameters:
        bank_id (int): ID of the bank to retrieve
    
    Returns:
        Standardized response with bank data
    """
    try:
        dto = banking_controller.get_bank(bank_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@banking_bp.route('/api/v2/banks', methods=['POST'])
@validate_bank_data
def create_bank():
    """
    Create a new bank.
    
    Request Body:
        name (str): Bank name (required)
        country (str): ISO 3166-1 alpha-2 country code (required)
        swift_bic (str): Optional SWIFT/BIC identifier
    
    Returns:
        Standardized response with created bank data
    """
    try:
        # Use validated data from middleware
        validated_data = request.validated_data
        dto = banking_controller.create_bank(validated_data)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@banking_bp.route('/api/v2/banks/<int:bank_id>', methods=['PUT'])
@validate_bank_data
def update_bank(bank_id):
    """
    Update a bank.
    
    Path Parameters:
        bank_id (int): ID of the bank to update
    
    Request Body:
        name (str): Bank name (optional)
        country (str): ISO 3166-1 alpha-2 country code (optional)
        swift_bic (str): Optional SWIFT/BIC identifier
    
    Returns:
        Standardized response with updated bank data
    """
    try:
        # Use validated data from middleware
        validated_data = request.validated_data
        dto = banking_controller.update_bank(bank_id, validated_data)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@banking_bp.route('/api/v2/banks/<int:bank_id>', methods=['DELETE'])
def delete_bank(bank_id):
    """
    Delete a bank.
    
    Path Parameters:
        bank_id (int): ID of the bank to delete
    
    Returns:
        Standardized response confirming deletion
    """
    try:
        dto = banking_controller.delete_bank(bank_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@banking_bp.route('/api/v2/bank-accounts', methods=['POST'])
@validate_bank_account_data
def create_bank_account():
    """
    Create a new bank account.
    
    Request Body:
        entity_id (int): Owner entity ID (required)
        bank_id (int): Linked bank ID (required)
        account_name (str): Human-readable account name (required)
        account_number (str): Account number (required)
        currency (str): ISO-4217 currency code (required)
        is_active (bool): Active status flag (default: true)
    
    Returns:
        Standardized response with created bank account data
    """
    try:
        # Use validated data from middleware
        validated_data = getattr(request, 'validated_data', request.get_json() or {})
        dto = banking_controller.create_bank_account(validated_data)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@banking_bp.route('/api/v2/bank-accounts/<int:account_id>', methods=['PUT'])
@validate_bank_account_data
def update_bank_account(account_id):
    """
    Update a bank account.
    
    Path Parameters:
        account_id (int): ID of the account to update
    
    Request Body:
        entity_id (int): Owner entity ID (optional)
        bank_id (int): Linked bank ID (optional)
        account_name (str): Human-readable account name (optional)
        account_number (str): Account number (optional)
        currency (str): ISO-4217 currency code (optional)
        is_active (bool): Active status flag (optional)
    
    Returns:
        Standardized response with updated bank account data
    """
    try:
        # Use validated data from middleware
        validated_data = getattr(request, 'validated_data', request.get_json() or {})
        dto = banking_controller.update_bank_account(account_id, validated_data)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@banking_bp.route('/api/v2/bank-accounts/<int:account_id>', methods=['DELETE'])
def delete_bank_account(account_id):
    """
    Delete a bank account.
    
    Path Parameters:
        account_id (int): ID of the account to delete
    
    Returns:
        Standardized response confirming deletion
    """
    try:
        dto = banking_controller.delete_bank_account(account_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()