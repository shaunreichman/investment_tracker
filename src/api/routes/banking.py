"""
Banking API Routes.

This module provides enterprise-grade REST API endpoints for banking operations,
with standardized response formats, comprehensive error handling, and performance optimization.

All endpoints use the banking controller with DTO responses.
"""

from flask import Blueprint, jsonify
from src.api.controllers.banking_controller import BankingController
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response
from src.api.middleware.validation.base_validation import validate_request
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode
from src.shared.enums.shared_enums import Country, Currency
from src.banking.enums.bank_enums import BankType
from src.banking.enums.bank_account_enums import BankAccountType


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
@validate_request(
    field_types={
        'name': 'string',
        'country': 'string',
        'bank_type': 'string',
        'include_bank_accounts': 'bool'
    },
    field_lengths={'name': {'max': 255}},
    enum_fields={
        'country': Country,
        'bank_type': BankType
    },
    sanitize=True
)
def get_banks():
    """
    Get all banks with optional search filters and bank accounts.
    
    Query Parameters (all optional):
        name (str): Filter by bank name
        country (str): Filter by country code (US, UK, etc.)
        bank_type (str): Filter by bank type (COMMERCIAL, INVESTMENT, etc.)
        include_bank_accounts (bool): Whether to include bank accounts (default: false)
    
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
@validate_request(
    field_types={'include_bank_accounts': 'bool'},
    sanitize=True
)
def get_bank(bank_id):
    """
    Get a bank by ID with optional bank accounts.

    Path Parameters:
        bank_id (int): ID of the bank to retrieve
        
    Query Parameters (all optional):
        include_bank_accounts (bool): Whether to include bank accounts (optional)
    
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
@validate_request(
    required_fields=['name', 'country'],
    field_types={
        'name': 'string',
        'country': 'string',
        'bank_type': 'string',
        'swift_bic': 'string'
    },
    field_lengths={
        'name': {'min': 2, 'max': 255},
        'swift_bic': {'max': 11}
    },
    enum_fields={
        'country': Country,
        'bank_type': BankType
    },
    sanitize=True
)
def create_bank():
    """
    Create a new bank.
    
    Request Body:
        name (str): Bank name (required)
        country (str): ISO 3166-1 alpha-2 country code (required)
        swift_bic (str): Optional SWIFT/BIC identifier
        bank_type (str): Optional bank type
    
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
@validate_request(
    field_types={
        'bank_id': 'int',
        'account_name': 'string',
        'currency': 'string'
    },
    field_ranges={
        'bank_id': {'min': 1}
    },
    field_lengths={'account_name': {'max': 255}},
    enum_fields={'currency': Currency},
    sanitize=True
)
def get_bank_accounts():
    """
    Get all bank accounts with optional search filters.
    
    Query Parameters (all optional):
        bank_id (int): Filter by bank ID
        account_name (str): Filter by account name
        currency (str): Filter by currency code
    
    Returns:
        Standardized response with bank accounts data
    """
    try:
        dto = banking_controller.get_bank_accounts()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting bank accounts: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@banking_bp.route('/api/banks/<int:bank_id>/bank-accounts', methods=['GET'])
def get_bank_accounts_by_bank_id(bank_id):
    """
    Get all bank accounts for a specific bank.
    
    Path Parameters:
        bank_id (int): ID of the bank to get bank accounts for
    """
    try:
        dto = banking_controller.get_bank_accounts(bank_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting bank accounts for bank {bank_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@banking_bp.route('/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>', methods=['GET'])
def get_bank_account_by_id(bank_id, bank_account_id):
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

@banking_bp.route('/api/banks/<int:bank_id>/bank-accounts', methods=['POST'])
@validate_request(
    required_fields=['entity_id', 'bank_id', 'account_name', 'account_number', 'currency'],
    field_types={
        'entity_id': 'int',
        'bank_id': 'int',
        'account_name': 'string',
        'account_number': 'string',
        'currency': 'string',
        'account_type': 'string'
    },
    field_lengths={
        'account_name': {'min': 2, 'max': 255},
        'account_number': {'min': 1, 'max': 50},
        'account_type': {'max': 255}
    },
    field_ranges={
        'entity_id': {'min': 1},
        'bank_id': {'min': 1}
    },
    enum_fields={
        'currency': Country,
        'account_type': BankAccountType
    },
    sanitize=True
)
def create_bank_account(bank_id):
    """
    Create a new bank account.
    
    Request Body:
        entity_id (int): Owner entity ID (required)
        bank_id (int): Linked bank ID (required)
        account_name (str): Human-readable account name (required)
        account_number (str): Account number (required)
        currency (str): ISO-4217 currency code (required)
        is_active (bool): Active status flag (optional, default: true)
    
    Returns:
        Standardized response with created bank account data
    """
    try:
        dto = banking_controller.create_bank_account(bank_id)
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

@banking_bp.route('/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>', methods=['DELETE'])
def delete_bank_account(bank_id, bank_account_id):
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