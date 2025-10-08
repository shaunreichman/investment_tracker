"""
Banking API Routes.

This module provides enterprise-grade REST API endpoints for banking operations,
with standardized response formats, comprehensive error handling, and performance optimization.

All endpoints use middleware validation for input data.
All endpoints use the banking controller with DTO responses.
"""

from flask import Blueprint, jsonify
from src.api.controllers.banking_controller import BankingController
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response
from src.api.middleware.validation.base_validation import validate_request
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode
from src.shared.enums.shared_enums import Country, Currency, SortOrder
from src.banking.enums.bank_enums import BankType, SortFieldBank
from src.banking.enums.bank_account_enums import BankAccountType, BankAccountStatus, SortFieldBankAccount
from src.banking.enums.bank_account_balance_enums import SortFieldBankAccountBalance


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
        'names': 'string_array',
        'country': 'string',
        'countries': 'string_array',
        'bank_type': 'string',
        'bank_types': 'string_array',
        'sort_by': 'string',
        'sort_order': 'string',
        'include_bank_accounts': 'bool',
        'include_bank_account_balances': 'bool'
    },
    field_lengths={
        'name': {'max': 255}
    },
    enum_fields={
        'country': Country,
        'bank_type': BankType,
        'sort_by': SortFieldBank,
        'sort_order': SortOrder
    },
    array_element_lengths={
        'names': {'max': 255}
    },
    array_element_enum_fields={
        'countries': Country,
        'bank_types': BankType
    },
    mutually_exclusive_groups=[
        ['name', 'names'],
        ['country', 'countries'],
        ['bank_type', 'bank_types']
    ],
    sanitize=True
)
def get_banks():
    """
    Get all banks with optional search filters and bank accounts.
    
    Query Parameters (all optional):
        name (str): Filter by bank name
        names (str): Filter by bank names
        country (str): Filter by country code (US, UK, etc.)
        countries (str): Filter by country codes (US, UK, etc.)
        bank_type (str): Filter by bank type (COMMERCIAL, INVESTMENT, etc.)
        bank_types (str): Filter by bank types (COMMERCIAL, INVESTMENT, etc.)
        sort_by (str): Sort by (NAME, COUNTRY, CURRENCY, TYPE, STATUS, CREATED_AT, UPDATED_AT)
        sort_order (str): Sort order (ASC, DESC)
        include_bank_accounts (bool): Whether to include bank accounts (default: false)
        include_bank_account_balances (bool): Whether to include bank account balances (default: false)
    
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
    field_types={
        'include_bank_accounts': 'bool',
        'include_bank_account_balances': 'bool'
    },
    sanitize=True
)
def get_bank_by_id(bank_id):
    """
    Get a bank by ID with optional bank accounts.

    Path Parameters:
        bank_id (int): ID of the bank to retrieve
        
    Query Parameters (all optional):
        include_bank_accounts (bool): Whether to include bank accounts (optional)
        include_bank_account_balances (bool): Whether to include bank account balances (optional)
    
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
        'bank_ids': 'int_array',
        'entity_id': 'int',
        'entity_ids': 'int_array',
        'account_name': 'string',
        'account_names': 'string_array',
        'currency': 'string',
        'currencies': 'string_array',
        'status': 'string',
        'statuses': 'string_array',
        'account_type': 'string',
        'account_types': 'string_array',
        'sort_by': 'string',
        'sort_order': 'string',
        'include_bank_account_balances': 'bool'
    },
    field_ranges={
        'bank_id': {'min': 1},
        'entity_id': {'min': 1}
    },
    field_lengths={
        'account_name': {'max': 255}
    },
    enum_fields={
        'currency': Currency,
        'status': BankAccountStatus,
        'account_type': BankAccountType,
        'sort_by': SortFieldBankAccount,
        'sort_order': SortOrder
    },
    array_element_ranges={
        'bank_ids': {'min': 1},
        'entity_ids': {'min': 1}
    },
    array_element_lengths={
        'account_names': {'max': 255}
    },
    array_element_enum_fields={
        'currencies': Currency,
        'statuses': BankAccountStatus,
        'account_types': BankAccountType
    },
    mutually_exclusive_groups=[
        ['bank_id', 'bank_ids'],
        ['entity_id', 'entity_ids'],
        ['currency', 'currencies'],
        ['status', 'statuses'],
        ['account_type', 'account_types']
    ],
    sanitize=True
)
def get_bank_accounts():
    """
    Get all bank accounts with optional search filters.
    
    Query Parameters (all optional):
        bank_id (int): Filter by bank ID
        bank_ids (int): Filter by bank IDs
        entity_id (int): Filter by entity ID
        entity_ids (int): Filter by entity IDs
        account_name (str): Filter by account name
        account_names (str): Filter by account names
        currency (str): Filter by currency code
        currencies (str): Filter by currency codes
        status (str): Filter by status
        statuses (str): Filter by statuses
        account_type (str): Filter by account type
        account_types (str): Filter by account types
        sort_by (str): Sort by (NAME, ACCOUNT_NUMBER, CURRENCY, STATUS, CREATED_AT, UPDATED_AT)
        sort_order (str): Sort order (ASC, DESC)
        include_bank_account_balances (bool): Whether to include bank account balances (default: false)
    
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
@validate_request(
    field_types={
        'include_bank_account_balances': 'bool'
    },
    sanitize=True
)
def get_bank_accounts_by_bank_id(bank_id):
    """
    Get all bank accounts for a specific bank.
    
    Path Parameters:
        bank_id (int): ID of the bank to get bank accounts for
    
    Query Parameters (all optional):
        include_bank_account_balances (bool): Whether to include bank account balances (optional)

    Returns:
        Standardized response with bank accounts data
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
@validate_request(
    field_types={
        'include_bank_account_balances': 'bool'
    },
    sanitize=True
)
def get_bank_account_by_id(bank_id, bank_account_id):
    """
    Get a bank account by ID.
    
    Path Parameters:
        bank_id (int): ID of the bank to get bank account for (not used)
        bank_account_id (int): ID of the bank account to retrieve

    Query Parameters (all optional):
        include_bank_account_balances (bool): Whether to include bank account balances (optional)
    
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
    required_fields=['entity_id', 'account_name', 'account_number', 'currency'],
    field_types={
        'entity_id': 'int',
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
    },
    enum_fields={
        'currency': Currency,
        'account_type': BankAccountType
    },
    sanitize=True
)
def create_bank_account(bank_id):
    """
    Create a new bank account.
    
    Request Body:
        entity_id (int): Owner entity ID (required)
        account_name (str): Human-readable account name (required)
        account_number (str): Account number (required)
        currency (str): ISO-4217 currency code (required)
        account_type (str): Account type (optional)
    
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
        bank_id (int): ID of the bank to delete bank account for (not used)
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


###############################################################################
# BANK ACCOUNT BALANCE ENDPOINTS
###############################################################################

###############################################
# Get bank account balances
###############################################

@banking_bp.route('/api/bank-account-balances', methods=['GET'])
@validate_request(
    field_types={
        'bank_id': 'int',
        'bank_ids': 'int_array',
        'bank_account_id': 'int',
        'bank_account_ids': 'int_array',
        'currency': 'string',
        'currencies': 'string_array',
        'start_date': 'date',
        'end_date': 'date',
        'sort_by': 'string',
        'sort_order': 'string'
    },
    field_ranges={
        'bank_id': {'min': 1},
        'bank_account_id': {'min': 1}
    },
    enum_fields={
        'currency': Currency,
        'sort_by': SortFieldBankAccountBalance,
        'sort_order': SortOrder
    },
    array_element_ranges={
        'bank_ids': {'min': 1},
        'bank_account_ids': {'min': 1}
    },
    array_element_enum_fields={
        'currencies': Currency
    },
    mutually_exclusive_groups=[
        ['bank_id', 'bank_ids'],
        ['bank_account_id', 'bank_account_ids'],
        ['currency', 'currencies']
    ],
    sanitize=True
)
def get_bank_account_balances():
    """
    Get all bank account balances.

    Query Parameters (all optional):
        bank_id (int): Filter by bank ID
        bank_ids (int): Filter by bank IDs
        bank_account_id (int): Filter by bank account ID
        bank_account_ids (int): Filter by bank account IDs
        currency (str): Filter by currency code
        currencies (str): Filter by currency codes
        start_date (str): Filter by start date
        end_date (str): Filter by end date
        sort_by (str): Sort by (DATE, BALANCE)
        sort_order (str): Sort order (ASC, DESC)

    Returns:
        Standardized response with bank account balances data
    """
    try:
        dto = banking_controller.get_bank_account_balances()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting bank account balances: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@banking_bp.route('/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>/bank-account-balances', methods=['GET'])
def get_bank_account_balances_by_bank_id_and_bank_account_id(bank_id, bank_account_id):
    """
    Get all bank account balances for a specific bank account.
    
    Path Parameters:
        bank_id (int): ID of the bank to get bank account balances for
        bank_account_id (int): ID of the bank account to get bank account balances for

    Returns:
        Standardized response with bank account balances data
    """
    try:
        dto = banking_controller.get_bank_account_balances(bank_id, bank_account_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting bank account balances for bank account {bank_account_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@banking_bp.route('/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>/bank-account-balances/<int:bank_account_balance_id>', methods=['GET'])
def get_bank_account_balance_by_id(bank_id, bank_account_id, bank_account_balance_id):
    """
    Get a bank account balance by ID.
    
    Path Parameters:
        bank_id (int): ID of the bank to get bank account balances for (not used)
        bank_account_id (int): ID of the bank account to get bank account balances for (not used)
        bank_account_balance_id (int): ID of the bank account balance to retrieve

    Returns:
        Standardized response with bank account balance data
    """
    try:
        dto = banking_controller.get_bank_account_balance_by_id(bank_account_balance_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting bank account balance {bank_account_balance_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create bank account balance
###############################################

@banking_bp.route('/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>/bank-account-balances', methods=['POST'])
@validate_request(
    required_fields=['currency', 'balance_statement', 'date'],
    field_types={
        'currency': 'string',
        'balance_statement': 'float',
        'date': 'date'
    },
    enum_fields={
        'currency': Currency
    }
)
def create_bank_account_balance(bank_id, bank_account_id):
    """
    Create a new bank account balance.

    Path Parameters:
        bank_id (int): ID of the bank to create bank account balance for
        bank_account_id (int): ID of the bank account to create bank account balance for

    Request Body:
        currency (str): ISO-4217 currency code (required)
        balance_statement (float): Balance of the bank account (required)
        date (str): Date of the bank account balance (required)

    Returns:
        Standardized response with created bank account balance data
    """
    try:
        dto = banking_controller.create_bank_account_balance(bank_account_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating bank account balance: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete bank account balance
###############################################

@banking_bp.route('/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>/bank-account-balances/<int:bank_account_balance_id>', methods=['DELETE'])
def delete_bank_account_balance(bank_id, bank_account_id, bank_account_balance_id):
    """
    Delete a bank account balance.
    
    Path Parameters:
        bank_id (int): ID of the bank to delete bank account balance for (not used)
        bank_account_id (int): ID of the bank account to delete bank account balance for (not used)
        bank_account_balance_id (int): ID of the bank account balance to delete

    Returns:
        Standardized response confirming deletion
    """
    try:
        dto = banking_controller.delete_bank_account_balance(bank_account_balance_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting bank account balance {bank_account_balance_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()