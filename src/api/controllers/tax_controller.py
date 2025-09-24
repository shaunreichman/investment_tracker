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

from flask import request, current_app
from sqlalchemy.orm import Session

from src.api.controllers.formatters.tax_formatter import format_tax_statement
from src.tax.services.tax_statement_service import TaxStatementService

from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.dto.response_codes import ApiResponseCode


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
        self.tax_statement_service = TaxStatementService()


    ################################################################################
    # TAX STATEMENT ENDPOINTS
    ################################################################################

    ###############################################
    # Get tax statement
    ###############################################

    def get_tax_statements_for_fund(self, fund_id: int) -> ControllerResponseDTO:
        """
        Get all tax statements for a fund.
        
        Args:
            fund_id: ID of the fund to get tax statements for
            
        Returns:
            ControllerResponseDTO: DTO containing tax statements data and status
        """
        try:
            # Get database session
            session = self._get_session()

            try:
                # Get tax statements for this fund
                tax_statements = self.tax_statement_service.get_tax_statements_for_fund(fund_id, session=session)

                if not tax_statements:
                    return ControllerResponseDTO(error="Tax statements not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                # Format the response using formatter
                formatted_tax_statements = [format_tax_statement(statement) for statement in tax_statements]

                return ControllerResponseDTO(data=formatted_tax_statements, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting tax statements for fund {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting tax statements for fund {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting tax statements for fund {fund_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


        #     # Get fund using repository pattern (no direct database queries)
        #     from src.fund.repositories.fund_repository import FundRepository
        #     fund = FundRepository().get_by_id(fund_id, session=session)
        #     if not fund:
        #         return jsonify({"error": "Fund not found"}), 404
            
        #     # Get tax statements for this fund using repository pattern
        #     from src.fund.repositories.tax_statement_repository import TaxStatementRepository
        #     tax_statements = TaxStatementRepository().get_by_fund(fund_id, session=session, sort_order=SortOrder.DESC)
            
        #     statements_data = []
        #     for statement in tax_statements:
        #         statement_data = {
        #             "id": statement.id,
        #             "entity_id": statement.entity_id,
        #             "financial_year": statement.financial_year,
        #             "statement_date": statement.statement_date.isoformat() if statement.statement_date else None,
        #             "tax_payment_date": statement.get_tax_payment_date().isoformat() if statement.get_tax_payment_date() else None,
        #             "eofy_debt_interest_deduction_rate": float(statement.eofy_debt_interest_deduction_rate) if statement.eofy_debt_interest_deduction_rate else None,
        #             "interest_received_in_cash": float(statement.interest_received_in_cash) if statement.interest_received_in_cash else None,
        #             "interest_receivable_this_fy": float(statement.interest_receivable_this_fy) if statement.interest_receivable_this_fy else None,
        #             "interest_receivable_prev_fy": float(statement.interest_receivable_prev_fy) if statement.interest_receivable_prev_fy else None,
        #             "interest_non_resident_withholding_tax_from_statement": float(statement.interest_non_resident_withholding_tax_from_statement) if statement.interest_non_resident_withholding_tax_from_statement else None,
        #             "interest_income_tax_rate": float(statement.interest_income_tax_rate) if statement.interest_income_tax_rate else None,
        #             "interest_income_amount": float(statement.interest_income_amount) if statement.interest_income_amount else None,
        #             "interest_tax_amount": float(statement.interest_tax_amount) if statement.interest_tax_amount else None,
        #             "dividend_franked_income_amount": float(statement.dividend_franked_income_amount) if statement.dividend_franked_income_amount else None,
        #             "dividend_unfranked_income_amount": float(statement.dividend_unfranked_income_amount) if statement.dividend_unfranked_income_amount else None,
        #             "dividend_franked_income_tax_rate": float(statement.dividend_franked_income_tax_rate) if statement.dividend_franked_income_tax_rate else None,
        #             "dividend_unfranked_income_tax_rate": float(statement.dividend_unfranked_income_tax_rate) if statement.dividend_unfranked_income_tax_rate else None,
        #             "dividend_franked_tax_amount": float(statement.dividend_franked_tax_amount) if statement.dividend_franked_tax_amount else None,
        #             "dividend_unfranked_tax_amount": float(statement.dividend_unfranked_tax_amount) if statement.dividend_unfranked_tax_amount else None,
        #             "capital_gain_income_amount": float(statement.capital_gain_income_amount) if statement.capital_gain_income_amount else None,
        #             "capital_gain_income_tax_rate": float(statement.capital_gain_income_tax_rate) if statement.capital_gain_income_tax_rate else None,
        #             "capital_gain_tax_amount": float(statement.capital_gain_tax_amount) if statement.capital_gain_tax_amount else None,
        #             "eofy_debt_interest_deduction_sum_of_daily_interest": float(statement.eofy_debt_interest_deduction_sum_of_daily_interest) if statement.eofy_debt_interest_deduction_sum_of_daily_interest else None,
        #             "eofy_debt_interest_deduction_total_deduction": float(statement.eofy_debt_interest_deduction_total_deduction) if statement.eofy_debt_interest_deduction_total_deduction else None,
        #             "non_resident": statement.non_resident,
        #             "accountant": statement.accountant,
        #             "notes": statement.notes,
        #             "created_at": statement.created_at.isoformat() if statement.created_at else None,
        #             "updated_at": statement.updated_at.isoformat() if statement.updated_at else None
        #         }
        #         statements_data.append(statement_data)
            
        #     return jsonify({"tax_statements": statements_data}), 200
            
        # except Exception as e:
        #     current_app.logger.error(f"Error getting fund tax statements: {str(e)}")
        #     return jsonify({"error": "Internal server error"}), 500

    def get_tax_statement(self, tax_statement_id: int) -> ControllerResponseDTO:
        """
        Get a tax statement by ID.

        Args:
            tax_statement_id: ID of the tax statement to get
            
        Returns:
            ControllerResponseDTO: DTO containing tax statement data and status
        """
        try:
            # Get database session
            session = self._get_session()

            try:
                # Get tax statement by ID
                tax_statement = self.tax_statement_service.get_tax_statement(tax_statement_id, session=session)

                if not tax_statement:
                    return ControllerResponseDTO(error="Tax statement not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                # Format the response using formatter
                formatted_tax_statement = format_tax_statement(tax_statement)

                return ControllerResponseDTO(data=formatted_tax_statement, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting tax statement {tax_statement_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting tax statement {tax_statement_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting tax statement {tax_statement_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    

    ###############################################
    # Create tax statement
    ###############################################

    def create_tax_statement(self, fund_id: int) -> ControllerResponseDTO:
        """
        Create a new tax statement for a fund.
        
        Args:
            fund_id: ID of the fund to create tax statement for
            
        Returns:
            ControllerResponseDTO: DTO containing tax statement data and status
            
        Note: Input data is pre-validated by middleware validation decorator.
        """
        try:
            tax_statement_data = getattr(request, 'validated_data', {})
            if not tax_statement_data:
                return ControllerResponseDTO(error="No validated data available", response_code=ApiResponseCode.VALIDATION_ERROR)

            # Validate required fields
            required_fields = ['entity_id', 'financial_year', 'statement_date', 'eofy_debt_interest_deduction_rate']
            for field in required_fields:
                if field not in tax_statement_data or not tax_statement_data[field]:
                    return ControllerResponseDTO(error=f"Missing required field: {field}", response_code=ApiResponseCode.VALIDATION_ERROR)

            # Get database session
            session = self._get_session()

            try:
                # Create tax statement with validated data
                tax_statement = self.tax_statement_service.create_tax_statement(fund_id, tax_statement_data, session=session)

                if not tax_statement:
                    return ControllerResponseDTO(error="Tax statement not created", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                # Format the response using formatter
                formatted_tax_statement = format_tax_statement(tax_statement)

                return ControllerResponseDTO(data=formatted_tax_statement, response_code=ApiResponseCode.CREATED)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating tax statement {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating tax statement {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error creating tax statement {fund_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
                        
        #     # Get fund and validate it exists
        #     from src.fund.repositories.fund_repository import FundRepository
        #     fund = FundRepository().get_by_id(fund_id, session=session)
            
        #     if not fund:
        #         return jsonify({"error": "Fund not found"}), 404
            
        #     # Get pre-validated data from middleware
        #     data = getattr(request, 'validated_data', {})
        #     if not data:
        #         return jsonify({"error": "No validated data available"}), 400
            
        #     # Extract validated fields
        #     entity_id = data['entity_id']
        #     financial_year = data['financial_year']
        #     statement_date = data['statement_date']
        #     eofy_debt_interest_deduction_rate = data['eofy_debt_interest_deduction_rate']
            
        #     # Validate entity exists
        #     entity = session.query(Entity).filter(Entity.id == entity_id).first()
        #     if not entity:
        #         return jsonify({"error": "Entity not found"}), 404
            
        #     # Check for existing tax statement
        #     existing_statement = session.query(TaxStatement).filter(
        #         TaxStatement.fund_id == fund_id,
        #         TaxStatement.entity_id == entity_id,
        #         TaxStatement.financial_year == financial_year
        #     ).first()
            
        #     if existing_statement:
        #         return jsonify({"error": "Tax statement already exists for this fund, entity, and financial year"}), 409
            
        #     # Create tax statement with validated data
        #     tax_statement = TaxStatement(
        #         fund_id=fund_id,
        #         entity_id=entity_id,
        #         financial_year=financial_year,
        #         statement_date=statement_date,
        #         eofy_debt_interest_deduction_rate=eofy_debt_interest_deduction_rate,
        #         interest_received_in_cash=data.get('interest_received_in_cash'),
        #         interest_receivable_this_fy=data.get('interest_receivable_this_fy'),
        #         interest_receivable_prev_fy=data.get('interest_receivable_prev_fy'),
        #         interest_non_resident_withholding_tax_from_statement=data.get('interest_non_resident_withholding_tax_from_statement'),
        #         interest_income_tax_rate=data.get('interest_income_tax_rate'),
        #         dividend_franked_income_amount=data.get('dividend_franked_income_amount'),
        #         dividend_unfranked_income_amount=data.get('dividend_unfranked_income_amount'),
        #         dividend_franked_income_tax_rate=data.get('dividend_franked_income_tax_rate'),
        #         dividend_unfranked_income_tax_rate=data.get('dividend_unfranked_income_tax_rate'),
        #         capital_gain_income_amount=data.get('capital_gain_income_amount'),
        #         capital_gain_income_tax_rate=data.get('capital_gain_income_tax_rate'),
        #         non_resident=data.get('non_resident', False),
        #         accountant=data.get('accountant'),
        #         notes=data.get('notes')
        #     )
            
        #     # Calculate derived fields
        #     interest_income = tax_statement.calculate_interest_income_amount(session)
        #     dividend_totals = tax_statement.calculate_dividend_totals(session)
        #     capital_gain_total = tax_statement.calculate_capital_gain_totals(session)
            
        #     session.add(tax_statement)
        #     session.commit()
            
        #     # Create tax payment events for this tax statement
        #     try:
        #         created_events = tax_statement.create_tax_payment_events(session)
        #     except Exception as e:
        #         current_app.logger.error(f"Error creating tax payment events: {str(e)}")
        #         # Don't fail the entire request if tax payment events fail to create
            
        #     # Return created tax statement data
        #     response_data = {
        #         "id": tax_statement.id,
        #         "fund_id": tax_statement.fund_id,
        #         "entity_id": tax_statement.entity_id,
        #         "financial_year": tax_statement.financial_year,
        #         "statement_date": tax_statement.statement_date.isoformat() if tax_statement.statement_date else None,
        #         "tax_payment_date": tax_statement.get_tax_payment_date().isoformat() if tax_statement.get_tax_payment_date() else None,
        #         "eofy_debt_interest_deduction_rate": float(tax_statement.eofy_debt_interest_deduction_rate) if tax_statement.eofy_debt_interest_deduction_rate else None,
        #         "interest_received_in_cash": float(tax_statement.interest_received_in_cash) if tax_statement.interest_received_in_cash else None,
        #         "interest_receivable_this_fy": float(tax_statement.interest_receivable_this_fy) if tax_statement.interest_receivable_this_fy else None,
        #         "interest_receivable_prev_fy": float(tax_statement.interest_receivable_prev_fy) if tax_statement.interest_receivable_prev_fy else None,
        #         "interest_non_resident_withholding_tax_from_statement": float(tax_statement.interest_non_resident_withholding_tax_from_statement) if tax_statement.interest_non_resident_withholding_tax_from_statement else None,
        #         "interest_income_tax_rate": float(tax_statement.interest_income_tax_rate) if tax_statement.interest_income_tax_rate else None,
        #         "interest_income_amount": float(tax_statement.interest_income_amount) if tax_statement.interest_income_amount else None,
        #         "interest_tax_amount": float(tax_statement.interest_tax_amount) if tax_statement.interest_tax_amount else None,
        #         "dividend_franked_income_amount": float(tax_statement.dividend_franked_income_amount) if tax_statement.dividend_franked_income_amount else None,
        #         "dividend_unfranked_income_amount": float(tax_statement.dividend_unfranked_income_amount) if tax_statement.dividend_unfranked_income_amount else None,
        #         "dividend_franked_income_tax_rate": float(tax_statement.dividend_franked_income_tax_rate) if tax_statement.dividend_franked_income_tax_rate else None,
        #         "dividend_unfranked_income_tax_rate": float(tax_statement.dividend_unfranked_income_tax_rate) if tax_statement.dividend_unfranked_income_tax_rate else None,
        #         "dividend_franked_tax_amount": float(tax_statement.dividend_franked_tax_amount) if tax_statement.dividend_franked_tax_amount else None,
        #         "dividend_unfranked_tax_amount": float(tax_statement.dividend_unfranked_tax_amount) if tax_statement.dividend_unfranked_tax_amount else None,
        #         "capital_gain_income_amount": float(tax_statement.capital_gain_income_amount) if tax_statement.capital_gain_income_amount else None,
        #         "capital_gain_income_tax_rate": float(tax_statement.capital_gain_income_tax_rate) if tax_statement.capital_gain_income_tax_rate else None,
        #         "capital_gain_tax_amount": float(tax_statement.capital_gain_tax_amount) if tax_statement.capital_gain_tax_amount else None,
        #         "eofy_debt_interest_deduction_sum_of_daily_interest": float(tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest) if tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest else None,
        #         "eofy_debt_interest_deduction_total_deduction": float(tax_statement.eofy_debt_interest_deduction_total_deduction) if tax_statement.eofy_debt_interest_deduction_total_deduction else None,
        #         "non_resident": tax_statement.non_resident,
        #         "accountant": tax_statement.accountant,
        #         "notes": tax_statement.notes,
        #         "created_at": tax_statement.created_at.isoformat() if tax_statement.created_at else None,
        #         "updated_at": tax_statement.updated_at.isoformat() if tax_statement.updated_at else None
        #     }
            
        #     return jsonify(response_data), 201
            
        # except Exception as e:
        #     current_app.logger.error(f"Error creating tax statement: {str(e)}")
        #     return jsonify({"error": "Internal server error"}), 500
  
    ###############################################
    # Delete tax statement
    ###############################################
    
    def delete_tax_statement(self, tax_statement_id: int) -> ControllerResponseDTO:
        """
        Delete a tax statement by ID.
        """
        try:
            # Get database session
            session = self._get_session()

            try:
                # Delete tax statement by ID
                success = self.tax_statement_service.delete_tax_statement(tax_statement_id, session=session)

                if not success:
                    return ControllerResponseDTO(error="Tax statement not deleted", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                # Commit the transaction
                session.commit()

                return ControllerResponseDTO(message="Tax statement deleted successfully", response_code=ApiResponseCode.DELETED)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting tax statement {tax_statement_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting tax statement {tax_statement_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error deleting tax statement {tax_statement_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Get fund financial years
    ###############################################

    def get_fund_financial_years(self, fund_id: int) -> ControllerResponseDTO:
        """
        Get all financial years from fund start date to current date.
        
        Args:
            fund_id: ID of the fund to get financial years for
            
        Returns:
            ControllerResponseDTO: DTO containing financial years data and status
        """
        try:
            # Get database session
            session = self._get_session()

            try:
                # Get financial years for this fund
                financial_years = self.tax_statement_service.get_fund_financial_years(fund_id, session=session)
                
                if not financial_years:
                    return ControllerResponseDTO(error="Financial years not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                return ControllerResponseDTO(data=financial_years, response_code=ApiResponseCode.SUCCESS)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting financial years for fund {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting financial years for fund {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()
        
        except Exception as e:
            current_app.logger.error(f"Error getting financial years for fund {fund_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

        #     # Get fund using repository pattern (no direct database queries)
        #     from src.fund.repositories.fund_repository import FundRepository
        #     fund = FundRepository().get_by_id(fund_id, session=session)
        #     if not fund:
        #         return jsonify({"error": "Fund not found"}), 404
            
        #     from src.fund.services.fund_date_service import FundDateService
        #     fund_date_service = FundDateService()
        #     financial_years = fund_date_service.get_fund_financial_years(fund, session=session)
            
        #     return jsonify({"financial_years": financial_years}), 200
            
        # except Exception as e:
        #     current_app.logger.error(f"Error getting fund financial years: {str(e)}")
        #     return jsonify({"error": "Internal server error"}), 500


    ###############################################################################
    # SESSION HANDLING
    ###############################################################################

    def _get_session(self) -> Session:
        """
        Get the current database session from middleware.
        
        Returns:
            Database session from Flask's g context
        """
        from src.api.middleware.database_session import get_current_session
        return get_current_session()
