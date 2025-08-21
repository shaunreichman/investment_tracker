"""
Fund API Routes.

This module contains all fund-related API endpoints including
fund management, fund events, tax statements, and cash flows.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload
from datetime import datetime, date
from src.fund.models import Fund, FundEvent, FundEventCashFlow
from src.fund.enums import FundStatus, FundType, EventType, CashFlowDirection
from src.entity.models import Entity
from src.banking.models import BankAccount
from src.tax.models import TaxStatement

# Create blueprint for fund routes
fund_bp = Blueprint('fund', __name__)


@fund_bp.route('/api/funds/<int:fund_id>', methods=['GET'])
def fund_detail(fund_id):
    """Get detailed information about a specific fund"""
    try:
        from src.api.database import get_db_session
        session = get_db_session()
        
        try:
            # Use domain methods to get fund
            fund = Fund.get_by_id(fund_id, session=session)
            
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
                    "units_purchased": float(event.units_purchased) if event.units_purchased else None,
                    "units_sold": float(event.units_sold) if event.units_sold else None,
                    "unit_price": float(event.unit_price) if event.unit_price else None,
                    "nav_per_share": float(event.nav_per_share) if event.nav_per_share else None,
                    "previous_nav_per_share": float(event.previous_nav_per_share) if event.previous_nav_per_share else None,
                    "nav_change_absolute": float(event.nav_change_absolute) if event.nav_change_absolute else None,
                    "nav_change_percentage": float(event.nav_change_percentage) if event.nav_change_percentage else None,
                    "brokerage_fee": float(event.brokerage_fee) if event.brokerage_fee else None,
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
                **fund_data,
                "events": events_data,
                "tax_statements": tax_statements_data
            }
            
            return jsonify(response_data), 200
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fund_bp.route('/api/funds', methods=['POST'])
def create_fund():
    """Create a new fund using the new FundController architecture"""
    try:
        from src.fund.api import FundController
        controller = FundController()
        return controller.create_fund()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fund_bp.route('/api/funds/<int:fund_id>/events', methods=['POST'])
def create_fund_event(fund_id):
    """Create a new fund event using the new FundController architecture"""
    try:
        from src.fund.api import FundController
        controller = FundController()
        return controller.add_fund_event(fund_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@fund_bp.route('/api/funds/<int:fund_id>/events/<int:event_id>', methods=['DELETE'])
def delete_fund_event(fund_id, event_id):
    """Delete a specific fund event using the new FundController architecture"""
    try:
        from src.fund.api import FundController
        controller = FundController()
        return controller.delete_fund_event(fund_id, event_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fund_bp.route('/api/funds/<int:fund_id>/tax-statements', methods=['POST'])
def create_tax_statement(fund_id):
    """Create a new tax statement for a fund"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Get fund and validate it exists
            fund = Fund.get_by_id(fund_id, session=session)
            if not fund:
                return jsonify({"error": "Fund not found"}), 404
            
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Extract required fields
            entity_id = data.get('entity_id')
            financial_year = data.get('financial_year')
            statement_date = data.get('statement_date')
            eofy_debt_interest_deduction_rate = data.get('eofy_debt_interest_deduction_rate')
            
            # Validate required fields
            if not entity_id:
                return jsonify({"error": "Entity ID is required"}), 400
            if not financial_year:
                return jsonify({"error": "Financial year is required"}), 400
            if not statement_date:
                return jsonify({"error": "Statement date is required"}), 400
            if eofy_debt_interest_deduction_rate is None:
                return jsonify({"error": "End of financial year debt interest deduction rate is required"}), 400
            
            # Validate entity exists
            entity = session.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                return jsonify({"error": "Entity not found"}), 404
            
            # Parse statement date
            try:
                if isinstance(statement_date, str):
                    statement_date = datetime.strptime(statement_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid statement date format. Use YYYY-MM-DD"}), 400
            
            # Validate numeric fields
            numeric_fields = [
                'eofy_debt_interest_deduction_rate',
                'interest_received_in_cash',
                'interest_receivable_this_fy',
                'interest_receivable_prev_fy',
                'interest_non_resident_withholding_tax_from_statement',
                'interest_income_tax_rate',
                'dividend_franked_income_amount',
                'dividend_unfranked_income_amount',
                'dividend_franked_income_tax_rate',
                'dividend_unfranked_income_tax_rate',
                'capital_gain_income_amount',
                'capital_gain_income_tax_rate'
            ]
            
            for field in numeric_fields:
                if field in data and data[field] is not None:
                    try:
                        float(data[field])
                    except (ValueError, TypeError):
                        return jsonify({"error": f"Invalid numeric value for {field}"}), 400
            
            # Create tax statement using domain method
            tax_statement = fund.create_tax_statement(
                entity_id=entity_id,
                financial_year=financial_year,
                statement_date=statement_date,
                eofy_debt_interest_deduction_rate=float(eofy_debt_interest_deduction_rate),
                interest_received_in_cash=data.get('interest_received_in_cash'),
                interest_receivable_this_fy=data.get('interest_receivable_this_fy'),
                interest_receivable_prev_fy=data.get('interest_receivable_prev_fy'),
                interest_non_resident_withholding_tax_from_statement=data.get('interest_non_resident_withholding_tax_from_statement'),
                interest_income_tax_rate=data.get('interest_income_tax_rate'),
                interest_income_amount=data.get('interest_income_amount'),
                interest_tax_amount=data.get('interest_tax_amount'),
                dividend_franked_income_amount=data.get('dividend_franked_income_amount'),
                dividend_franked_income_tax_rate=data.get('dividend_franked_income_tax_rate'),
                dividend_unfranked_income_amount=data.get('dividend_unfranked_income_amount'),
                dividend_unfranked_income_tax_rate=data.get('dividend_unfranked_income_tax_rate'),
                capital_gain_income_amount=data.get('capital_gain_income_amount'),
                capital_gain_income_tax_rate=data.get('capital_gain_income_tax_rate'),
                session=session
            )
            
            session.commit()
            
            # Return created tax statement
            response_data = {
                "id": tax_statement.id,
                "fund_id": fund_id,
                "entity_id": tax_statement.entity_id,
                "financial_year": tax_statement.financial_year,
                "statement_date": tax_statement.statement_date.isoformat() if tax_statement.statement_date else None,
                "eofy_debt_interest_deduction_rate": float(tax_statement.eofy_debt_interest_deduction_rate) if tax_statement.eofy_debt_interest_deduction_rate else None,
                "interest_received_in_cash": float(tax_statement.interest_received_in_cash) if tax_statement.interest_received_in_cash else None,
                "interest_receivable_this_fy": float(tax_statement.interest_receivable_this_fy) if tax_statement.interest_receivable_this_fy else None,
                "interest_receivable_prev_fy": float(tax_statement.interest_receivable_prev_fy) if tax_statement.interest_receivable_prev_fy else None,
                "interest_non_resident_withholding_tax_from_statement": float(tax_statement.interest_non_resident_withholding_tax_from_statement) if tax_statement.interest_non_resident_withholding_tax_from_statement else None,
                "interest_income_tax_rate": float(tax_statement.interest_income_tax_rate) if tax_statement.interest_income_tax_rate else None,
                "interest_income_amount": float(tax_statement.interest_income_amount) if tax_statement.interest_income_amount else None,
                "interest_tax_amount": float(tax_statement.interest_tax_amount) if tax_statement.interest_tax_amount else None,
                "dividend_franked_income_amount": float(tax_statement.dividend_franked_income_amount) if tax_statement.dividend_franked_income_amount else None,
                "dividend_franked_income_tax_rate": float(tax_statement.dividend_franked_income_tax_rate) if tax_statement.dividend_franked_income_tax_rate else None,
                "dividend_unfranked_income_amount": float(tax_statement.dividend_unfranked_income_amount) if tax_statement.dividend_unfranked_income_amount else None,
                "dividend_unfranked_income_tax_rate": float(tax_statement.dividend_unfranked_income_tax_rate) if tax_statement.dividend_unfranked_income_tax_rate else None,
                "capital_gain_income_amount": float(tax_statement.capital_gain_income_amount) if tax_statement.capital_gain_income_amount else None,
                "capital_gain_income_tax_rate": float(tax_statement.capital_gain_income_tax_rate) if tax_statement.capital_gain_income_tax_rate else None,
                "created_at": tax_statement.created_at.isoformat() if tax_statement.created_at else None,
                "updated_at": tax_statement.updated_at.isoformat() if tax_statement.updated_at else None
            }
            
            return jsonify(response_data), 201
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fund_bp.route('/api/funds/<int:fund_id>/tax-statements', methods=['GET'])
def get_fund_tax_statements(fund_id):
    """Get all tax statements for a specific fund"""
    try:
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Validate fund exists
            fund = Fund.get_by_id(fund_id, session=session)
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
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Validate fund exists
            fund = Fund.get_by_id(fund_id, session=session)
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
def add_fund_event_cash_flow(fund_id, event_id):
    """Add a cash flow to a fund event"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['bank_account_id', 'transfer_date', 'currency', 'amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        from src.api import get_db_session
        session = get_db_session()
        
        try:
            # Validate fund exists
            fund = Fund.get_by_id(fund_id, session=session)
            if not fund:
                return jsonify({"error": "Fund not found"}), 404
            
            # Validate event exists and belongs to fund
            event = session.query(FundEvent).filter(
                FundEvent.id == event_id,
                FundEvent.fund_id == fund_id
            ).first()
            
            if not event:
                return jsonify({"error": "Fund event not found"}), 404
            
            # Validate bank account exists
            bank_account = session.query(BankAccount).filter(BankAccount.id == data['bank_account_id']).first()
            if not bank_account:
                return jsonify({"error": "Bank account not found"}), 404
            
            # Validate currency matches bank account
            if data['currency'].upper() != bank_account.currency.upper():
                return jsonify({"error": "Cash flow currency must match bank account currency"}), 400
            
            # Parse transfer date
            try:
                transfer_date = datetime.strptime(data['transfer_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid transfer_date format. Use YYYY-MM-DD"}), 400
            
            # Add cash flow using domain method
            cash_flow = event.add_cash_flow(
                bank_account_id=data['bank_account_id'],
                transfer_date=transfer_date,
                currency=data['currency'],
                amount=float(data['amount']),
                reference=data.get('reference'),
                notes=data.get('notes'),
                session=session
            )
            
            session.commit()
            
            response_data = {
                "id": cash_flow.id,
                "fund_event_id": cash_flow.fund_event_id,
                "bank_account_id": cash_flow.bank_account_id,
                "bank_name": bank_account.bank.name,
                "account_name": bank_account.account_name,
                "direction": cash_flow.direction.value,
                "transfer_date": cash_flow.transfer_date.isoformat(),
                "currency": cash_flow.currency,
                "amount": float(cash_flow.amount),
                "reference": cash_flow.reference,
                "notes": cash_flow.notes,
                "message": "Cash flow added successfully"
            }
            
            return jsonify(response_data), 201
            
        finally:
            session.close()
            
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
            fund = Fund.get_by_id(fund_id, session=session)
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
