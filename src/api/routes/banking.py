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


###############################################################################
# BANK ENDPOINTS
###############################################################################

###############################################
# Get bank
###############################################

@banking_bp.route('/api/banks', methods=['GET'])
def get_banks():
    """
    Get all banks.
    
    Returns:
        Standardized response with banks data
    """
    try:
        dto = banking_controller.get_banks()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting banks: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@banking_bp.route('/api/banks/<int:bank_id>', methods=['GET'])
def get_bank(bank_id):
    """
    Get a bank by ID.
    
    Path Parameters:
        bank_id (int): ID of the bank to retrieve
    
    Returns:
        Standardized response with bank data
    """
    try:
        dto = banking_controller.get_bank_by_id(bank_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting bank {bank_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create bank
###############################################

@banking_bp.route('/api/banks', methods=['POST'])
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
        dto = banking_controller.create_bank()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating bank: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete bank
###############################################

@banking_bp.route('/api/banks/<int:bank_id>', methods=['DELETE'])
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
            message=f"Unexpected error deleting bank {bank_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################################################
# BANK ACCOUNT ENDPOINTS
###############################################################################

###############################################
# Get bank accounts
###############################################

@banking_bp.route('/api/bank-accounts', methods=['GET'])
def get_bank_accounts(bank_id):
    """
    Get all bank accounts.
    
    Path Parameters:
        bank_id (int): ID of the bank to get bank accounts for
    
    Returns:
        Standardized response with bank accounts data
    """
    try:
        dto = banking_controller.get_bank_accounts(bank_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting bank accounts {bank_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@banking_bp.route('/api/bank-accounts/<int:bank_account_id>', methods=['GET'])
def get_bank_account_by_id(bank_account_id):
    """
    Get a bank account by ID.
    
    Path Parameters:
        bank_account_id (int): ID of the bank account to retrieve
    
    Returns:
        Standardized response with bank account data
    """
    try:
        dto = banking_controller.get_bank_account_by_id(bank_account_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting bank account {bank_account_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create bank account
###############################################

@banking_bp.route('/api/bank-accounts', methods=['POST'])
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
        dto = banking_controller.create_bank_account()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating bank account: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete bank account
###############################################

@banking_bp.route('/api/bank-accounts/<int:account_id>', methods=['DELETE'])
def delete_bank_account(bank_account_id):
    """
    Delete a bank account.
    
    Path Parameters:
        bank_account_id (int): ID of the bank account to delete
    
    Returns:
        Standardized response confirming deletion
    """
    try:
        dto = banking_controller.delete_bank_account(bank_account_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting bank account {bank_account_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()