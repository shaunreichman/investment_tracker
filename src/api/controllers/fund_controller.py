"""
Fund API Controller.

This controller handles HTTP requests for fund operations,
providing RESTful endpoints for fund management.

Key responsibilities:
- Fund CRUD endpoints
- Fund event endpoints
- Fund calculation endpoints
- Input validation and error handling
"""

from typing import List, Optional, Dict, Any, Tuple
from flask import request, jsonify, current_app
from sqlalchemy.orm import Session

from src.api.dto.api_response import ApiResponse
from src.fund.enums import FundStatus, FundType, EventType
from src.fund.services.fund_service import FundService
from src.fund.services.fund_event_service import FundEventService
from src.api.controllers.formatters.fund_formatter import format_fund_comprehensive, format_fund, format_event
from src.api.dto.controller_response_dto import ControllerResponseDTO, ControllerResponseStatus
class FundController:
    """
    Controller for fund operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for fund operations. It delegates business logic to the FundService
    and handles request/response formatting.
    
    Attributes:
        fund_service (FundService): Service layer for fund operations
    """
    
    def __init__(self):
        """Initialize the fund controller."""
        self.fund_service = FundService()
        self.fund_event_service = FundEventService()

    def get_fund(self, fund_id: int, include_events: bool = True, include_cash_flows: bool = False, include_tax_statements: bool = False):
        """
        Get a fund by ID with optional detailed information.
        
        Args:
            fund_id: ID of the fund to retrieve
            include_events: Whether to include fund events in the response
            include_cash_flows: Whether to include cash flows for each event
            include_tax_statements: Whether to include tax statements for the fund
            
        Returns:
            ControllerResponseDTO: DTO containing fund data and status
        """
        try:
            # Get database session
            session = self._get_session()
            
            # Get the fund (now returns domain object)
            fund = self.fund_service.get_fund(fund_id, session)
            
            if not fund:
                return ControllerResponseDTO(error="Fund not found", status=ControllerResponseStatus.NOT_FOUND.value)
            
            # Format the response using comprehensive formatter with specified options
            formatted_fund = format_fund_comprehensive(
                fund, 
                include_events=include_events, 
                include_cash_flows=include_cash_flows,
                include_tax_statements=include_tax_statements
            )

            return ControllerResponseDTO(data=formatted_fund, status=ControllerResponseStatus.SUCCESS.value)
            
        except Exception as e:
            current_app.logger.error(f"Error getting fund {fund_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
        finally:
            if 'session' in locals():
                session.close()
    
    def create_fund(self):
        """
        Create a new fund.
        
        Returns:
            ControllerResponseDTO: DTO containing fund data or error
            
        Note: Input data is pre-validated by middleware validation decorator.
        """
        try:
            # Get pre-validated data from middleware
            fund_data = getattr(request, 'validated_data', {})
            if not fund_data:
                return ControllerResponseDTO(error='No validated data available', status=ControllerResponseStatus.VALIDATION_ERROR.value)
            
            # Get database session
            session = self._get_session()
            
            try:
                # Create the fund with validated data (now returns domain object)
                fund = self.fund_service.create_fund(fund_data, session)
                
                # Commit the transaction
                session.commit()
                
                # Format the response using formatter
                formatted_fund = format_fund(fund)
                return ControllerResponseDTO(data=formatted_fund, status=ControllerResponseStatus.CREATED.value)
                
            except ValueError as e:
                session.rollback()
                return ControllerResponseDTO(error=str(e), status=ControllerResponseStatus.VALIDATION_ERROR.value)
            except Exception as e:
                current_app.logger.error(f"Error creating fund: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
            finally:
                session.close()
                
        except Exception as e:
            current_app.logger.error(f"Error in create_fund: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
    
    def delete_fund(self, fund_id: int):
        """
        Delete a fund with enterprise validation.
        
        Args:
            fund_id: ID of the fund to delete
            
        Returns:
            ControllerResponseDTO: DTO containing status or error
        """
        try:
            # Get database session
            session = self._get_session()
            
            try:
                # Delete the fund (now includes validation)
                success = self.fund_service.delete_fund(fund_id, session)
                
                if not success:
                    return ControllerResponseDTO(error="Fund not found", status=ControllerResponseStatus.NOT_FOUND.value)
                
                # Commit the transaction
                session.commit()
                
                return ControllerResponseDTO(status=ControllerResponseStatus.DELETED.value, message="Fund deleted successfully")
                
            except ValueError as e:
                # ENTERPRISE ERROR HANDLING: Validation errors
                session.rollback()
                return ControllerResponseDTO(error=f"Fund deletion validation failed: {str(e)}", status=ControllerResponseStatus.VALIDATION_ERROR.value)
                
            except Exception as e:
                # ENTERPRISE ERROR HANDLING: Unexpected errors
                current_app.logger.error(f"Error deleting fund: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
                
            finally:
                session.close()
            
        except Exception as e:
            current_app.logger.error(f"Error in delete_fund: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
    
    def add_capital_call(self, fund_id: int, event_data: dict):
        """
        Add a capital call event.
        
        Args:
            fund_id: ID of the fund
            event_data: Validated event data from middleware
            
        Returns:
            ControllerResponseDTO: DTO containing event data or error
        """
        
        try:
            # Get database session
            session = self._get_session()
            
            try:
                # Get the fund
                fund = self.fund_service.get_fund(fund_id, session)
                if not fund:
                    return ControllerResponseDTO(error="Fund not found", status=ControllerResponseStatus.NOT_FOUND.value)

                event = self.fund_event_service.add_capital_call(
                    fund=fund,
                    amount=float(event_data['amount']),
                    call_date=event_data['event_date'],  # Already parsed by middleware
                    description=event_data.get('description'),
                    reference_number=event_data.get('reference_number'),
                    session=session
                )
                
                session.commit()
                
                formatted_event = format_event(event)
                return ControllerResponseDTO(data=formatted_event, status=ControllerResponseStatus.CREATED.value)
                
            except ValueError as e:
                session.rollback()
                return ControllerResponseDTO(error=str(e), status=ControllerResponseStatus.VALIDATION_ERROR.value)
            except Exception as e:
                current_app.logger.error(f"Error adding capital call: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
            finally:
                session.close()
                
        except Exception as e:
            current_app.logger.error(f"Error in add_capital_call: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status="server_error")
    
    def add_return_of_capital(self, fund_id: int, event_data: dict):
        """
        Add a return of capital event.
        
        Args:
            fund_id: ID of the fund
            event_data: Validated event data from middleware
            
        Returns:
            ControllerResponseDTO: DTO containing event data or error
        """
        
        try:
            # Validate required fields (business validation)
            required_fields = ['amount', 'event_date']
            for field in required_fields:
                if field not in event_data:
                    return ControllerResponseDTO(error=f'Required field "{field}" is missing', status="validation_error")
            
            # Get database session
            session = self._get_session()
            
            try:
                # Get the fund
                fund = self.fund_service.get_fund(fund_id, session)
                if not fund:
                    return ControllerResponseDTO(error="Fund not found", status=ControllerResponseStatus.NOT_FOUND.value)
                
                # Parse event date (business logic)
                event_date = event_data['event_date']
                if isinstance(event_date, str):
                    from datetime import datetime
                    event_date = datetime.fromisoformat(event_date).date()
                
                # Add the return of capital event using FundEventService
                event = self.fund_event_service.add_return_of_capital(
                    fund=fund,
                    amount=float(event_data['amount']),
                    return_date=event_date,
                    description=event_data.get('description'),
                    reference_number=event_data.get('reference_number'),
                    session=session
                )
                
                # Commit the transaction
                session.commit()
                
                # Format the event for response
                formatted_event = format_event(event)
                return ControllerResponseDTO(data=formatted_event, status=ControllerResponseStatus.CREATED.value)
                
            except ValueError as e:
                session.rollback()
                return ControllerResponseDTO(error=str(e), status=ControllerResponseStatus.VALIDATION_ERROR.value)
            except Exception as e:
                current_app.logger.error(f"Error adding return of capital: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
            finally:
                session.close()
                
        except Exception as e:
            current_app.logger.error(f"Error in add_return_of_capital: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status="server_error")
    
    def add_unit_purchase(self, fund_id: int, event_data: dict):
        """
        Add a unit purchase event.
        
        Args:
            fund_id: ID of the fund
            event_data: Validated event data from middleware
            
        Returns:
            ControllerResponseDTO: DTO containing event data or error
        """
        
        try:
            # Validate required fields (business validation)
            required_fields = ['units_purchased', 'unit_price', 'event_date']
            for field in required_fields:
                if field not in event_data:
                    return ControllerResponseDTO(error=f'Required field "{field}" is missing', status="validation_error")
            
            # Get database session
            session = self._get_session()
            
            try:
                # Get the fund
                fund = self.fund_service.get_fund(fund_id, session)
                if not fund:
                    return ControllerResponseDTO(error="Fund not found", status=ControllerResponseStatus.NOT_FOUND.value)
                
                # Parse event date (business logic)
                event_date = event_data['event_date']
                if isinstance(event_date, str):
                    from datetime import datetime
                    event_date = datetime.fromisoformat(event_date).date()
                
                # Add the unit purchase event using FundEventService
                event = self.fund_event_service.add_unit_purchase(
                    fund=fund,
                    units=float(event_data['units_purchased']),
                    price=float(event_data['unit_price']),
                    date=event_date,
                    brokerage_fee=float(event_data.get('brokerage_fee', 0.0)),
                    description=event_data.get('description'),
                    reference_number=event_data.get('reference_number'),
                    session=session
                )
                
                # Commit the transaction
                session.commit()
                
                # Format the event for response
                formatted_event = format_event(event)
                return ControllerResponseDTO(data=formatted_event, status=ControllerResponseStatus.CREATED.value)
                
            except ValueError as e:
                session.rollback()
                return ControllerResponseDTO(error=str(e), status=ControllerResponseStatus.VALIDATION_ERROR.value)
            except Exception as e:
                current_app.logger.error(f"Error adding unit purchase: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
            finally:
                session.close()
                
        except Exception as e:
            current_app.logger.error(f"Error in add_unit_purchase: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status="server_error")
    
    def add_unit_sale(self, fund_id: int, event_data: dict):
        """
        Add a unit sale event.
        
        Args:
            fund_id: ID of the fund
            event_data: Validated event data from middleware
            
        Returns:
            ControllerResponseDTO: DTO containing event data or error
        """
        
        try:
            # Validate required fields (business validation)
            required_fields = ['units_sold', 'unit_price', 'event_date']
            for field in required_fields:
                if field not in event_data:
                    return ControllerResponseDTO(error=f'Required field "{field}" is missing', status="validation_error")
            
            # Get database session
            session = self._get_session()
            
            try:
                # Get the fund
                fund = self.fund_service.get_fund(fund_id, session)
                if not fund:
                    return ControllerResponseDTO(error="Fund not found", status=ControllerResponseStatus.NOT_FOUND.value)
                
                # Parse event date (business logic)
                event_date = event_data['event_date']
                if isinstance(event_date, str):
                    from datetime import datetime
                    event_date = datetime.fromisoformat(event_date).date()
                
                # Add the unit sale event using FundEventService
                event = self.fund_event_service.add_unit_sale(
                    fund=fund,
                    units=float(event_data['units_sold']),
                    price=float(event_data['unit_price']),
                    date=event_date,
                    brokerage_fee=float(event_data.get('brokerage_fee', 0.0)),
                    description=event_data.get('description'),
                    reference_number=event_data.get('reference_number'),
                    session=session
                )
                
                # Commit the transaction
                session.commit()
                
                # Format the event for response
                formatted_event = format_event(event)
                return ControllerResponseDTO(data=formatted_event, status=ControllerResponseStatus.CREATED.value)
                
            except ValueError as e:
                session.rollback()
                return ControllerResponseDTO(error=str(e), status=ControllerResponseStatus.VALIDATION_ERROR.value)
            except Exception as e:
                current_app.logger.error(f"Error adding unit sale: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
            finally:
                session.close()
                
        except Exception as e:
            current_app.logger.error(f"Error in add_unit_sale: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status="server_error")
    
    def add_nav_update(self, fund_id: int, event_data: dict):
        """
        Add a NAV update event.
        
        Args:
            fund_id: ID of the fund
            event_data: Validated event data from middleware
            
        Returns:
            ControllerResponseDTO: DTO containing event data or error
        """
        
        try:
            # Validate required fields (business validation)
            required_fields = ['nav_per_share', 'event_date']
            for field in required_fields:
                if field not in event_data:
                    return ControllerResponseDTO(error=f'Required field "{field}" is missing', status="validation_error")            

            session = self._get_session()
            
            try:
                fund = self.fund_service.get_fund(fund_id, session)
                if not fund:
                    return ControllerResponseDTO(error="Fund not found", status=ControllerResponseStatus.NOT_FOUND.value)
                
                # Parse event date (business logic)
                event_date = event_data['event_date']
                if isinstance(event_date, str):
                    from datetime import datetime
                    event_date = datetime.fromisoformat(event_date).date()
                
                # Add the NAV update event using FundEventService
                event = self.fund_event_service.add_nav_update(
                    fund=fund,
                    nav_per_share=float(event_data['nav_per_share']),
                    date=event_date,
                    description=event_data.get('description'),
                    reference_number=event_data.get('reference_number'),
                    session=session
                )
                
                # Commit the transaction
                session.commit()
                
                # Format the event for response
                formatted_event = format_event(event)
                return ControllerResponseDTO(data=formatted_event, status=ControllerResponseStatus.CREATED.value)
                
            except ValueError as e:
                session.rollback()
                return ControllerResponseDTO(error=str(e), status=ControllerResponseStatus.VALIDATION_ERROR.value)
            except Exception as e:
                current_app.logger.error(f"Error adding NAV update: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
            finally:
                session.close()
                
        except Exception as e:
            current_app.logger.error(f"Error in add_nav_update: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status="server_error")
    
    def add_distribution(self, fund_id: int, event_data: dict):
        """
        Add a distribution event.
        
        Args:
            fund_id: ID of the fund
            event_data: Validated event data from middleware
            
        Returns:
            ControllerResponseDTO: DTO containing event data or error
        """
        
        try:
            # Validate required fields (business validation)
            required_fields = ['event_date', 'distribution_type']
            for field in required_fields:
                if field not in event_data:
                    return ControllerResponseDTO(error=f'Required field "{field}" is missing', status="validation_error")
            
            # Get database session
            session = self._get_session()
            
            try:
                # Get the fund
                fund = self.fund_service.get_fund(fund_id, session)
                if not fund:
                    return ControllerResponseDTO(error="Fund not found", status=ControllerResponseStatus.NOT_FOUND.value)
                
                # Parse event date (business logic)
                event_date = event_data['event_date']
                if isinstance(event_date, str):
                    from datetime import datetime
                    event_date = datetime.fromisoformat(event_date).date()
                
                # Parse distribution type (business logic)
                from src.fund.enums import DistributionType
                distribution_type = DistributionType(event_data['distribution_type'])
                
                # Handle withholding tax distributions (business logic)
                if (event_data.get('distribution_type') == 'INTEREST' and
                    any([
                        event_data.get('interest_gross_amount') is not None,
                        event_data.get('interest_net_amount') is not None,
                        event_data.get('interest_withholding_tax_amount') is not None,
                        event_data.get('interest_withholding_tax_rate') is not None
                    ])):
                    # Withholding tax distribution
                    event = self.fund_event_service.add_distribution(
                        fund=fund,
                        event_date=event_date,
                        distribution_type=distribution_type,
                        has_withholding_tax=True,
                        gross_interest_amount=float(event_data.get('interest_gross_amount', 0)) if event_data.get('interest_gross_amount') else None,
                        net_interest_amount=float(event_data.get('interest_net_amount', 0)) if event_data.get('interest_net_amount') else None,
                        withholding_tax_amount=float(event_data.get('interest_withholding_tax_amount', 0)) if event_data.get('interest_withholding_tax_amount') else None,
                        withholding_tax_rate=float(event_data.get('interest_withholding_tax_rate', 0)) if event_data.get('interest_withholding_tax_rate') else None,
                        description=event_data.get('description'),
                        reference_number=event_data.get('reference_number'),
                        session=session
                    )
                else:
                    # Simple distribution
                    if 'amount' not in event_data:
                        return ControllerResponseDTO(error='Required field "amount" is missing for simple distribution', status="validation_error")
                    
                    event = self.fund_event_service.add_distribution(
                        fund=fund,
                        event_date=event_date,
                        distribution_type=distribution_type,
                        distribution_amount=float(event_data['amount']),
                        has_withholding_tax=False,
                        description=event_data.get('description'),
                        reference_number=event_data.get('reference_number'),
                        session=session
                    )
                
                # Commit the transaction
                session.commit()
                
                # Format the event for response
                formatted_event = format_event(event)
                return ControllerResponseDTO(data=formatted_event, status=ControllerResponseStatus.CREATED.value)
                
            except ValueError as e:
                session.rollback()
                return ControllerResponseDTO(error=str(e), status=ControllerResponseStatus.VALIDATION_ERROR.value)
            except Exception as e:
                current_app.logger.error(f"Error adding distribution: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
            finally:
                session.close()
                
        except Exception as e:
            current_app.logger.error(f"Error in add_distribution: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status="server_error")
    
    def get_fund_events(self, fund_id: int):
        """
        Get all events for a specific fund - optimized for fast table updates.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            ControllerResponseDTO: DTO containing events and status
        """
        try:
            # Get database session
            session = self._get_session()
            try:
                # Get fund events - service returns a list directly
                events = self.fund_event_service.get_fund_events(fund_id, session)
                if events is None:
                    return ControllerResponseDTO(error="Fund not found", status=ControllerResponseStatus.NOT_FOUND.value)
                formatted_events = [format_event(event) for event in events]
                return ControllerResponseDTO(data=formatted_events, status=ControllerResponseStatus.SUCCESS.value)
            except ValueError as e:
                return ControllerResponseDTO(error=str(e), status=ControllerResponseStatus.VALIDATION_ERROR.value)
            except Exception as e:
                current_app.logger.error(f"Error getting fund events: {str(e)}")
                return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
            finally:
                session.close()
        except Exception as e:
            current_app.logger.error(f"Error in get_fund_events: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status="server_error")
    
    def delete_fund_event(self, fund_id: int, event_id: int):
        """
        Delete a fund event.
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event to delete
            
        Returns:
            ControllerResponseDTO: DTO containing status or error
        """
        try:
            # Get database session
            session = self._get_session()
            try:
                success = self.fund_event_service.delete_fund_event(fund_id, event_id, session)
                if not success:
                    return ControllerResponseDTO(error="Event not found", status=ControllerResponseStatus.NOT_FOUND.value)
                session.commit()
                return ControllerResponseDTO(status=ControllerResponseStatus.DELETED.value)
            except Exception as e:
                current_app.logger.error(f"Error deleting fund event: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", status=ControllerResponseStatus.SERVER_ERROR.value)
            finally:
                session.close()
        except Exception as e:
            current_app.logger.error(f"Error in delete_fund_event: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", status="server_error")
    
    def add_fund_event_cash_flow(self, fund_id: int, event_id: int, cash_flow_data: dict) -> Tuple[ApiResponse, int]:
        """
        Add a cash flow to a fund event with pre-validated data.
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event
            cash_flow_data: Pre-validated cash flow data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get database session
            session = self._get_session()
            
            # Validate fund exists
            fund = self.fund_service.get_fund(fund_id, session)
            if not fund:
                return jsonify(ApiResponse(success=False, message='Fund not found').to_dict()), 404
            
            # Validate event exists and belongs to fund
            event = self.fund_event_service.get_fund_event(fund_id, event_id, session)
            if not event:
                return jsonify(ApiResponse(success=False, message='Fund event not found').to_dict()), 404
            
            # Validate bank account exists
            from src.banking.models import BankAccount
            bank_account = session.query(BankAccount).filter(BankAccount.id == cash_flow_data['bank_account_id']).first()
            if not bank_account:
                return jsonify(ApiResponse(success=False, message='Bank account not found').to_dict()), 404
            
            # Validate currency matches bank account
            if cash_flow_data['currency'].upper() != bank_account.currency.upper():
                return jsonify(ApiResponse(success=False, message='Cash flow currency must match bank account currency').to_dict()), 400
            
            # Add cash flow using domain method
            cash_flow = event.add_cash_flow(
                bank_account_id=cash_flow_data['bank_account_id'],
                transfer_date=cash_flow_data['transfer_date'],
                currency=cash_flow_data['currency'],
                amount=cash_flow_data['amount'],
                reference=cash_flow_data.get('reference'),
                notes=cash_flow_data.get('notes'),
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
            
            return jsonify(ApiResponse(data=response_data).to_dict()), 201
            
        except Exception as e:
            current_app.logger.error(f"Error adding cash flow to event: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify(ApiResponse(success=False, message='Internal server error').to_dict()), 500
        finally:
            if 'session' in locals():
                session.close()
    
    def _get_session(self) -> Session:
        """
        Get the current database session from middleware.
        
        Returns:
            Database session from Flask's g context
        """
        from src.api.middleware.database_session import get_current_session
        return get_current_session()