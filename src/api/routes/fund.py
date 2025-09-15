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


@fund_bp.route('/api/funds/<int:fund_id>', methods=['GET'])
def fund_detail(fund_id):
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
        include_events = request.args.get('include_events', 'true').lower() == 'true'
        include_cash_flows = request.args.get('include_cash_flows', 'false').lower() == 'true'
        include_tax_statements = request.args.get('include_tax_statements', 'false').lower() == 'true'
        
        dto = fund_controller.get_fund(
            fund_id=fund_id,
            include_events=include_events,
            include_cash_flows=include_cash_flows,
            include_tax_statements=include_tax_statements
        )
        
        return handle_controller_response(dto)
    
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


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
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


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
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


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
        
        if event_type == 'CAPITAL_CALL':
            dto = fund_controller.add_capital_call(fund_id, validated_data)
        elif event_type == 'RETURN_OF_CAPITAL':
            dto = fund_controller.add_return_of_capital(fund_id, validated_data)
        elif event_type == 'UNIT_PURCHASE':
            dto = fund_controller.add_unit_purchase(fund_id, validated_data)
        elif event_type == 'UNIT_SALE':
            dto = fund_controller.add_unit_sale(fund_id, validated_data)
        elif event_type == 'NAV_UPDATE':
            dto = fund_controller.add_nav_update(fund_id, validated_data)
        elif event_type == 'DISTRIBUTION':
            dto = fund_controller.add_distribution(fund_id, validated_data)
        else:
            response = ApiResponse(
                response_code=ApiResponseCode.VALIDATION_ERROR,
                message=f'Unsupported event type: {event_type}'
            )
            return jsonify(response.to_dict()), response.response_code.get_http_status_code()
        
        return handle_controller_response(dto)
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


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
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


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
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


# Tax statement creation is now handled by the tax routes with middleware validation
# This duplicate route has been removed to eliminate duplication and use the centralized validation


@fund_bp.route('/api/funds/<int:fund_id>/tax-statements', methods=['GET'])
def get_fund_tax_statements(fund_id):
    """Get all tax statements for a specific fund"""
    try:
        from src.api.database import get_db_session
        session = get_db_session()
        
        try:
            # Validate fund exists
            fund_repository = FundRepository()
            fund = fund_repository.get_by_id(fund_id, session=session)
            if not fund:
                return jsonify({"error": "Fund not found"}), 404
            
            # Get tax statements for this fund
            tax_statements = session.query(TaxStatement).filter(
                TaxStatement.fund_id == fund_id
            ).order_by(TaxStatement.financial_year.desc()).all()
            
            tax_statements_data = []
            for statement in tax_statements:
                statement_data = {
                    "id": statement.id,
                    "fund_id": fund_id,
                    "entity_id": statement.entity_id,
                    "financial_year": statement.financial_year,
                    "statement_date": statement.statement_date.isoformat() if statement.statement_date else None,
                    "tax_payment_date": statement.get_tax_payment_date().isoformat() if statement.get_tax_payment_date() else None,
                    "eofy_debt_interest_deduction_rate": float(statement.eofy_debt_interest_deduction_rate) if statement.eofy_debt_interest_deduction_rate else None,
                    "interest_received_in_cash": float(statement.interest_received_in_cash) if statement.interest_received_in_cash else None,
                    "interest_receivable_this_fy": float(statement.interest_receivable_this_fy) if statement.interest_receivable_this_fy else None,
                    "interest_receivable_prev_fy": float(statement.interest_receivable_prev_fy) if statement.interest_receivable_prev_fy else None,
                    "interest_non_resident_withholding_tax_from_statement": float(statement.interest_non_resident_withholding_tax_from_statement) if statement.interest_non_resident_withholding_tax_from_statement else None,
                    "interest_income_tax_rate": float(statement.interest_income_tax_rate) if statement.interest_income_tax_rate else None,
                    "interest_income_amount": float(statement.interest_income_amount) if statement.interest_income_amount else None,
                    "interest_tax_amount": float(statement.interest_tax_amount) if statement.interest_tax_amount else None,
                    "dividend_franked_income_amount": float(statement.dividend_franked_income_amount) if statement.dividend_franked_income_amount else None,
                    "dividend_franked_income_tax_rate": float(statement.dividend_franked_income_tax_rate) if statement.dividend_franked_income_tax_rate else None,
                    "dividend_unfranked_income_amount": float(statement.dividend_unfranked_income_amount) if statement.dividend_unfranked_income_amount else None,
                    "dividend_unfranked_income_tax_rate": float(statement.dividend_unfranked_income_tax_rate) if statement.dividend_unfranked_income_tax_rate else None,
                    "capital_gain_income_amount": float(statement.capital_gain_income_amount) if statement.capital_gain_income_amount else None,
                    "capital_gain_income_tax_rate": float(statement.capital_gain_income_tax_rate) if statement.capital_gain_income_tax_rate else None,
                    "created_at": statement.created_at.isoformat() if statement.created_at else None,
                    "updated_at": statement.updated_at.isoformat() if statement.updated_at else None
                }
                tax_statements_data.append(statement_data)
            
            return jsonify({"tax_statements": tax_statements_data}), 200
            
        finally:
            session.close()
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@fund_bp.route('/api/funds/<int:fund_id>/events/<int:event_id>/cash-flows', methods=['GET'])
def get_fund_event_cash_flows(fund_id, event_id):
    """Get all cash flows for a specific fund event"""
    try:
        from src.api.database import get_db_session
        session = get_db_session()
        
        try:
            # Validate fund exists
            fund_repository = FundRepository()
            fund = fund_repository.get_by_id(fund_id, session=session)
            if not fund:
                return jsonify({"error": "Fund not found"}), 404
            
            # Validate event exists and belongs to fund
            event = session.query(FundEvent).filter(
                FundEvent.id == event_id,
                FundEvent.fund_id == fund_id
            ).first()
            
            if not event:
                return jsonify({"error": "Fund event not found"}), 404
            
            cash_flows_data = []
            for cf in event.cash_flows:
                cf_data = {
                    "id": cf.id,
                    "bank_account_id": cf.bank_account_id,
                    "bank_name": cf.bank_account.bank.name,
                    "account_name": cf.bank_account.account_name,
                    "direction": cf.direction.value,
                    "transfer_date": cf.transfer_date.isoformat(),
                    "currency": cf.currency,
                    "amount": float(cf.amount),
                    "reference": cf.reference,
                    "notes": cf.notes
                }
                cash_flows_data.append(cf_data)
            
            response_data = {
                "fund_id": fund_id,
                "event_id": event_id,
                "event_type": event.event_type.value,
                "event_date": event.event_date.isoformat(),
                "event_amount": float(event.amount) if event.amount else None,
                "is_cash_flow_complete": event.is_cash_flow_complete,
                "cash_flows": cash_flows_data
            }
            
            return jsonify(response_data), 200
            
        finally:
            session.close()
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@fund_bp.route('/api/funds/<int:fund_id>/events/<int:event_id>/cash-flows', methods=['POST'])
@validate_cash_flow_data
def add_fund_event_cash_flow(fund_id, event_id):
    """Add a cash flow to a fund event"""
    try:
        from src.api.controllers.fund_controller import FundController
        controller = FundController()
        # Use validated data from middleware
        validated_data = request.validated_data
        return controller.add_cash_flow_to_event(fund_id, event_id, validated_data)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@fund_bp.route('/api/funds/<int:fund_id>/events/<int:event_id>/cash-flows/<int:cash_flow_id>', methods=['DELETE'])
def remove_fund_event_cash_flow(fund_id, event_id, cash_flow_id):
    """Remove a cash flow from a fund event"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Validate fund exists
            fund_repository = FundRepository()
            fund = fund_repository.get_by_id(fund_id, session=session)
            if not fund:
                return jsonify({"error": "Fund not found"}), 404
            
            # Validate event exists and belongs to fund
            event = session.query(FundEvent).filter(
                FundEvent.id == event_id,
                FundEvent.fund_id == fund_id
            ).first()
            
            if not event:
                return jsonify({"error": "Fund event not found"}), 404
            
            # Remove cash flow using domain method
            event.remove_cash_flow(cash_flow_id, session=session)
            session.commit()
            
            return jsonify({"message": "Cash flow removed successfully"}), 200
            
        finally:
            session.close()
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@fund_bp.route('/api/cash-flows', methods=['GET'])
def get_cash_flows():
    """Get cash flows with optional filtering"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Get query parameters for filtering
            fund_id = request.args.get('fund_id', type=int)
            bank_account_id = request.args.get('bank_account_id', type=int)
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            currency = request.args.get('currency')
            
            query = session.query(FundEventCashFlow).join(FundEvent)
            
            # Apply filters
            if fund_id:
                query = query.filter(FundEvent.fund_id == fund_id)
            if bank_account_id:
                query = query.filter(FundEventCashFlow.bank_account_id == bank_account_id)
            if currency:
                query = query.filter(FundEventCashFlow.currency == currency.upper())
            
            # Date filtering
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                    query = query.filter(FundEventCashFlow.transfer_date >= start_dt)
                except ValueError:
                    response = ApiResponse(
                        response_code=ApiResponseCode.VALIDATION_ERROR,
                        message="Invalid start_date format. Use YYYY-MM-DD"
                    )
                    return jsonify(response.to_dict()), response.response_code.get_http_status_code()
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                    query = query.filter(FundEventCashFlow.transfer_date <= end_dt)
                except ValueError:
                    response = ApiResponse(
                        response_code=ApiResponseCode.VALIDATION_ERROR,
                        message="Invalid end_date format. Use YYYY-MM-DD"
                    )
                    return jsonify(response.to_dict()), response.response_code.get_http_status_code()
            
            cash_flows = query.order_by(FundEventCashFlow.transfer_date.desc()).all()
            
            flows_data = []
            for cf in cash_flows:
                cf_data = {
                    "id": cf.id,
                    "fund_event_id": cf.fund_event_id,
                    "fund_id": cf.fund_event.fund_id,
                    "fund_name": cf.fund_event.fund.name,
                    "event_type": cf.fund_event.event_type.value,
                    "event_date": cf.fund_event.event_date.isoformat(),
                    "bank_account_id": cf.bank_account_id,
                    "bank_name": cf.bank_account.bank.name,
                    "account_name": cf.bank_account.account_name,
                    "direction": cf.direction.value,
                    "transfer_date": cf.transfer_date.isoformat(),
                    "currency": cf.currency,
                    "amount": float(cf.amount),
                    "reference": cf.reference,
                    "notes": cf.notes
                }
                flows_data.append(cf_data)
            
            return jsonify({"cash_flows": flows_data}), 200
            
        finally:
            session.close()
            
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()