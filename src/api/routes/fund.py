"""
Fund API Routes.

This module contains all fund-related API endpoints including
fund management, fund events, tax statements, and cash flows.

All endpoints use middleware validation for input data.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from src.fund.models import FundEvent, FundEventCashFlow
from src.tax.models import TaxStatement
from src.fund.repositories import FundRepository
from src.api.middleware.validation import validate_fund_data, validate_fund_event_data, validate_cash_flow_data
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response
from src.api.controllers.fund_controller import FundController
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode


# Create blueprint for fund routes
fund_bp = Blueprint('fund', __name__)

# Initialize fund controller (single instance for all routes)
fund_controller = FundController()


###############################################################
# FUND ENDPOINTS
###############################################################

###############################################
# Get fund
###############################################


@fund_bp.route('/api/funds', methods=['GET'])
def get_funds():
    """
    Get all funds.

    Query Parameters:
        include_events (bool): Include fund events in response (default: false)
        include_cash_flows (bool): Include cash flow details (default: false)
        include_tax_statements (bool): Include tax statement data (default: false)
    """
    try:
        # Parse query parameters for controlling response detail level
        include_events = request.args.get('include_events', 'false').lower() == 'true'
        include_cash_flows = request.args.get('include_cash_flows', 'false').lower() == 'true'
        include_tax_statements = request.args.get('include_tax_statements', 'false').lower() == 'true'

        dto = fund_controller.get_funds(
            include_events=include_events,
            include_cash_flows=include_cash_flows,
            include_tax_statements=include_tax_statements
        )

        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting funds: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@fund_bp.route('/api/funds/<int:fund_id>', methods=['GET'])
def get_fund_by_id(fund_id):
    """
    Get detailed information about a specific fund.
    
    Path Parameters:
        fund_id (int): ID of the fund to retrieve
    
    Query Parameters:
        include_events (bool): Include fund events in response (default: true)
        include_cash_flows (bool): Include cash flow details (default: false)
        include_tax_statements (bool): Include tax statement data (default: false)
        
    Returns:
        Standardized response with fund data and optional related information
    """
    try:
        # Parse query parameters for controlling response detail level
        include_events = request.args.get('include_events', 'false').lower() == 'true'
        include_cash_flows = request.args.get('include_cash_flows', 'false').lower() == 'true'
        include_tax_statements = request.args.get('include_tax_statements', 'false').lower() == 'true'
        
        dto = fund_controller.get_fund_by_id(
            fund_id=fund_id,
            include_events=include_events,
            include_cash_flows=include_cash_flows,
            include_tax_statements=include_tax_statements
        )
        
        return handle_controller_response(dto)
    
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create fund
###############################################

@fund_bp.route('/api/funds', methods=['POST'])
@validate_fund_data
def create_fund():
    """
    Create a new fund.
    
    Request Body:
        name (str): Fund name (required)
        description (str): Fund description (optional)
        start_date (str): Fund start date in YYYY-MM-DD format (required)
        end_date (str): Fund end date in YYYY-MM-DD format (optional)
        entity_id (int): Associated entity ID (required)
    
    Returns:
        Standardized response with created fund data
    """
    try:
        dto = fund_controller.create_fund()
        return handle_controller_response(dto)
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating fund: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete fund
###############################################

@fund_bp.route('/api/funds/<int:fund_id>', methods=['DELETE'])
def delete_fund(fund_id):
    """
    Delete a fund.
    
    Path Parameters:
        fund_id (int): ID of the fund to delete
    
    Returns:
        Standardized response confirming deletion (204 No Content on success)
    """
    try:
        dto = fund_controller.delete_fund(fund_id)
        return handle_delete_response(dto)
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

###############################################################
# FUND EVENTS ENDPOINTS
###############################################################

###############################################
# Get fund events
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/events', methods=['GET'])
def get_fund_events(fund_id):
    """
    Get all events for a specific fund.
    
    Path Parameters:
        fund_id (int): ID of the fund
    
    Returns:
        Standardized response with list of fund events
    """
    try:
        dto = fund_controller.get_fund_events(fund_id)
        return handle_controller_response(dto)
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund events {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

###############################################
# Create fund event
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/events', methods=['POST'])
@validate_fund_event_data
def create_fund_event(fund_id):
    """
    Create a new fund event.
    
    Path Parameters:
        fund_id (int): ID of the fund
    
    Request Body:
        event_type (str): Type of event (CAPITAL_CALL, RETURN_OF_CAPITAL, UNIT_PURCHASE, UNIT_SALE)
        amount (float): Event amount (required)
        event_date (str): Event date in YYYY-MM-DD format (required)
        description (str): Event description (optional)
    
    Returns:
        Standardized response with created event data
    """
    try:
        # Use validated data from middleware
        validated_data = request.validated_data
        
        # Route to specific method based on event type
        event_type = validated_data.get('event_type')
        if not event_type:
            response = ApiResponse(
                response_code=ApiResponseCode.VALIDATION_ERROR,
                message='event_type is required'
            )
            return jsonify(response.to_dict()), response.response_code.get_http_status_code()

        dto = fund_controller.create_fund_event(validated_data)
        
        # if event_type == 'CAPITAL_CALL':
        #     dto = fund_controller.create_capital_call(fund_id, validated_data)
        # elif event_type == 'RETURN_OF_CAPITAL':
        #     dto = fund_controller.create_return_of_capital(fund_id, validated_data)
        # elif event_type == 'UNIT_PURCHASE':
        #     dto = fund_controller.create_unit_purchase(fund_id, validated_data)
        # elif event_type == 'UNIT_SALE':
        #     dto = fund_controller.create_unit_sale(fund_id, validated_data)
        # elif event_type == 'NAV_UPDATE':
        #     dto = fund_controller.create_nav_update(fund_id, validated_data)
        # elif event_type == 'DISTRIBUTION':
        #     dto = fund_controller.create_distribution(fund_id, validated_data)
        # else:
        #     response = ApiResponse(
        #         response_code=ApiResponseCode.VALIDATION_ERROR,
        #         message=f'Unsupported event type: {event_type}'
        #     )
        #     return jsonify(response.to_dict()), response.response_code.get_http_status_code()
        
        return handle_controller_response(dto)
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating fund event {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete fund event
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/events/<int:event_id>', methods=['DELETE'])
def delete_fund_event(fund_id, event_id):
    """
    Delete a specific fund event.
    
    Path Parameters:
        fund_id (int): ID of the fund
        event_id (int): ID of the event to delete
    
    Returns:
        Standardized response confirming deletion (204 No Content on success)
    """
    try:
        dto = fund_controller.delete_fund_event(fund_id, event_id)
        return handle_delete_response(dto)
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting fund event {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################################
# FUND EVENT CASH FLOWS ENDPOINTS
###############################################################

###############################################
# Get fund event cash flows
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/events/<int:event_id>/cash-flows', methods=['GET'])
def get_fund_event_cash_flows(fund_id, event_id, bank_account_id):
    """
    Get all cash flows for a specific fund event.
    
    Path Parameters:
        fund_id (int): ID of the fund
        event_id (int): ID of the event
        bank_account_id (int): ID of the bank account
    """
    try:
        dto = fund_controller.get_fund_event_cash_flows(fund_id, event_id, bank_account_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund event cash flows {fund_id}: {event_id}: {bank_account_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@fund_bp.route('/api/funds/<int:fund_id>/events/<int:event_id>/cash-flows/<int:cash_flow_id>', methods=['GET'])
def get_fund_event_cash_flow_by_id(cash_flow_id):
    """
    Get a cash flow by ID for a specific fund event.
    
    Path Parameters:
        cash_flow_id (int): ID of the cash flow
    """
    try:
        dto = fund_controller.get_fund_event_cash_flow_by_id(cash_flow_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund event cash flow by ID {cash_flow_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create fund event cash flows
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/events/<int:event_id>/cash-flows', methods=['POST'])
@validate_cash_flow_data
def create_fund_event_cash_flow():
    """
    Create a new cash flow for a specific fund event.

    Request Body:
        bank_account_id (int): ID of the bank account
        amount (float): Amount of the cash flow
        transfer_date (str): Transfer date in YYYY-MM-DD format
        direction (str): Direction of the cash flow (IN or OUT)
        reference (str): Reference of the cash flow
        notes (str): Notes of the cash flow

    Returns:
        Standardized response with created cash flow data
    """
    try:
        dto = fund_controller.create_fund_event_cash_flow()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating fund event cash flow: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete fund event cash flows
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/events/<int:event_id>/cash-flows/<int:cash_flow_id>', methods=['DELETE'])
def delete_fund_event_cash_flow(fund_id, event_id, cash_flow_id):
    """Delete a specific cash flow for a specific fund event"""
    try:
        dto = fund_controller.delete_fund_event_cash_flow(cash_flow_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting fund event cash flow {fund_id}: {event_id}: {cash_flow_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################################
# FUND TAX STATEMENT ENDPOINTS
###############################################################

###############################################
# Get fund tax statements
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/tax-statements', methods=['GET'])
def get_fund_tax_statements(fund_id):
    """Get all tax statements for a specific fund"""
    try:
        dto = fund_controller.get_fund_tax_statements(fund_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund tax statements {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@fund_bp.route('/api/funds/<int:fund_id>/tax-statements/<int:fund_tax_statement_id>', methods=['GET'])
def get_fund_tax_statement_by_id(fund_tax_statement_id):
    """Get a tax statement by ID for a specific fund"""
    try:
        dto = fund_controller.get_fund_tax_statement_by_id(fund_tax_statement_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund tax statement by ID {fund_tax_statement_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create fund tax statement
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/tax-statements', methods=['POST'])
def create_fund_tax_statement():
    """Create a new tax statement for a specific fund"""
    try:
        dto = fund_controller.create_fund_tax_statement()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating fund tax statement: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete fund tax statement
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/tax-statements/<int:fund_tax_statement_id>', methods=['DELETE'])
def delete_fund_tax_statement(fund_tax_statement_id):
    """Delete a specific tax statement for a specific fund"""
    try:
        dto = fund_controller.delete_fund_tax_statement(fund_tax_statement_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting fund tax statement {fund_tax_statement_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()