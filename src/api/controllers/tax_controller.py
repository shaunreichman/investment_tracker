"""
Tax API Controller.

This controller handles HTTP requests for tax operations,
providing RESTful endpoints for tax statement management.

Key responsibilities:
- Tax statement CRUD endpoints
- Tax validation and error handling
- Input sanitization and type validation
"""

from typing import List, Optional, Dict, Any
from flask import request, jsonify, current_app
from sqlalchemy.orm import Session
from datetime import datetime

from src.tax.models import TaxStatement
from src.fund.models import Fund
from src.entity.models import Entity


class TaxController:
    """
    Controller for tax operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for tax operations. It delegates business logic to the domain
    models and handles request/response formatting.
    
    Attributes:
        None - Direct domain model usage for simplicity
    """
    
    def __init__(self):
        """Initialize the tax controller."""
        pass
    
    def create_tax_statement(self, session: Session, fund_id: int) -> tuple:
        """
        Create a new tax statement for a fund.
        
        Args:
            session: Database session
            fund_id: ID of the fund to create tax statement for
            
        Returns:
            Tuple of (response_data, status_code)
        """
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
                value = data.get(field)
                if value is not None:
                    try:
                        float_value = float(value)
                        if float_value < 0:
                            return jsonify({"error": f"{field.replace('_', ' ').title()} must be non-negative"}), 400
                        data[field] = float_value
                    except (ValueError, TypeError):
                        return jsonify({"error": f"{field.replace('_', ' ').title()} must be a valid number"}), 400
            
            # Validate percentage fields (0-100%)
            percentage_fields = [
                'eofy_debt_interest_deduction_rate',
                'interest_income_tax_rate',
                'dividend_franked_income_tax_rate',
                'dividend_unfranked_income_tax_rate',
                'capital_gain_income_tax_rate'
            ]
            
            for field in percentage_fields:
                value = data.get(field)
                if value is not None:
                    if not (0 <= float(value) <= 100):
                        return jsonify({"error": f"{field.replace('_', ' ').title()} must be between 0 and 100"}), 400
            
            # Check for existing tax statement
            existing_statement = session.query(TaxStatement).filter(
                TaxStatement.fund_id == fund_id,
                TaxStatement.entity_id == entity_id,
                TaxStatement.financial_year == financial_year
            ).first()
            
            if existing_statement:
                return jsonify({"error": "Tax statement already exists for this fund, entity, and financial year"}), 409
            
            # Create tax statement
            tax_statement = TaxStatement(
                fund_id=fund_id,
                entity_id=entity_id,
                financial_year=financial_year,
                statement_date=statement_date,
                eofy_debt_interest_deduction_rate=data.get('eofy_debt_interest_deduction_rate'),
                interest_received_in_cash=data.get('interest_received_in_cash'),
                interest_receivable_this_fy=data.get('interest_receivable_this_fy'),
                interest_receivable_prev_fy=data.get('interest_receivable_prev_fy'),
                interest_non_resident_withholding_tax_from_statement=data.get('interest_non_resident_withholding_tax_from_statement'),
                interest_income_tax_rate=data.get('interest_income_tax_rate'),
                dividend_franked_income_amount=data.get('dividend_franked_income_amount'),
                dividend_unfranked_income_amount=data.get('dividend_unfranked_income_amount'),
                dividend_franked_income_tax_rate=data.get('dividend_franked_income_tax_rate'),
                dividend_unfranked_income_tax_rate=data.get('dividend_unfranked_income_tax_rate'),
                capital_gain_income_amount=data.get('capital_gain_income_amount'),
                capital_gain_income_tax_rate=data.get('capital_gain_income_tax_rate'),
                non_resident=data.get('non_resident', False),
                accountant=data.get('accountant'),
                notes=data.get('notes')
            )
            
            session.add(tax_statement)
            session.commit()
            
            # Return created tax statement data
            response_data = {
                "id": tax_statement.id,
                "fund_id": tax_statement.fund_id,
                "entity_id": tax_statement.entity_id,
                "financial_year": tax_statement.financial_year,
                "statement_date": tax_statement.statement_date.isoformat() if tax_statement.statement_date else None,
                "tax_payment_date": tax_statement.get_tax_payment_date().isoformat() if tax_statement.get_tax_payment_date() else None,
                "eofy_debt_interest_deduction_rate": float(tax_statement.eofy_debt_interest_deduction_rate) if tax_statement.eofy_debt_interest_deduction_rate else None,
                "interest_received_in_cash": float(tax_statement.interest_received_in_cash) if tax_statement.interest_received_in_cash else None,
                "interest_receivable_this_fy": float(tax_statement.interest_receivable_this_fy) if tax_statement.interest_receivable_this_fy else None,
                "interest_receivable_prev_fy": float(tax_statement.interest_receivable_prev_fy) if tax_statement.interest_receivable_prev_fy else None,
                "interest_non_resident_withholding_tax_from_statement": float(tax_statement.interest_non_resident_withholding_tax_from_statement) if tax_statement.interest_non_resident_withholding_tax_from_statement else None,
                "interest_income_tax_rate": float(tax_statement.interest_income_tax_rate) if tax_statement.interest_income_tax_rate else None,
                "interest_income_amount": float(tax_statement.interest_income_amount) if tax_statement.interest_income_amount else None,
                "interest_tax_amount": float(tax_statement.interest_tax_amount) if tax_statement.interest_tax_amount else None,
                "dividend_franked_income_amount": float(tax_statement.dividend_franked_income_amount) if tax_statement.dividend_franked_income_amount else None,
                "dividend_unfranked_income_amount": float(tax_statement.dividend_unfranked_income_amount) if tax_statement.dividend_unfranked_income_amount else None,
                "dividend_franked_income_tax_rate": float(tax_statement.dividend_franked_income_tax_rate) if tax_statement.dividend_franked_income_tax_rate else None,
                "dividend_unfranked_income_tax_rate": float(tax_statement.dividend_unfranked_income_tax_rate) if tax_statement.dividend_unfranked_income_tax_rate else None,
                "dividend_franked_tax_amount": float(tax_statement.dividend_franked_tax_amount) if tax_statement.dividend_franked_tax_amount else None,
                "dividend_unfranked_tax_amount": float(tax_statement.dividend_unfranked_tax_amount) if tax_statement.dividend_unfranked_tax_amount else None,
                "capital_gain_income_amount": float(tax_statement.capital_gain_income_amount) if tax_statement.capital_gain_income_amount else None,
                "capital_gain_income_tax_rate": float(tax_statement.capital_gain_income_tax_rate) if tax_statement.capital_gain_income_tax_rate else None,
                "capital_gain_tax_amount": float(tax_statement.capital_gain_tax_amount) if tax_statement.capital_gain_tax_amount else None,
                "eofy_debt_interest_deduction_sum_of_daily_interest": float(tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest) if tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest else None,
                "eofy_debt_interest_deduction_total_deduction": float(tax_statement.eofy_debt_interest_deduction_total_deduction) if tax_statement.eofy_debt_interest_deduction_total_deduction else None,
                "non_resident": tax_statement.non_resident,
                "accountant": tax_statement.accountant,
                "notes": tax_statement.notes,
                "created_at": tax_statement.created_at.isoformat() if tax_statement.created_at else None,
                "updated_at": tax_statement.updated_at.isoformat() if tax_statement.updated_at else None
            }
            
            return jsonify(response_data), 201
            
        except Exception as e:
            current_app.logger.error(f"Error creating tax statement: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_fund_tax_statements(self, session: Session, fund_id: int) -> tuple:
        """
        Get all tax statements for a fund.
        
        Args:
            session: Database session
            fund_id: ID of the fund to get tax statements for
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get fund and validate it exists
            fund = Fund.get_by_id(fund_id, session=session)
            if not fund:
                return jsonify({"error": "Fund not found"}), 404
            
            # Get tax statements for this fund
            tax_statements = session.query(TaxStatement).filter(
                TaxStatement.fund_id == fund_id
            ).order_by(TaxStatement.financial_year.desc()).all()
            
            statements_data = []
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
                    "dividend_unfranked_income_amount": float(statement.dividend_unfranked_income_amount) if statement.dividend_unfranked_income_amount else None,
                    "dividend_franked_income_tax_rate": float(statement.dividend_franked_income_tax_rate) if statement.dividend_franked_income_tax_rate else None,
                    "dividend_unfranked_income_tax_rate": float(statement.dividend_unfranked_income_tax_rate) if statement.dividend_unfranked_income_tax_rate else None,
                    "dividend_franked_tax_amount": float(statement.dividend_franked_tax_amount) if statement.dividend_franked_tax_amount else None,
                    "dividend_unfranked_tax_amount": float(statement.dividend_unfranked_tax_amount) if statement.dividend_unfranked_tax_amount else None,
                    "capital_gain_income_amount": float(statement.capital_gain_income_amount) if statement.capital_gain_income_amount else None,
                    "capital_gain_income_tax_rate": float(statement.capital_gain_income_tax_rate) if statement.capital_gain_income_tax_rate else None,
                    "capital_gain_tax_amount": float(statement.capital_gain_tax_amount) if statement.capital_gain_tax_amount else None,
                    "eofy_debt_interest_deduction_sum_of_daily_interest": float(statement.eofy_debt_interest_deduction_sum_of_daily_interest) if statement.eofy_debt_interest_deduction_sum_of_daily_interest else None,
                    "eofy_debt_interest_deduction_total_deduction": float(statement.eofy_debt_interest_deduction_total_deduction) if statement.eofy_debt_interest_deduction_total_deduction else None,
                    "non_resident": statement.non_resident,
                    "accountant": statement.accountant,
                    "notes": statement.notes,
                    "created_at": statement.created_at.isoformat() if statement.created_at else None,
                    "updated_at": statement.updated_at.isoformat() if statement.updated_at else None
                }
                statements_data.append(statement_data)
            
            return jsonify({"tax_statements": statements_data}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting fund tax statements: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
