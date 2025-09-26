"""
Fund API Routes.

This module contains all fund-related API endpoints including
fund management, fund events, tax statements, and cash flows.

All endpoints use middleware validation for input data.
All endpoints use the fund controller with DTO responses.
"""

from flask import Blueprint, jsonify, request
from src.api.middleware.validation import validate_request, validate_distribution_data
from src.fund.enums.fund_enums import FundStatus, FundTrackingType, FundInvestmentType
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response
from src.api.controllers.fund_controller import FundController
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode
from src.shared.enums.shared_enums import Country, Currency
from src.fund.enums.fund_event_cash_flow_enums import CashFlowDirection
from src.fund.enums.fund_event_enums import EventType, DistributionType


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
@validate_request(
    field_types={
        'company_id': 'int',
        'entity_id': 'int',
        'fund_status': 'string',
        'fund_tracking_type': 'string',
        'include_events': 'bool',
        'include_cash_flows': 'bool',
        'include_tax_statements': 'bool'
    },
    field_lengths={
        'fund_status': {'max': 255},
        'fund_tracking_type': {'max': 255}
    },
    field_ranges={
        'company_id': {'min': 1},
        'entity_id': {'min': 1}
    },
    enum_fields={
        'fund_status': FundStatus,
        'fund_tracking_type': FundTrackingType
    },
    sanitize=True
)
def get_funds():
    """
    Get all funds.

    Query Parameters (all optional):
        company_id (int): ID of the company
        entity_id (int): ID of the entity
        fund_status (str): Status of the fund
        fund_tracking_type (str): Tracking type of the fund
        include_events (bool): Include fund events in response (default: false)
        include_cash_flows (bool): Include cash flow details (default: false)
        include_tax_statements (bool): Include tax statement data (default: false)
    """
    try:
        dto = fund_controller.get_funds()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting funds: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@fund_bp.route('/api/funds/<int:fund_id>', methods=['GET'])
@validate_request(
    field_types={
        'include_events': 'bool',
        'include_cash_flows': 'bool',
        'include_tax_statements': 'bool'
    }
)
def get_fund_by_id(fund_id):
    """
    Get detailed information about a specific fund.
    
    Path Parameters:
        fund_id (int): ID of the fund to retrieve
    
    Query Parameters (all optional):
        include_events (bool): Include fund events in response (default: true)
        include_cash_flows (bool): Include cash flow details (default: false)
        include_tax_statements (bool): Include tax statement data (default: false)
        
    Returns:
        Standardized response with fund data and optional related information
    """
    try:
        dto = fund_controller.get_fund_by_id(fund_id=fund_id)
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
@validate_request(
    required_fields=['name', 'entity_id', 'investment_company_id', 'tracking_type', 'tax_jurisdiction', 'currency'],
    field_types={
        'entity_id': 'int',
        'investment_company_id': 'int',
        'name': 'string',
        'fund_investment_type': 'string',
        'tracking_type': 'string',
        'description': 'string',
        'currency': 'string',
        'tax_jurisdiction': 'string',
        'expected_irr': 'float',
        'expected_duration_months': 'int',
        'commitment_amount': 'float',
    },
    field_lengths={
        'name': {'min': 2, 'max': 255},
        'fund_investment_type': {'max': 255},
        'description': {'max': 1000},
        'expected_irr': {'max': 100},
        'expected_duration_months': {'max': 1200},
        'commitment_amount': {'max': 999999999},
    },
    field_ranges={
        'entity_id': {'min': 1},
        'investment_company_id': {'min': 1},
        'expected_irr': {'min': 0, 'max': 100},
        'expected_duration_months': {'min': 1, 'max': 1200},
        'commitment_amount': {'min': 0, 'max': 999999999},
    },
    enum_fields={
        'fund_investment_type': FundInvestmentType,
        'tracking_type': FundTrackingType,
        'tax_jurisdiction': Country,
        'currency': Currency
    },
    sanitize=True
)
def create_fund():
    """
    Create a new fund.
    
    Request Body:
        entity_id (int): Associated entity ID (required)
        investment_company_id (int): Associated investment company ID (required)
        name (str): Fund name (required)
        fund_investment_type (str): Fund investment type (required)
        tracking_type (str): Tracking type (required)
        description (str): Fund description (optional)
        currency (str): Currency (required)
        tax_jurisdiction (str): Tax jurisdiction (required)
        expected_irr (float): Expected IRR (optional)
        expected_duration_months (int): Expected duration months (optional)
        commitment_amount (float): Commitment amount (optional)
    
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

@fund_bp.route('/api/fund-events', methods=['GET'])
def get_fund_events():
    """
    Get all events for a specific fund.
    
    Query Parameters:
        fund_id (int): ID of the fund
        event_type (str): Type of event (CAPITAL_CALL, RETURN_OF_CAPITAL, UNIT_PURCHASE, UNIT_SALE)
        event_date (str): Event date in YYYY-MM-DD format
        description (str): Event description
    
    Returns:
        Standardized response with list of fund events
    """
    try:
        dto = fund_controller.get_fund_events()
        return handle_controller_response(dto)
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund events: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@fund_bp.route('/api/funds/<int:fund_id>/fund-events', methods=['GET'])
def get_fund_events_by_fund_id(fund_id):
    """
    Get all events for a specific fund.
    
    Path Parameters:
        fund_id (int): ID of the fund
    """
    try:
        dto = fund_controller.get_fund_events(fund_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund events for fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@fund_bp.route('/api/funds/<int:fund_id>/fund-events/<int:fund_event_id>', methods=['GET'])
def get_fund_event_by_id(fund_id, fund_event_id):
    """
    Get a specific fund event.
    
    Path Parameters:
        fund_id (int): ID of the fund
        fund_event_id (int): ID of the event
    """
    try:
        dto = fund_controller.get_fund_event_by_id(fund_event_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund event {fund_event_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

###############################################
# Create fund event
###############################################
@fund_bp.route('/api/funds/<int:fund_id>/fund-events/capital-call', methods=['POST'])
@validate_request(
    required_fields=['event_date', 'amount'],
    field_types={
        'event_date': 'date',
        'amount': 'float',
        'description': 'string',
        'reference_number': 'string',
    },
    field_lengths={
        'event_date': {'min': 10, 'max': 10},
        'description': {'max': 1000},
        'reference_number': {'max': 255},
    },
    field_ranges={
        'amount': {'min': 0, 'max': 9999999999},
    },
    sanitize=True
)
def create_capital_call(fund_id):
    """
    Create a new capital call event for a specific fund.

    Path Parameters:
        fund_id (int): ID of the fund

    Request Body:
        event_date (str): Event date in YYYY-MM-DD format (required)
        amount (float): Event amount (required)
        description (str): Event description (optional)
        reference_number (str): Event reference number (optional)
    """
    try:
        dto = fund_controller.create_fund_event(fund_id, EventType.CAPITAL_CALL)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating capital call for fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@fund_bp.route('/api/funds/<int:fund_id>/fund-events/return-of-capital', methods=['POST'])
@validate_request(
    required_fields=['event_date', 'amount'],
    field_types={
        'event_date': 'date',
        'amount': 'float',
        'description': 'string',
        'reference_number': 'string',
    },
    field_lengths={
        'event_date': {'min': 10, 'max': 10},
        'description': {'max': 1000},
        'reference_number': {'max': 255},
    },
    field_ranges={
        'amount': {'min': 0, 'max': 9999999999},
    },
    sanitize=True
)
def create_return_of_capital(fund_id):
    """
    Create a new return of capital event for a specific fund.

    Path Parameters:
        fund_id (int): ID of the fund

    Request Body:
        event_date (str): Event date in YYYY-MM-DD format (required)
        amount (float): Event amount (required)
        description (str): Event description (optional)
        reference_number (str): Event reference number (optional)
    """
    try:
        dto = fund_controller.create_fund_event(fund_id, EventType.RETURN_OF_CAPITAL)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating return of capital for fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@fund_bp.route('/api/funds/<int:fund_id>/fund-events/unit-purchase', methods=['POST'])
@validate_request(
    required_fields=['event_date', 'amount', 'units_purchased', 'unit_price'],
    field_types={
        'event_date': 'date',
        'amount': 'float',
        'description': 'string',
        'reference_number': 'string',
        'units_purchased': 'float',
        'unit_price': 'float',
        'brokerage_fee': 'float',
    },
    field_lengths={
        'event_date': {'min': 10, 'max': 10},
        'description': {'max': 1000},
        'reference_number': {'max': 255},
    },
    field_ranges={
        'amount': {'min': 0, 'max': 9999999999},
        'units_purchased': {'min': 0, 'max': 9999999999},
        'unit_price': {'min': 0, 'max': 9999999999},
        'brokerage_fee': {'min': 0, 'max': 9999999999},
    },
    sanitize=True
)
def create_unit_purchase(fund_id):
    """
    Create a new unit purchase event for a specific fund.

    Path Parameters:
        fund_id (int): ID of the fund

    Request Body:
        event_date (str): Event date in YYYY-MM-DD format (required)
        amount (float): Event amount (required)
        description (str): Event description (optional)
        reference_number (str): Event reference number (optional)
        units_purchased (float): Units purchased (required)
        unit_price (float): Unit price (required)
        brokerage_fee (float): Brokerage fee (required)
    """
    try:
        dto = fund_controller.create_fund_event(fund_id, EventType.UNIT_PURCHASE)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating unit purchase for fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@fund_bp.route('/api/funds/<int:fund_id>/fund-events/unit-sale', methods=['POST'])
@validate_request(
    required_fields=['event_date', 'amount', 'units_sold', 'unit_price'],
    field_types={
        'event_date': 'date',
        'amount': 'float',
        'description': 'string',
        'reference_number': 'string',
        'units_sold': 'float',
        'unit_price': 'float',
        'brokerage_fee': 'float',
    },
    field_lengths={
        'event_date': {'min': 10, 'max': 10},
        'description': {'max': 1000},
        'reference_number': {'max': 255},
    },
    field_ranges={
        'amount': {'min': 0, 'max': 9999999999},
        'units_sold': {'min': 0, 'max': 9999999999},
        'unit_price': {'min': 0, 'max': 9999999999},
        'brokerage_fee': {'min': 0, 'max': 9999999999},
    },
    sanitize=True
)
def create_unit_sale(fund_id):
    """
    Create a new unit sale event for a specific fund.

    Path Parameters:
        fund_id (int): ID of the fund

    Request Body:
        event_date (str): Event date in YYYY-MM-DD format (required)
        amount (float): Event amount (required)
        description (str): Event description (optional)
        reference_number (str): Event reference number (optional)
        units_sold (float): Units sold (required)
        unit_price (float): Unit price (required)
        brokerage_fee (float): Brokerage fee (required)
    """
    try:
        dto = fund_controller.create_fund_event(fund_id, EventType.UNIT_SALE)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating unit sale for fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@fund_bp.route('/api/funds/<int:fund_id>/fund-events/nav-update', methods=['POST'])
@validate_request(
    required_fields=['event_date', 'nav_per_share'],
    field_types={
        'event_date': 'date',
        'description': 'string',
        'reference_number': 'string',
        'nav_per_share': 'float',
    },
    field_lengths={
        'event_date': {'min': 10, 'max': 10},
        'description': {'max': 1000},
        'reference_number': {'max': 255},
    },
    field_ranges={
        'nav_per_share': {'min': 0, 'max': 9999999999},
    },
    sanitize=True
)
def create_nav_update(fund_id):
    """
    Create a new NAV update event for a specific fund.

    Path Parameters:
        fund_id (int): ID of the fund

    Request Body:
        event_date (str): Event date in YYYY-MM-DD format (required)
        nav_per_share (float): NAV per share (required)
        description (str): Event description (optional)
        reference_number (str): Event reference number (optional)
    """
    try:
        dto = fund_controller.create_fund_event(fund_id, EventType.NAV_UPDATE)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating NAV update for fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@fund_bp.route('/api/funds/<int:fund_id>/fund-events/distribution', methods=['POST'])
@validate_request(
    required_fields=['event_date', 'distribution_type'],
    field_types={
        'event_date': 'date',
        'amount': 'float',
        'description': 'string',
        'reference_number': 'string',
        'distribution_type': 'string',
        'has_withholding_tax': 'bool',
        'gross_amount': 'float',
        'net_amount': 'float',
        'withholding_tax_amount': 'float',
        'withholding_tax_rate': 'float',
    },
    field_lengths={
        'event_date': {'min': 10, 'max': 10},
        'description': {'max': 1000},
        'reference_number': {'max': 255},
    },
    field_ranges={
        'amount': {'min': 0, 'max': 9999999999},
        'gross_amount': {'min': 0, 'max': 9999999999},
        'net_amount': {'min': 0, 'max': 9999999999},
        'withholding_tax_amount': {'min': 0, 'max': 9999999999},
        'withholding_tax_rate': {'min': 0, 'max': 100},
    },
    enum_fields={
        'distribution_type': DistributionType,
    },
    custom_validation=validate_distribution_data,
    sanitize=True
)
def create_distribution(fund_id):
    """
    Create a new distribution event for a specific fund.
    
    Supports both simple distributions and distributions with withholding tax.
    
    Path Parameters:
        fund_id (int): ID of the fund
    
    Request Body:
        event_date (str): Event date in YYYY-MM-DD format (required)
        distribution_type (str): Type of distribution (required)
        
        For simple distributions:
        - amount (float): Distribution amount (required)
        
        For withholding tax distributions:
        - has_withholding_tax (bool): Whether the distribution has withholding tax (required)
        - Exactly one of: gross_amount (float) OR net_amount (float) (required)
        - Exactly one of: withholding_tax_amount (float) OR withholding_tax_rate (float) (required)
        
        Optional fields:
        - description (str): Event description
        - reference_number (str): Event reference number
    """
    try:

        dto = fund_controller.create_fund_event(fund_id, EventType.DISTRIBUTION)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating distribution for fund {fund_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()






# @fund_bp.route('/api/funds/<int:fund_id>/fund-events', methods=['POST'])
# @validate_fund_event_data
# def create_fund_event(fund_id):
#     """
#     Create a new fund event.
    
#     Path Parameters:
#         fund_id (int): ID of the fund
    
#     Request Body:
#         event_type (str): Type of event (CAPITAL_CALL, RETURN_OF_CAPITAL, UNIT_PURCHASE, UNIT_SALE)
#         amount (float): Event amount (required)
#         event_date (str): Event date in YYYY-MM-DD format (required)
#         description (str): Event description (optional)
    
#     Returns:
#         Standardized response with created event data
#     """
#     try:
#         # Use validated data from middleware
#         validated_data = request.validated_data
        
#         # Route to specific method based on event type
#         event_type = validated_data.get('event_type')
#         if not event_type:
#             response = ApiResponse(
#                 response_code=ApiResponseCode.VALIDATION_ERROR,
#                 message='event_type is required'
#             )
#             return jsonify(response.to_dict()), response.response_code.get_http_status_code()

#         dto = fund_controller.create_fund_event(validated_data)
        
#         # if event_type == 'CAPITAL_CALL':
#         #     dto = fund_controller.create_capital_call(fund_id, validated_data)
#         # elif event_type == 'RETURN_OF_CAPITAL':
#         #     dto = fund_controller.create_return_of_capital(fund_id, validated_data)
#         # elif event_type == 'UNIT_PURCHASE':
#         #     dto = fund_controller.create_unit_purchase(fund_id, validated_data)
#         # elif event_type == 'UNIT_SALE':
#         #     dto = fund_controller.create_unit_sale(fund_id, validated_data)
#         # elif event_type == 'NAV_UPDATE':
#         #     dto = fund_controller.create_nav_update(fund_id, validated_data)
#         # elif event_type == 'DISTRIBUTION':
#         #     dto = fund_controller.create_distribution(fund_id, validated_data)
#         # else:
#         #     response = ApiResponse(
#         #         response_code=ApiResponseCode.VALIDATION_ERROR,
#         #         message=f'Unsupported event type: {event_type}'
#         #     )
#         #     return jsonify(response.to_dict()), response.response_code.get_http_status_code()
        
#         return handle_controller_response(dto)
            
#     except Exception as e:
#         response = ApiResponse(
#             response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
#             message=f"Unexpected error creating fund event {fund_id}: {str(e)}"
#         )
#         return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete fund event
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/fund-events/<int:fund_event_id>', methods=['DELETE'])
def delete_fund_event(fund_id, fund_event_id):
    """
    Delete a specific fund event.
    
    Path Parameters:
        fund_id (int): ID of the fund
        fund_event_id (int): ID of the event to delete
    
    Returns:
        Standardized response confirming deletion (204 No Content on success)
    """
    try:
        dto = fund_controller.delete_fund_event(fund_event_id)
        return handle_delete_response(dto)
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting fund event {fund_event_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################################
# FUND EVENT CASH FLOWS ENDPOINTS
###############################################################

###############################################
# Get fund event cash flows
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/fund-events/<int:fund_event_id>/fund-event-cash-flows', methods=['GET'])
@validate_request(
    field_types={
        'fund_id': 'int',
        'fund_event_id': 'int',
        'bank_account_id': 'int',
    },
    field_ranges={
        'fund_id': {'min': 1},
        'fund_event_id': {'min': 1},
        'bank_account_id': {'min': 1}
    },
    sanitize=True
)
def get_fund_event_cash_flows():
    """
    Get all cash flows for a specific fund event.
    
    Query Parameters:
        fund_id (int): ID of the fund
        fund_event_id (int): ID of the event
        bank_account_id (int): ID of the bank account
    """
    try:
        dto = fund_controller.get_fund_event_cash_flows()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund event cash flows: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@fund_bp.route('/api/funds/<int:fund_id>/fund-events/<int:fund_event_id>/fund-event-cash-flows', methods=['GET'])
def get_fund_event_cash_flows_by_fund_id_and_event_id(fund_id, fund_event_id):
    """
    Get all cash flows for a specific fund event.
    
    Path Parameters:
        fund_id (int): ID of the fund
        fund_event_id (int): ID of the event
    """
    try:
        dto = fund_controller.get_fund_event_cash_flows(fund_id, fund_event_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund event cash flows {fund_id}: {fund_event_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@fund_bp.route('/api/funds/<int:fund_id>/fund-events/<int:fund_event_id>/fund-event-cash-flows/<int:fund_event_cash_flow_id>', methods=['GET'])
def get_fund_event_cash_flow_by_id(fund_id, fund_event_id, fund_event_cash_flow_id):
    """
    Get a cash flow by ID for a specific fund event.
    
    Path Parameters:
        fund_id (int): ID of the fund
        fund_event_id (int): ID of the event
        fund_event_cash_flow_id (int): ID of the cash flow
    """
    try:
        dto = fund_controller.get_fund_event_cash_flow_by_id(fund_event_cash_flow_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund event cash flow by ID {fund_event_cash_flow_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create fund event cash flows
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/fund-events/<int:fund_event_id>/fund-event-cash-flows', methods=['POST'])
@validate_request(
    required_fields=['bank_account_id', 'direction', 'transfer_date', 'currency', 'amount'],
    field_types={
        'bank_account_id': 'int',
        'direction': 'string',
        'transfer_date': 'date',
        'currency': 'string',
        'amount': 'float',
        'reference': 'string',
        'description': 'string'
    },
    field_lengths={
        'transfer_date': {'min': 10, 'max': 10},
        'reference': {'max': 255},
        'description': {'max': 1000}
    },
    field_ranges={
        'bank_account_id': {'min': 1},
        'amount': {'min': 0, 'max': 9999999999},
        'transfer_date': {'min': 0, 'max': 9999999999},
        'currency': {'min': 0}
    },
    enum_fields={
        'direction': CashFlowDirection,
        'currency': Currency
    },
    sanitize=True
)
def create_fund_event_cash_flow(fund_id, fund_event_id):
    """
    Create a new cash flow for a specific fund event.

    Request Body:
        fund_event_id (int): ID of the fund event
        bank_account_id (int): ID of the bank account
        amount (float): Amount of the cash flow
        transfer_date (str): Transfer date in YYYY-MM-DD format
        direction (str): Direction of the cash flow (IN or OUT)
        currency (str): Currency of the cash flow
        reference (str): Reference of the cash flow
        description (str): Description of the cash flow

    Returns:
        Standardized response with created cash flow data
    """
    try:
        dto = fund_controller.create_fund_event_cash_flow(fund_event_id)
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

@fund_bp.route('/api/funds/<int:fund_id>/fund-events/<int:fund_event_id>/fund-event-cash-flows/<int:fund_event_cash_flow_id>', methods=['DELETE'])
def delete_fund_event_cash_flow(fund_id, fund_event_id, fund_event_cash_flow_id):
    """Delete a specific cash flow for a specific fund event"""
    try:
        dto = fund_controller.delete_fund_event_cash_flow(fund_event_cash_flow_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting fund event cash flow {fund_id}: {fund_event_id}: {fund_event_cash_flow_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################################
# FUND TAX STATEMENT ENDPOINTS
###############################################################

###############################################
# Get fund tax statements
###############################################

@fund_bp.route('/api/fund-tax-statements', methods=['GET'])
@validate_request(
    field_types={
        'fund_id': 'int',
        'entity_id': 'int',
        'financial_year': 'string',
        'start_tax_payment_date': 'date',
        'end_tax_payment_date': 'date',
    },
    field_ranges={
        'fund_id': {'min': 1},
        'entity_id': {'min': 1},
        'start_tax_payment_date': {'min': 0, 'max': 9999999999},
        'end_tax_payment_date': {'min': 0, 'max': 9999999999}
    },
    field_lengths={
        'financial_year': {'max': 255},
        'start_tax_payment_date': {'min': 10, 'max': 10},
        'end_tax_payment_date': {'min': 10, 'max': 10}
    },
    sanitize=True
)
def get_fund_tax_statements():
    """Get all tax statements for a specific fund"""
    try:
        dto = fund_controller.get_fund_tax_statements()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting fund tax statements: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()

@fund_bp.route('/api/funds/<int:fund_id>/fund-tax-statements', methods=['GET'])
def get_fund_tax_statements_by_fund_id(fund_id):
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

@fund_bp.route('/api/funds/<int:fund_id>/fund-tax-statements/<int:fund_tax_statement_id>', methods=['GET'])
def get_fund_tax_statement_by_id(fund_id, fund_tax_statement_id):
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

@fund_bp.route('/api/funds/<int:fund_id>/fund-tax-statements', methods=['POST'])
@validate_request(
    required_fields=['entity_id', 'financial_year'],
    field_types={
        'entity_id': 'int',
        'financial_year': 'string',
        'tax_payment_date': 'date',
        'statement_date': 'date',
        'interest_income_tax_rate': 'float',
        'interest_received_in_cash': 'float',
        'interest_receivable_this_fy': 'float',
        'interest_receivable_prev_fy': 'float',
        'interest_non_resident_withholding_tax_from_statement': 'float',
        'dividend_franked_income_amount': 'float',
        'dividend_unfranked_income_amount': 'float',
        'dividend_franked_income_tax_rate': 'float',
        'dividend_unfranked_income_tax_rate': 'float',
        'capital_gain_income_amount': 'float',
        'capital_gain_income_tax_rate': 'float',
        'eofy_debt_interest_deduction_rate': 'float',
        'non_resident': 'bool',
        'accountant': 'string',
        'notes': 'string',
    },
    field_lengths={
        'financial_year': {'min': 4, 'max': 4},
        'tax_payment_date': {'min': 10, 'max': 10},
        'statement_date': {'min': 10, 'max': 10},
        'interest_income_tax_rate': {'min': 0, 'max': 100},
        'interest_received_in_cash': {'max': 9999999999},
        'interest_receivable_this_fy': {'max': 9999999999},
        'interest_receivable_prev_fy': {'max': 9999999999},
        'interest_non_resident_withholding_tax_from_statement': {'max': 9999999999},
        'dividend_franked_income_amount': {'max': 9999999999},
        'dividend_unfranked_income_amount': {'max': 9999999999},
        'dividend_franked_income_tax_rate': {'min': 0, 'max': 100},
        'dividend_unfranked_income_tax_rate': {'min': 0, 'max': 100},
        'capital_gain_income_amount': {'max': 9999999999},
        'capital_gain_income_tax_rate': {'min': 0, 'max': 100},
        'eofy_debt_interest_deduction_rate': {'min': 0, 'max': 100},
        'accountant': {'max': 255},
        'notes': {'max': 1000}
    },
    field_ranges={
        'entity_id': {'min': 1},
    },
    sanitize=True
)
def create_fund_tax_statement(fund_id):
    """Create a new tax statement for a specific fund"""
    try:
        dto = fund_controller.create_fund_tax_statement(fund_id)
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

@fund_bp.route('/api/funds/<int:fund_id>/fund-tax-statements/<int:fund_tax_statement_id>', methods=['DELETE'])
def delete_fund_tax_statement(fund_id, fund_tax_statement_id):
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