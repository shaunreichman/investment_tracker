"""
Fund API Routes.

This module contains all fund-related API endpoints including
fund management, fund events, tax statements, and cash flows.

All endpoints use middleware validation for input data.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload
from datetime import datetime, date
from src.fund.models import Fund, FundEvent, FundEventCashFlow
from src.fund.enums import FundStatus, FundType, EventType, CashFlowDirection
from src.entity.models import Entity
from src.banking.models import BankAccount
from src.tax.models import TaxStatement
from src.fund.repositories import FundRepository
from src.api.middleware.validation import validate_fund_data, validate_fund_event_data, validate_cash_flow_data

# Create blueprint for fund routes
fund_bp = Blueprint('fund', __name__)


@fund_bp.route('/api/funds/<int:fund_id>', methods=['GET'])
def fund_detail(fund_id):
    """Get detailed information about a specific fund"""
    try:
        from src.api.database import get_db_session
        session = get_db_session()
        
        try:
            # Use repository to get fund
            fund_repository = FundRepository()
            fund = fund_repository.get_by_id(fund_id, session=session)
            
            if not fund:
                return jsonify({"error": "Fund not found"}), 404
            
            # Get fund summary data using domain methods
            fund_data = fund.get_summary_data(session=session)
            
            # Get all events using domain methods (excluding system events)
            all_events = fund.get_all_fund_events(exclude_system_events=True, session=session)
            
            events_data = []
            for event in all_events:
                event_data = {
                    "id": event.id,
                    "event_type": event.event_type.value.upper() if event.event_type else None,
                    "event_date": event.event_date.isoformat() if event.event_date else None,
                    "amount": float(event.amount) if event.amount else None,
                    "description": event.description,
                    "reference_number": event.reference_number,
                    "distribution_type": event.distribution_type.value.upper() if event.distribution_type else None,
                    "tax_payment_type": event.tax_payment_type.value.upper() if event.tax_payment_type else None,
                    "units_owned": float(event.units_owned) if event.units_owned else None,
                    "units_purchased": float(event.units_purchased) if event.units_purchased else None,
                    "units_sold": float(event.units_sold) if event.units_sold else None,
                    "unit_price": float(event.unit_price) if event.unit_price else None,
                    "nav_per_share": float(event.nav_per_share) if event.nav_per_share else None,
                    "previous_nav_per_share": float(event.previous_nav_per_share) if event.previous_nav_per_share else None,
                    "nav_change_absolute": float(event.nav_change_absolute) if event.nav_change_absolute else None,
                    "nav_change_percentage": float(event.nav_change_percentage) if event.nav_change_percentage else None,
                    "brokerage_fee": float(event.brokerage_fee) if event.brokerage_fee else None,
                    "tax_withholding": float(event.tax_withholding) if event.tax_withholding else None,
                    "has_withholding_tax": bool(event.has_withholding_tax) if event.has_withholding_tax is not None else None,
                    "created_at": event.created_at.isoformat() if event.created_at else None,
                    # CALCULATED: Grouping flags set by backend when creating events
                    "is_grouped": bool(event.is_grouped) if event.is_grouped is not None else False,
                    "group_id": event.group_id,
                    "group_type": event.group_type.value if event.group_type else None,
                    "group_position": event.group_position
                }
                
                # Add tax statement fields for TAX_PAYMENT and EOFY_DEBT_COST events
                if event.event_type.value in ['TAX_PAYMENT', 'EOFY_DEBT_COST'] and event.tax_statement_id:
                    tax_statement = session.query(TaxStatement).filter(TaxStatement.id == event.tax_statement_id).first()
                    if tax_statement:
                        # Add tax statement fields for TAX_PAYMENT events
                        if event.event_type.value == 'TAX_PAYMENT':
                            event_data.update({
                                "interest_income_amount": float(tax_statement.interest_income_amount) if tax_statement.interest_income_amount else None,
                                "interest_income_tax_rate": float(tax_statement.interest_income_tax_rate) if tax_statement.interest_income_tax_rate else None,
                                "dividend_franked_income_amount": float(tax_statement.dividend_franked_income_amount) if tax_statement.dividend_franked_income_amount else None,
                                "dividend_franked_income_tax_rate": float(tax_statement.dividend_franked_income_tax_rate) if tax_statement.dividend_franked_income_tax_rate else None,
                                "dividend_unfranked_income_amount": float(tax_statement.dividend_unfranked_income_amount) if tax_statement.dividend_unfranked_income_amount else None,
                                "dividend_unfranked_income_tax_rate": float(tax_statement.dividend_unfranked_income_tax_rate) if tax_statement.dividend_unfranked_income_tax_rate else None,
                                "capital_gain_income_amount": float(tax_statement.capital_gain_income_amount) if tax_statement.capital_gain_income_amount else None,
                                "capital_gain_income_tax_rate": float(tax_statement.capital_gain_income_tax_rate) if tax_statement.capital_gain_income_tax_rate else None,
                            })
                        # Add tax statement fields for EOFY_DEBT_COST events
                        elif event.event_type.value == 'eofy_debt_cost':
                            event_data.update({
                                "eofy_debt_interest_deduction_sum_of_daily_interest": float(tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest) if tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest else None,
                                "eofy_debt_interest_deduction_rate": float(tax_statement.eofy_debt_interest_deduction_rate) if tax_statement.eofy_debt_interest_deduction_rate else None,
                                "eofy_debt_interest_deduction_total_deduction": float(tax_statement.eofy_debt_interest_deduction_total_deduction) if tax_statement.eofy_debt_interest_deduction_total_deduction else None,
                            })
                
                events_data.append(event_data)
            
            # Get tax statements for this fund
            tax_statements = session.query(TaxStatement).filter(
                TaxStatement.fund_id == fund_id
            ).order_by(TaxStatement.financial_year.desc()).all()
            
            tax_statements_data = []
            for statement in tax_statements:
                statement_data = {
                    "id": statement.id,
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
            
            # Combine all data
            response_data = {
                "fund": fund_data,
                "events": events_data,
                "statistics": {
                    # Add any additional statistics that might be needed
                    "total_events": len(events_data),
                    "total_tax_statements": len(tax_statements_data)
                }
            }
            
            return jsonify(response_data), 200
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fund_bp.route('/api/funds', methods=['POST'])
@validate_fund_data
def create_fund():
    """Create a new fund using the new FundController architecture"""
    try:
        from src.api.controllers.fund_controller import FundController
        controller = FundController()
        return controller.create_fund()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fund_bp.route('/api/funds/<int:fund_id>', methods=['DELETE'])
def delete_fund(fund_id):
    """Delete a fund using enterprise validation"""
    try:
        from src.api.controllers.fund_controller import FundController
        controller = FundController()
        return controller.delete_fund(fund_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fund_bp.route('/api/funds/<int:fund_id>/events', methods=['POST'])
@validate_fund_event_data
def create_fund_event(fund_id):
    """Create a new fund event using the new FundController architecture"""
    try:
        from src.api.controllers.fund_controller import FundController
        from src.api.database import get_db_session
        
        # Create database session
        session = get_db_session()
        
        try:
            controller = FundController()
            # Use validated data from middleware
            validated_data = request.validated_data
            return controller.add_fund_event_with_data(fund_id, validated_data, session)
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@fund_bp.route('/api/funds/<int:fund_id>/events/<int:event_id>', methods=['DELETE'])
def delete_fund_event(fund_id, event_id):
    """Delete a specific fund event using the new FundController architecture"""
    try:
        from src.api.controllers.fund_controller import FundController
        controller = FundController()
        return controller.delete_fund_event(fund_id, event_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


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
                    return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                    query = query.filter(FundEventCashFlow.transfer_date <= end_dt)
                except ValueError:
                    return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
            
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
        return jsonify({"error": str(e)}), 500
