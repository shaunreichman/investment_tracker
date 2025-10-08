"""
Fund API Routes.

This module contains all fund-related API endpoints including
fund management, fund events, tax statements, and cash flows.

All endpoints use middleware validation for input data.
All endpoints use the fund controller with DTO responses.
"""

from flask import Blueprint, jsonify, request
from src.api.middleware.validation import validate_request, validate_distribution_data
from src.fund.enums.fund_enums import FundStatus, FundTrackingType, FundInvestmentType, SortFieldFund
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response
from src.api.controllers.fund_controller import FundController
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode
from src.shared.enums.shared_enums import Country, Currency, SortOrder
from src.fund.enums.fund_event_cash_flow_enums import CashFlowDirection
from src.fund.enums.fund_event_enums import EventType, DistributionType, TaxPaymentType, GroupType
from src.fund.enums.fund_event_enums import SortFieldFundEvent
from src.fund.enums.fund_event_cash_flow_enums import SortFieldFundEventCashFlow
from src.fund.enums.fund_tax_statement_enums import SortFieldFundTaxStatement


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
        'company_ids': 'int_array',
        'entity_id': 'int',
        'entity_ids': 'int_array',
        'fund_status': 'string',
        'fund_statuses': 'string_array',
        'fund_tracking_type': 'string',
        'fund_tracking_types': 'string_array',
        'start_start_date': 'date',
        'end_start_date': 'date',
        'start_end_date': 'date',
        'end_end_date': 'date',
        'sort_by': 'string',
        'sort_order': 'string',
        'include_fund_events': 'bool',
        'include_fund_event_cash_flows': 'bool',
        'include_fund_tax_statements': 'bool'
    },
    field_ranges={
        'company_id': {'min': 1},
        'entity_id': {'min': 1}
    },
    enum_fields={
        'fund_status': FundStatus,
        'fund_tracking_type': FundTrackingType,
        'sort_by': SortFieldFund,
        'sort_order': SortOrder
    },
    array_element_ranges={
        'company_ids': {'min': 1},
        'entity_ids': {'min': 1}
    },
    array_element_enum_fields={
        'fund_statuses': FundStatus,
        'fund_tracking_types': FundTrackingType
    },
    mutually_exclusive_groups=[
        ['company_id', 'company_ids'],
        ['entity_id', 'entity_ids'],
        ['fund_status', 'fund_statuses'],
        ['fund_tracking_type', 'fund_tracking_types']
    ],
    sanitize=True
)
def get_funds():
    """
    Get all funds.

    Query Parameters (all optional):
        company_id (int): ID of the company
        company_ids (int_array): IDs of the companies
        entity_id (int): ID of the entity
        entity_ids (int_array): IDs of the entities
        fund_status (str): Status of the fund
        fund_statuses (string_array): Statuses of the funds
        fund_tracking_type (str): Tracking type of the fund
        fund_tracking_types (string_array): Tracking types of the funds
        start_start_date (date): Start start date
        end_start_date (date): End start date
        start_end_date (date): End end date
        end_end_date (date): End end date
        sort_by (str): Field to sort by
        sort_order (str): Sort order
        include_fund_events (bool): Include fund events in response (default: false)
        include_fund_event_cash_flows (bool): Include cash flow details (default: false)
        include_fund_tax_statements (bool): Include tax statement data (default: false)
    
    Returns:
        Standardized response with list of funds
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
        'include_fund_events': 'bool',
        'include_fund_event_cash_flows': 'bool',
        'include_fund_tax_statements': 'bool'
    }
)
def get_fund_by_id(fund_id):
    """
    Get detailed information about a specific fund.
    
    Path Parameters:
        fund_id (int): ID of the fund to retrieve
    
    Query Parameters (all optional):
        include_fund_events (bool): Include fund events in response (default: true)
        include_fund_event_cash_flows (bool): Include cash flow details (default: false)
        include_fund_tax_statements (bool): Include tax statement data (default: false)
        
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
        'name': 'string',
        'entity_id': 'int',
        'investment_company_id': 'int',
        'tracking_type': 'string',
        'tax_jurisdiction': 'string',
        'currency': 'string',
        'fund_investment_type': 'string',
        'description': 'string',
        'expected_irr': 'float',
        'expected_duration_months': 'int',
        'commitment_amount': 'float',
    },
    field_lengths={
        'name': {'min': 2, 'max': 255},
        'description': {'max': 1000},
    },
    field_ranges={
        'entity_id': {'min': 1},
        'investment_company_id': {'min': 1},
        'expected_irr': {'min': 0.0, 'max': 100.0},
        'expected_duration_months': {'min': 0, 'max': 1200},
        'commitment_amount': {'min': 0.0, 'max': 999999999.0},
    },
    enum_fields={
        'tracking_type': FundTrackingType,
        'tax_jurisdiction': Country,
        'currency': Currency,
        'fund_investment_type': FundInvestmentType
    },
    sanitize=True
)
def create_fund():
    """
    Create a new fund.
    
    Request Body:
        name (str): Fund name (required)
        entity_id (int): Associated entity ID (required)
        investment_company_id (int): Associated investment company ID (required)
        tracking_type (str): Tracking type (required)
        tax_jurisdiction (str): Tax jurisdiction (required)
        currency (str): Currency (required)
        fund_investment_type (str): Fund investment type (optional)
        description (str): Fund description (optional)
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
@validate_request(
    field_types={
        'fund_id': 'int',
        'fund_ids': 'int_array',
        'event_type': 'string',
        'event_types': 'string_array',
        'distribution_type': 'string',
        'distribution_types': 'string_array',
        'tax_payment_type': 'string',
        'tax_payment_types': 'string_array',
        'group_id': 'int',
        'group_ids': 'int_array',
        'group_type': 'string',
        'group_types': 'string_array',
        'is_cash_flow_complete': 'bool',
        'start_event_date': 'date',
        'end_event_date': 'date',
        'sort_by': 'string',
        'sort_order': 'string',
        'include_fund_event_cash_flows': 'bool'
    },
    field_ranges={
        'fund_id': {'min': 1},
        'group_id': {'min': 1}
    },
    enum_fields={
        'event_type': EventType,
        'distribution_type': DistributionType,
        'tax_payment_type': TaxPaymentType,
        'group_type': GroupType,
        'sort_by': SortFieldFundEvent,
        'sort_order': SortOrder
    },
    array_element_ranges={
        'fund_ids': {'min': 1},
        'group_ids': {'min': 1}
    },
    array_element_enum_fields={
        'event_types': EventType,
        'distribution_types': DistributionType,
        'tax_payment_types': TaxPaymentType,
        'group_types': GroupType
    },
    mutually_exclusive_groups=[
        ['fund_id', 'fund_ids'],
        ['event_type', 'event_types'],
        ['distribution_type', 'distribution_types'],
        ['tax_payment_type', 'tax_payment_types'],
        ['group_id', 'group_ids'],
        ['group_type', 'group_types']
    ],
)
def get_fund_events():
    """
    Get all events for a specific fund.
    
    Query Parameters:
        fund_id (int): ID of the fund
        fund_ids (int_array): IDs of the funds
        event_type (str): Type of event (CAPITAL_CALL, RETURN_OF_CAPITAL, UNIT_PURCHASE, UNIT_SALE)
        event_types (string_array): Types of events
        distribution_type (str): Type of distribution
        distribution_types (string_array): Types of distributions
        tax_payment_type (str): Type of tax payment
        tax_payment_types (string_array): Types of tax payments
        group_id (int): ID of the group
        group_ids (int_array): IDs of the groups
        group_type (str): Type of group
        group_types (string_array): Types of groups
        is_cash_flow_complete (bool): Whether the cash flow is complete
        start_event_date (str): Start event date in YYYY-MM-DD format
        end_event_date (str): End event date in YYYY-MM-DD format
        sort_by (str): Field to sort by
        sort_order (str): Sort order
        include_fund_event_cash_flows (bool): Whether to include cash flows
    
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
@validate_request(
    field_types={
        'include_fund_event_cash_flows': 'bool'
    }
)
def get_fund_events_by_fund_id(fund_id):
    """
    Get all events for a specific fund.
    
    Path Parameters:
        fund_id (int): ID of the fund

    Query Parameters:
        include_fund_event_cash_flows (bool): Whether to include cash flows

    Returns:
        Standardized response with list of fund events
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
@validate_request(
    field_types={
        'include_fund_event_cash_flows': 'bool'
    }
)
def get_fund_event_by_id(fund_id, fund_event_id):
    """
    Get a specific fund event.
    
    Path Parameters:
        fund_id (int): ID of the fund
        fund_event_id (int): ID of the event

    Query Parameters:
        include_fund_event_cash_flows (bool): Whether to include cash flows

    Returns:
        Standardized response with fund event
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

    Returns:
        Standardized response with fund event
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

    Returns:
        Standardized response with fund event
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
    required_fields=['event_date', 'units_purchased', 'unit_price'],
    forbidden_fields=['amount', 'units_owned', 'units_sold'],
    field_types={
        'event_date': 'date',
        'units_purchased': 'float',
        'unit_price': 'float',
        'brokerage_fee': 'float',
        'description': 'string',
        'reference_number': 'string',
    },
    field_lengths={
        'description': {'max': 1000},
        'reference_number': {'max': 255},
    },
    field_ranges={
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
        units_purchased (float): Units purchased (required)
        unit_price (float): Unit price (required)
        brokerage_fee (float): Brokerage fee (required)
        description (str): Event description (optional)
        reference_number (str): Event reference number (optional)

    Returns:
        Standardized response with fund event
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
    required_fields=['event_date', 'units_sold', 'unit_price'],
    forbidden_fields=['amount', 'units_owned', 'units_purchased'],
    field_types={
        'event_date': 'date',
        'units_sold': 'float',
        'unit_price': 'float',
        'brokerage_fee': 'float',
        'description': 'string',
        'reference_number': 'string',
    },
    field_lengths={
        'description': {'max': 1000},
        'reference_number': {'max': 255},
    },
    field_ranges={
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
        units_sold (float): Units sold (required)
        unit_price (float): Unit price (required)
        brokerage_fee (float): Brokerage fee (required)
        description (str): Event description (optional)
        reference_number (str): Event reference number (optional)

    Returns:
        Standardized response with fund event
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
    forbidden_fields=['amount', 'previous_nav_per_share', 'nav_change_absolute', 'nav_change_percentage', 'units_owned', 'units_purchased', 'units_sold'],
    field_types={
        'event_date': 'date',
        'nav_per_share': 'float',
        'description': 'string',
        'reference_number': 'string',
    },
    field_lengths={
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

    Returns:
        Standardized response with fund event
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
    forbidden_fields=['units_owned', 'units_purchased', 'units_sold'],
    field_types={
        'event_date': 'date',
        'amount': 'float',
        'distribution_type': 'string',
        'has_withholding_tax': 'bool',
        'gross_amount': 'float',
        'net_amount': 'float',
        'withholding_tax_amount': 'float',
        'withholding_tax_rate': 'float',
        'description': 'string',
        'reference_number': 'string',
    },
    field_lengths={
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

    Returns:
        Standardized response with fund event
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


###############################################
# Delete fund event
###############################################

@fund_bp.route('/api/funds/<int:fund_id>/fund-events/<int:fund_event_id>', methods=['DELETE'])
def delete_fund_event(fund_id, fund_event_id):
    """
    Delete a specific fund event.
    
    Path Parameters:
        fund_id (int): ID of the fund (not used)
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

@fund_bp.route('/api/fund-event-cash-flows', methods=['GET'])
@validate_request(
    field_types={
        'fund_id': 'int',
        'fund_ids': 'int_array',
        'fund_event_id': 'int',
        'fund_event_ids': 'int_array',
        'bank_account_id': 'int',
        'bank_account_ids': 'int_array',
        'different_month': 'bool',
        'adjusted_bank_account_balance_id': 'int',
        'adjusted_bank_account_balance_ids': 'int_array',
        'currency': 'string',
        'currencies': 'string_array',
        'start_transfer_date': 'date',
        'end_transfer_date': 'date',
        'start_fund_event_date': 'date',
        'end_fund_event_date': 'date',
        'sort_by': 'string',
        'sort_order': 'string',
    },
    field_ranges={
        'fund_id': {'min': 1},
        'fund_event_id': {'min': 1},
        'bank_account_id': {'min': 1},
        'adjusted_bank_account_balance_id': {'min': 1},
    },
    enum_fields={
        'currency': Currency,
        'sort_by': SortFieldFundEventCashFlow,
        'sort_order': SortOrder
    },
    array_element_ranges={
        'fund_ids': {'min': 1},
        'fund_event_ids': {'min': 1},
        'bank_account_ids': {'min': 1},
        'adjusted_bank_account_balance_ids': {'min': 1},
    },
    array_element_enum_fields={
        'currencies': Currency,
    },
    mutually_exclusive_groups=[
        ['fund_id', 'fund_ids'],
        ['fund_event_id', 'fund_event_ids'],
        ['bank_account_id', 'bank_account_ids'],
        ['adjusted_bank_account_balance_id', 'adjusted_bank_account_balance_ids'],
        ['currency', 'currencies'],
    ],
    sanitize=True
)
def get_fund_event_cash_flows():
    """
    Get all cash flows.
    
    Query Parameters:
        fund_id (int): ID of the fund
        fund_event_id (int): ID of the event
        bank_account_id (int): ID of the bank account
        bank_account_ids (int_array): IDs of the bank accounts
        different_month (bool): Whether the transfer date is in a different month to the fund event date
        adjusted_bank_account_balance_id (int): ID of the bank account balance
        adjusted_bank_account_balance_ids (int_array): IDs of the bank account balances
        currency (string): Currency
        currencies (string_array): Currencies
        start_transfer_date (date): Start date of the transfer date
        end_transfer_date (date): End date of the transfer date
        start_fund_event_date (date): Start date of the fund event date
        end_fund_event_date (date): End date of the fund event date
        sort_by (string): Field to sort by
        sort_order (string): Sort order

    Returns:
        Standardized response with fund event cash flows
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

    Returns:
        Standardized response with fund event cash flows
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
        fund_id (int): ID of the fund (not used)
        fund_event_id (int): ID of the event (not used)
        fund_event_cash_flow_id (int): ID of the cash flow

    Returns:
        Standardized response with fund event cash flow
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
        'reference': {'max': 255},
        'description': {'max': 1000}
    },
    field_ranges={
        'bank_account_id': {'min': 1},
        'amount': {'min': 0, 'max': 9999999999},
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

    Path Parameters:
        fund_id (int): ID of the fund
        fund_event_id (int): ID of the event

    Request Body:
        bank_account_id (int): ID of the bank account
        direction (str): Direction of the cash flow (IN or OUT)
        transfer_date (str): Transfer date in YYYY-MM-DD format
        currency (str): Currency of the cash flow
        amount (float): Amount of the cash flow
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
    """
    Delete a specific cash flow for a specific fund event.

    Path Parameters:
        fund_id (int): ID of the fund (not used)
        fund_event_id (int): ID of the event (not used)
        fund_event_cash_flow_id (int): ID of the cash flow

    Returns:
        Standardized response with deleted fund event cash flow
    """
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
        'fund_ids': 'int_array',
        'entity_id': 'int',
        'entity_ids': 'int_array',
        'financial_year': 'string',
        'financial_years': 'string_array',
        'start_tax_payment_date': 'date',
        'end_tax_payment_date': 'date',
        'sort_by': 'string',
        'sort_order': 'string',
    },
    field_ranges={
        'fund_id': {'min': 1},
        'entity_id': {'min': 1},
        'financial_year': {'min': 1900, 'max': 2100},
    },
    field_lengths={
        'financial_year': {'min': 4, 'max': 4},
    },
    enum_fields={
        'sort_by': SortFieldFundTaxStatement,
        'sort_order': SortOrder
    },
    array_element_ranges={
        'fund_ids': {'min': 1},
        'entity_ids': {'min': 1},
        'financial_years': {'min': 1900, 'max': 2100},
    },
    array_element_lengths={
        'financial_years': {'min': 4, 'max': 4},
    },
    mutually_exclusive_groups=[
        ['fund_id', 'fund_ids'],
        ['entity_id', 'entity_ids'],
        ['financial_year', 'financial_years'],
    ],
    sanitize=True
)
def get_fund_tax_statements():
    """
    Get all tax statements.

    Search parameters (all optional):
        fund_id: ID of the fund
        fund_ids: IDs of the funds
        entity_id: ID of the entity
        entity_ids: IDs of the entities
        financial_year: Financial year
        financial_years: Financial years
        start_tax_payment_date: Start tax payment date
        end_tax_payment_date: End tax payment date
        sort_by: Field to sort by
        sort_order: Sort order

    Returns:
        Standardized response with fund tax statements
    """
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
    """
    Get all tax statements for a specific fund.

    Path Parameters:
        fund_id (int): ID of the fund

    Returns:
        Standardized response with fund tax statements
    """
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
    """
    Get a fund tax statement by ID.

    Path Parameters:
        fund_id (int): ID of the fund (not used)
        fund_tax_statement_id (int): ID of the fund tax statement

    Returns:
        Standardized response with fund tax statement
    """
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
    forbidden_fields=['amount', 'interest_income_amount'],
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
        'capital_gain_discount_applicable_flag': 'bool',
        'eofy_debt_interest_deduction_rate': 'float',
        'accountant': 'string',
        'notes': 'string',
    },
    field_lengths={
        'financial_year': {'min': 4, 'max': 4},
        'accountant': {'max': 255},
        'notes': {'max': 1000}
    },
    field_ranges={
        'entity_id': {'min': 1},
        'financial_year': {'min': 1900, 'max': 2100},
        'interest_income_tax_rate': {'min': 0, 'max': 100},
        'interest_received_in_cash': {'min': 0, 'max': 9999999999},
        'interest_receivable_this_fy': {'min': 0, 'max': 9999999999},
        'interest_receivable_prev_fy': {'min': 0, 'max': 9999999999},
        'interest_non_resident_withholding_tax_from_statement': {'min': 0, 'max': 9999999999},
        'dividend_franked_income_amount': {'min': 0, 'max': 9999999999},
        'dividend_unfranked_income_amount': {'min': 0, 'max': 9999999999},
        'dividend_franked_income_tax_rate': {'min': 0, 'max': 100},
        'dividend_unfranked_income_tax_rate': {'min': 0, 'max': 100},
        'capital_gain_income_amount': {'min': 0, 'max': 9999999999},
        'capital_gain_income_tax_rate': {'min': 0, 'max': 100},
        'eofy_debt_interest_deduction_rate': {'min': 0, 'max': 100},
    },
    sanitize=True
)
def create_fund_tax_statement(fund_id):
    """
    Create a new fund tax statement for a specific fund.

    Path Parameters:
        fund_id (int): ID of the fund

    Request Body:
        entity_id (int): ID of the entity
        financial_year (string): Financial year
        tax_payment_date (date): Tax payment date
        statement_date (date): Statement date
        interest_income_tax_rate (float): Interest income tax rate
        interest_received_in_cash (float): Interest received in cash
        interest_receivable_this_fy (float): Interest receivable this FY
        interest_receivable_prev_fy (float): Interest receivable previous FY
        interest_non_resident_withholding_tax_from_statement (float): Interest non-resident withholding tax from statement
        dividend_franked_income_amount (float): Dividend franked income amount
        dividend_unfranked_income_amount (float): Dividend unfranked income amount
        dividend_franked_income_tax_rate (float): Dividend franked income tax rate
        dividend_unfranked_income_tax_rate (float): Dividend unfranked income tax rate
        capital_gain_income_amount (float): Capital gain income amount
        capital_gain_income_tax_rate (float): Capital gain income tax rate
        capital_gain_discount_applicable_flag (bool): Capital gain discount applicable flag
        eofy_debt_interest_deduction_rate (float): EOFY debt interest deduction rate
        accountant (string): Accountant
        notes (string): Notes

    Returns:
        Standardized response with created fund tax statement data
    """
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
    """
    Delete a specific fund tax statement.

    Path Parameters:
        fund_id (int): ID of the fund (not used)
        fund_tax_statement_id (int): ID of the fund tax statement

    Returns:
        Standardized response with deleted fund tax statement
    """
    try:
        dto = fund_controller.delete_fund_tax_statement(fund_tax_statement_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting fund tax statement {fund_tax_statement_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()