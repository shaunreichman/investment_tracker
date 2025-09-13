"""
Tax API Controller.

This controller handles HTTP requests for tax operations,
providing RESTful endpoints for tax statement management.

Key responsibilities:
- Tax statement CRUD endpoints
- Business logic delegation to domain models
- Response formatting and error handling

Note: All input validation is handled by middleware validation decorators.
"""

from typing import List, Optional, Dict, Any
from flask import request, jsonify, current_app
from sqlalchemy.orm import Session
from datetime import datetime

from src.tax.models import TaxStatement
from src.fund.models import Fund
from src.entity.models import Entity
from src.fund.enums import SortOrder


class TaxController:
    """
    Controller for tax operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for tax operations. It delegates business logic to the domain
    models and handles request/response formatting.
    
    All input validation is handled by middleware validation decorators.
    
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
            
        Note: Input data is pre-validated by middleware validation decorator.
        """
        try:
            # Get fund and validate it exists
            from src.fund.repositories.fund_repository import FundRepository
            fund = FundRepository().get_by_id(fund_id, session=session)
            
            if not fund:
                return jsonify({"error": "Fund not found"}), 404
            
            # Get pre-validated data from middleware
            data = getattr(request, 'validated_data', {})
            if not data:
                return jsonify({"error": "No validated data available"}), 400
            
            # Extract validated fields
            entity_id = data['entity_id']
            financial_year = data['financial_year']
            statement_date = data['statement_date']
            eofy_debt_interest_deduction_rate = data['eofy_debt_interest_deduction_rate']
            
            # Validate entity exists
            entity = session.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                return jsonify({"error": "Entity not found"}), 404
            
            # Check for existing tax statement
            existing_statement = session.query(TaxStatement).filter(
                TaxStatement.fund_id == fund_id,
                TaxStatement.entity_id == entity_id,
                TaxStatement.financial_year == financial_year
            ).first()
            
            if existing_statement:
                return jsonify({"error": "Tax statement already exists for this fund, entity, and financial year"}), 409
            
            # Create tax statement with validated data
            tax_statement = TaxStatement(
                fund_id=fund_id,
                entity_id=entity_id,
                financial_year=financial_year,
                statement_date=statement_date,
                eofy_debt_interest_deduction_rate=eofy_debt_interest_deduction_rate,
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
            
            # Calculate derived fields
            interest_income = tax_statement.calculate_interest_income_amount(session)
            dividend_totals = tax_statement.calculate_dividend_totals(session)
            capital_gain_total = tax_statement.calculate_capital_gain_totals(session)
            
            session.add(tax_statement)
            session.commit()
            
            # Create tax payment events for this tax statement
            try:
                created_events = tax_statement.create_tax_payment_events(session)
            except Exception as e:
                current_app.logger.error(f"Error creating tax payment events: {str(e)}")
                # Don't fail the entire request if tax payment events fail to create
            
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
            # Get fund using repository pattern (no direct database queries)
            from src.fund.repositories.fund_repository import FundRepository
            fund = FundRepository().get_by_id(fund_id, session=session)
            if not fund:
                return jsonify({"error": "Fund not found"}), 404
            
            # Get tax statements for this fund using repository pattern
            from src.fund.repositories.tax_statement_repository import TaxStatementRepository
            tax_statements = TaxStatementRepository().get_by_fund(fund_id, session=session, sort_order=SortOrder.DESC)
            
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
    
    def get_fund_financial_years(self, session: Session, fund_id: int) -> tuple:
        """
        Get all financial years from fund start date to current date.
        
        Args:
            session: Database session
            fund_id: ID of the fund to get financial years for
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get fund using repository pattern (no direct database queries)
            from src.fund.repositories.fund_repository import FundRepository
            fund = FundRepository().get_by_id(fund_id, session=session)
            if not fund:
                return jsonify({"error": "Fund not found"}), 404
            
            from src.fund.services.fund_date_service import FundDateService
            fund_date_service = FundDateService()
            financial_years = fund_date_service.get_fund_financial_years(fund, session=session)
            
            return jsonify({"financial_years": financial_years}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting fund financial years: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
