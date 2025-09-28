"""
Fund API Controller.
"""

from flask import request, current_app
from sqlalchemy.orm import Session

from src.fund.services.fund_service import FundService
from src.fund.services.fund_event_service import FundEventService
from src.fund.services.fund_event_cash_flow_service import FundEventCashFlowService
from src.fund.services.fund_tax_statement_service import FundTaxStatementService
from src.api.controllers.formatters.fund_formatter import format_fund_comprehensive, format_fund, format_fund_event, format_fund_event_cash_flow, format_fund_tax_statement
from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.dto.response_codes import ApiResponseCode
from typing import Optional, Dict, Any
from src.fund.enums.fund_event_enums import EventType
class FundController:
    """
    Controller for fund operations.
    
    Attributes:
        fund_service (FundService): Service layer for fund operations
        fund_event_service (FundEventService): Service layer for fund event operations
        fund_event_cash_flow_service (FundEventCashFlowService): Service layer for fund event cash flow operations
        fund_tax_statement_service (FundTaxStatementService): Service layer for fund tax statement operations
    """
    
    def __init__(self):
        """Initialize the fund controller."""
        self.fund_service = FundService()
        self.fund_event_service = FundEventService()
        self.fund_event_cash_flow_service = FundEventCashFlowService()
        self.fund_tax_statement_service = FundTaxStatementService()

    ################################################################################
    # FUND ENDPOINTS
    ################################################################################

    ###############################################
    # Get fund
    ###############################################

    def get_funds(self) -> ControllerResponseDTO:
        """
        Get all funds.
        """
        try:
            search_data = getattr(request, 'validated_data', {})
            company_id = search_data.get('company_id')
            entity_id = search_data.get('entity_id')
            fund_status = search_data.get('fund_status')
            fund_tracking_type = search_data.get('fund_tracking_type')
            include_events = search_data.get('include_events', False)
            include_cash_flows = search_data.get('include_cash_flows', False)
            include_tax_statements = search_data.get('include_tax_statements', False)

            session = self._get_session()

            try:
                funds = self.fund_service.get_funds(
                    session=session,
                    company_id=company_id,
                    entity_id=entity_id,
                    fund_status=fund_status,
                    fund_tracking_type=fund_tracking_type
                )

                if funds is None:
                    return ControllerResponseDTO(error="Funds not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                if include_events or include_cash_flows or include_tax_statements:
                    for fund in funds:
                        if include_events:
                            fund.events = self.fund_event_service.get_fund_events(fund_ids=[fund.id], session=session)
                        if include_cash_flows:
                            fund.cash_flows = self.fund_event_cash_flow_service.get_fund_event_cash_flows(fund.id, session)
                        if include_tax_statements:
                            fund.tax_statements = self.fund_tax_statement_service.get_fund_tax_statements(fund.id, session)

                formatted_funds = [format_fund_comprehensive(fund, include_events=include_events, include_cash_flows=include_cash_flows, include_tax_statements=include_tax_statements) for fund in funds]
                return ControllerResponseDTO(data=formatted_funds, response_code=ApiResponseCode.SUCCESS)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting funds: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting funds: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error in get_funds: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_fund_by_id(self, fund_id: int) -> ControllerResponseDTO:
        """
        Get a fund by ID with optional detailed information.
        
        Args:
            fund_id: ID of the fund to retrieve
            
        Returns:
            ControllerResponseDTO: DTO containing fund data and status
        """
        try:
            # Get include_events, include_cash_flows, include_tax_statements flags from middleware
            search_data = getattr(request, 'validated_data', {})
            include_events = search_data.get('include_events', False)
            include_cash_flows = search_data.get('include_cash_flows', False)
            include_tax_statements = search_data.get('include_tax_statements', False)

            session = self._get_session()
            
            try:
                fund = self.fund_service.get_fund_by_id(fund_id, session)
                if not fund:
                    return ControllerResponseDTO(error="Fund not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                if include_events:
                    fund.events = self.fund_event_service.get_fund_events(fund_id, session)
                if include_cash_flows:
                    fund.cash_flows = self.fund_event_cash_flow_service.get_fund_event_cash_flows(fund_id, session)
                if include_tax_statements:
                    fund.tax_statements = self.fund_tax_statement_service.get_fund_tax_statements(fund_id, session)
                
                formatted_fund = format_fund_comprehensive(
                    fund, 
                    include_events=include_events, 
                    include_cash_flows=include_cash_flows,
                    include_tax_statements=include_tax_statements
                )

                return ControllerResponseDTO(data=formatted_fund, response_code=ApiResponseCode.SUCCESS)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting fund {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting fund {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting fund {fund_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create fund
    ###############################################
    
    def create_fund(self) -> ControllerResponseDTO:
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
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)
            
            # Get database session
            session = self._get_session()
            
            try:
                # Create the fund with validated data (now returns domain object)
                fund = self.fund_service.create_fund(fund_data, session)
                
                # Commit the transaction
                session.commit()
                
                # Format the response using formatter
                formatted_fund = format_fund(fund)
                return ControllerResponseDTO(data=formatted_fund, response_code=ApiResponseCode.CREATED)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating fund: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating fund: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()
                
        except Exception as e:
            current_app.logger.error(f"Error in create_fund: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    

    ###############################################
    # Delete fund
    ###############################################
    
    def delete_fund(self, fund_id: int) -> ControllerResponseDTO:
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
                    return ControllerResponseDTO(error="Fund not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                # Commit the transaction
                session.commit()
                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED, message="Fund deleted successfully")
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting fund {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=f"Fund deletion validation failed: {str(e)}", response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting fund {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)                
            finally:
                session.close()
            
        except Exception as e:
            current_app.logger.error(f"Error in delete_fund {fund_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
        
    
    ###############################################################################
    # FUND EVENTS ENDPOINTS
    ###############################################################################
    
    ###############################################
    # Get fund events
    ###############################################

    def get_fund_events(self, fund_id: int) -> ControllerResponseDTO:
        """
        Get all events for a specific fund - optimized for fast table updates.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            ControllerResponseDTO: DTO containing events and status
        """
        try:
            search_data = getattr(request, 'validated_data', {})
            if fund_id is None:
                fund_id = search_data.get('fund_id')

            session = self._get_session()

            try:
                # Get fund events - service returns a list directly
                events = self.fund_event_service.get_fund_events(fund_ids=[fund_id], session=session)

                if events is None:
                    return ControllerResponseDTO(error="Fund not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_events = [format_fund_event(event) for event in events]
                return ControllerResponseDTO(data=formatted_events, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting fund events {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting fund events {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error in get_fund_events {fund_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    
    def get_fund_event_by_id(self, fund_event_id: int) -> ControllerResponseDTO:
        """
        Get a fund event by ID.

        Args:
            fund_event_id: ID of the fund event
            
        Returns:
            ControllerResponseDTO: DTO containing event data or error
        """
        try:
            session = self._get_session()
            try:
                fund_event = self.fund_event_service.get_fund_event_by_id(fund_event_id, session)
                if fund_event is None:
                    return ControllerResponseDTO(error="Fund event not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_fund_event = format_fund_event(fund_event)
                return ControllerResponseDTO(data=formatted_fund_event, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting fund event by ID: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting fund event by ID: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error in get_fund_event_by_id {fund_event_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create fund event
    ###############################################

    def create_fund_event(self, fund_id: int, event_type: EventType) -> ControllerResponseDTO:
        """
        Add a fund event.

        Args:
            fund_id: ID of the fund
            event_type: Type of event
            
        Returns:
            ControllerResponseDTO: DTO containing event data or error
        """
        event_data = getattr(request, 'validated_data', {})
        if not event_data:
            return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)
        
        event_data['event_type'] = event_type
        
        try:
            session = self._get_session()
            try:
                event = self.fund_event_service.create_fund_event(fund_id, event_data, session)
                return ControllerResponseDTO(data=format_fund_event(event), response_code=ApiResponseCode.CREATED)
            except Exception as e:
                current_app.logger.error(f"Error in create_fund_event: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()
        except Exception as e:
            current_app.logger.error(f"Error in create_fund_event: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    

    # def create_capital_call(self, fund_id: int, event_data: dict) -> ControllerResponseDTO:
    #     """
    #     Add a capital call event.
        
    #     Args:
    #         fund_id: ID of the fund
    #         event_data: Validated event data from middleware
            
    #     Returns:
    #         ControllerResponseDTO: DTO containing event data or error
    #     """
        
    #     try:
    #         session = self._get_session()
            
    #         try:
    #             # Get the fund
    #             fund = self.fund_service.get_fund_by_id(fund_id, session)
    #             if not fund:
    #                 return ControllerResponseDTO(error="Fund not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

    #             event = self.fund_event_service.create_capital_call(
    #                 fund=fund,
    #                 amount=float(event_data['amount']),
    #                 call_date=event_data['event_date'],  # Already parsed by middleware
    #                 description=event_data.get('description'),
    #                 reference_number=event_data.get('reference_number'),
    #                 session=session
    #             )
                
    #             session.commit()
                
    #             formatted_event = format_event(event)
    #             return ControllerResponseDTO(data=formatted_event, response_code=ApiResponseCode.CREATED)
                
    #         except ValueError as e:
    #             current_app.logger.warning(f"Business logic error adding capital call {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
    #         except Exception as e:
    #             current_app.logger.error(f"Error adding capital call {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    #         finally:
    #             session.close()
                
    #     except Exception as e:
    #         current_app.logger.error(f"Error in create_capital_call {fund_id}: {str(e)}")
    #         return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    
    # def create_return_of_capital(self, fund_id: int, event_data: dict) -> ControllerResponseDTO:
    #     """
    #     Add a return of capital event.
        
    #     Args:
    #         fund_id: ID of the fund
    #         event_data: Validated event data from middleware
            
    #     Returns:
    #         ControllerResponseDTO: DTO containing event data or error
    #     """
        
    #     try:
    #         # Validate required fields (business validation)
    #         required_fields = ['amount', 'event_date']
    #         for field in required_fields:
    #             if field not in event_data:
    #                 return ControllerResponseDTO(error=f'Required field "{field}" is missing', response_code=ApiResponseCode.VALIDATION_ERROR)
            
    #         # Get database session
    #         session = self._get_session()
            
    #         try:
    #             # Get the fund
    #             fund = self.fund_service.get_fund_by_id(fund_id, session)
    #             if not fund:
    #                 return ControllerResponseDTO(error="Fund not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
    #             # Parse event date (business logic)
    #             event_date = event_data['event_date']
    #             if isinstance(event_date, str):
    #                 from datetime import datetime
    #                 event_date = datetime.fromisoformat(event_date).date()
                
    #             # Add the return of capital event using FundEventService
    #             event = self.fund_event_service.create_return_of_capital(
    #                 fund=fund,
    #                 amount=float(event_data['amount']),
    #                 return_date=event_date,
    #                 description=event_data.get('description'),
    #                 reference_number=event_data.get('reference_number'),
    #                 session=session
    #             )
                
    #             # Commit the transaction
    #             session.commit()
                
    #             # Format the event for response
    #             formatted_event = format_event(event)
    #             return ControllerResponseDTO(data=formatted_event, response_code=ApiResponseCode.CREATED)
                
    #         except ValueError as e:
    #             current_app.logger.warning(f"Business logic error adding return of capital {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
    #         except Exception as e:
    #             current_app.logger.error(f"Error adding return of capital {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    #         finally:
    #             session.close()
                
    #     except Exception as e:
    #         current_app.logger.error(f"Error in create_return_of_capital {fund_id}: {str(e)}")
    #         return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    
    # def create_unit_purchase(self, fund_id: int, event_data: dict) -> ControllerResponseDTO:
    #     """
    #     Add a unit purchase event.
        
    #     Args:
    #         fund_id: ID of the fund
    #         event_data: Validated event data from middleware
            
    #     Returns:
    #         ControllerResponseDTO: DTO containing event data or error
    #     """
        
    #     try:
    #         # Validate required fields (business validation)
    #         required_fields = ['units_purchased', 'unit_price', 'event_date']
    #         for field in required_fields:
    #             if field not in event_data:
    #                 return ControllerResponseDTO(error=f'Required field "{field}" is missing', response_code=ApiResponseCode.VALIDATION_ERROR)
            
    #         # Get database session
    #         session = self._get_session()
            
    #         try:
    #             # Get the fund
    #             fund = self.fund_service.get_fund_by_id(fund_id, session)
    #             if not fund:
    #                 return ControllerResponseDTO(error="Fund not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
    #             # Parse event date (business logic)
    #             event_date = event_data['event_date']
    #             if isinstance(event_date, str):
    #                 from datetime import datetime
    #                 event_date = datetime.fromisoformat(event_date).date()
                
    #             # Add the unit purchase event using FundEventService
    #             event = self.fund_event_service.create_unit_purchase(
    #                 fund=fund,
    #                 units=float(event_data['units_purchased']),
    #                 price=float(event_data['unit_price']),
    #                 date=event_date,
    #                 brokerage_fee=float(event_data.get('brokerage_fee', 0.0)),
    #                 description=event_data.get('description'),
    #                 reference_number=event_data.get('reference_number'),
    #                 session=session
    #             )
                
    #             # Commit the transaction
    #             session.commit()
                
    #             # Format the event for response
    #             formatted_event = format_event(event)
    #             return ControllerResponseDTO(data=formatted_event, response_code=ApiResponseCode.CREATED)
                
    #         except ValueError as e:
    #             current_app.logger.warning(f"Business logic error adding unit purchase {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
    #         except Exception as e:
    #             current_app.logger.error(f"Error adding unit purchase {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    #         finally:
    #             session.close()
                
    #     except Exception as e:
    #         current_app.logger.error(f"Error in create_unit_purchase {fund_id}: {str(e)}")
    #         return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    
    # def create_unit_sale(self, fund_id: int, event_data: dict) -> ControllerResponseDTO:
    #     """
    #     Add a unit sale event.
        
    #     Args:
    #         fund_id: ID of the fund
    #         event_data: Validated event data from middleware
            
    #     Returns:
    #         ControllerResponseDTO: DTO containing event data or error
    #     """
        
    #     try:
    #         # Validate required fields (business validation)
    #         required_fields = ['units_sold', 'unit_price', 'event_date']
    #         for field in required_fields:
    #             if field not in event_data:
    #                 return ControllerResponseDTO(error=f'Required field "{field}" is missing', response_code=ApiResponseCode.VALIDATION_ERROR)
            
    #         # Get database session
    #         session = self._get_session()
            
    #         try:
    #             # Get the fund
    #             fund = self.fund_service.get_fund(fund_id, session)
    #             if not fund:
    #                 return ControllerResponseDTO(error="Fund not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
    #             # Parse event date (business logic)
    #             event_date = event_data['event_date']
    #             if isinstance(event_date, str):
    #                 from datetime import datetime
    #                 event_date = datetime.fromisoformat(event_date).date()
                
    #             # Add the unit sale event using FundEventService
    #             event = self.fund_event_service.create_unit_sale(
    #                 fund=fund,
    #                 units=float(event_data['units_sold']),
    #                 price=float(event_data['unit_price']),
    #                 date=event_date,
    #                 brokerage_fee=float(event_data.get('brokerage_fee', 0.0)),
    #                 description=event_data.get('description'),
    #                 reference_number=event_data.get('reference_number'),
    #                 session=session
    #             )
                
    #             # Commit the transaction
    #             session.commit()
                
    #             # Format the event for response
    #             formatted_event = format_event(event)
    #             return ControllerResponseDTO(data=formatted_event, response_code=ApiResponseCode.CREATED)
                
    #         except ValueError as e:
    #             current_app.logger.warning(f"Business logic error adding unit sale {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
    #         except Exception as e:
    #             current_app.logger.error(f"Error adding unit sale {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    #         finally:
    #             session.close()
                
    #     except Exception as e:
    #         current_app.logger.error(f"Error in create_unit_sale {fund_id}: {str(e)}")
    #         return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    
    # def create_nav_update(self, fund_id: int, event_data: dict) -> ControllerResponseDTO:
    #     """
    #     Add a NAV update event.
        
    #     Args:
    #         fund_id: ID of the fund
    #         event_data: Validated event data from middleware
            
    #     Returns:
    #         ControllerResponseDTO: DTO containing event data or error
    #     """
        
    #     try:
    #         # Validate required fields (business validation)
    #         required_fields = ['nav_per_share', 'event_date']
    #         for field in required_fields:
    #             if field not in event_data:
    #                 return ControllerResponseDTO(error=f'Required field "{field}" is missing', response_code=ApiResponseCode.VALIDATION_ERROR)            

    #         session = self._get_session()
            
    #         try:
    #             fund = self.fund_service.get_fund(fund_id, session)
    #             if not fund:
    #                 return ControllerResponseDTO(error="Fund not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
    #             # Parse event date (business logic)
    #             event_date = event_data['event_date']
    #             if isinstance(event_date, str):
    #                 from datetime import datetime
    #                 event_date = datetime.fromisoformat(event_date).date()
                
    #             # Add the NAV update event using FundEventService
    #             event = self.fund_event_service.create_nav_update(
    #                 fund=fund,
    #                 nav_per_share=float(event_data['nav_per_share']),
    #                 date=event_date,
    #                 description=event_data.get('description'),
    #                 reference_number=event_data.get('reference_number'),
    #                 session=session
    #             )
                
    #             # Commit the transaction
    #             session.commit()
                
    #             # Format the event for response
    #             formatted_event = format_event(event)
    #             return ControllerResponseDTO(data=formatted_event, response_code=ApiResponseCode.CREATED)
                
    #         except ValueError as e:
    #             current_app.logger.warning(f"Business logic error adding NAV update {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
    #         except Exception as e:
    #             current_app.logger.error(f"Error adding NAV update {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    #         finally:
    #             session.close()
                
    #     except Exception as e:
    #         current_app.logger.error(f"Error in create_nav_update {fund_id}: {str(e)}")
    #         return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    
    # def create_distribution(self, fund_id: int, event_data: dict) -> ControllerResponseDTO:
    #     """
    #     Add a distribution event.
        
    #     Args:
    #         fund_id: ID of the fund
    #         event_data: Validated event data from middleware
            
    #     Returns:
    #         ControllerResponseDTO: DTO containing event data or error
    #     """
        
    #     try:
    #         # Validate required fields (business validation)
    #         required_fields = ['event_date', 'distribution_type']
    #         for field in required_fields:
    #             if field not in event_data:
    #                 return ControllerResponseDTO(error=f'Required field "{field}" is missing', response_code=ApiResponseCode.VALIDATION_ERROR)
            
    #         # Get database session
    #         session = self._get_session()
            
    #         try:
    #             # Get the fund
    #             fund = self.fund_service.get_fund(fund_id, session)
    #             if not fund:
    #                 return ControllerResponseDTO(error="Fund not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
    #             # Parse event date (business logic)
    #             event_date = event_data['event_date']
    #             if isinstance(event_date, str):
    #                 from datetime import datetime
    #                 event_date = datetime.fromisoformat(event_date).date()
                
    #             # Parse distribution type (business logic)
    #             from src.fund.enums import DistributionType
    #             distribution_type = DistributionType(event_data['distribution_type'])
                
    #             # Handle withholding tax distributions (business logic)
    #             if (event_data.get('distribution_type') == 'INTEREST' and
    #                 any([
    #                     event_data.get('interest_gross_amount') is not None,
    #                     event_data.get('interest_net_amount') is not None,
    #                     event_data.get('interest_withholding_tax_amount') is not None,
    #                     event_data.get('interest_withholding_tax_rate') is not None
    #                 ])):
    #                 # Withholding tax distribution
    #                 event = self.fund_event_service.create_distribution(
    #                     fund=fund,
    #                     event_date=event_date,
    #                     distribution_type=distribution_type,
    #                     has_withholding_tax=True,
    #                     gross_interest_amount=float(event_data.get('interest_gross_amount', 0)) if event_data.get('interest_gross_amount') else None,
    #                     net_interest_amount=float(event_data.get('interest_net_amount', 0)) if event_data.get('interest_net_amount') else None,
    #                     withholding_tax_amount=float(event_data.get('interest_withholding_tax_amount', 0)) if event_data.get('interest_withholding_tax_amount') else None,
    #                     withholding_tax_rate=float(event_data.get('interest_withholding_tax_rate', 0)) if event_data.get('interest_withholding_tax_rate') else None,
    #                     description=event_data.get('description'),
    #                     reference_number=event_data.get('reference_number'),
    #                     session=session
    #                 )
    #             else:
    #                 # Simple distribution
    #                 if 'amount' not in event_data:
    #                     return ControllerResponseDTO(error='Required field "amount" is missing for simple distribution', response_code=ApiResponseCode.VALIDATION_ERROR)
                    
    #                 event = self.fund_event_service.create_distribution(
    #                     fund=fund,
    #                     event_date=event_date,
    #                     distribution_type=distribution_type,
    #                     distribution_amount=float(event_data['amount']),
    #                     has_withholding_tax=False,
    #                     description=event_data.get('description'),
    #                     reference_number=event_data.get('reference_number'),
    #                     session=session
    #                 )
                
    #             # Commit the transaction
    #             session.commit()
                
    #             # Format the event for response
    #             formatted_event = format_event(event)
    #             return ControllerResponseDTO(data=formatted_event, response_code=ApiResponseCode.CREATED)
                
    #         except ValueError as e:
    #             current_app.logger.warning(f"Business logic error adding distribution {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
    #         except Exception as e:
    #             current_app.logger.error(f"Error adding distribution {fund_id}: {str(e)}")
    #             session.rollback()
    #             return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    #         finally:
    #             session.close()
                
    #     except Exception as e:
    #         current_app.logger.error(f"Error in create_distribution {fund_id}: {str(e)}")
    #         return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Delete fund event
    ###############################################
    
    def delete_fund_event(self, fund_id: int, event_id: int) -> ControllerResponseDTO:
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
                    return ControllerResponseDTO(error="Event not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                session.commit()
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting fund event {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting fund event {fund_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()
        except Exception as e:
            current_app.logger.error(f"Error in delete_fund_event {fund_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    
    
    ###############################################################
    # FUND EVENT CASH FLOWS ENDPOINTS
    ###############################################################

    ###############################################
    # Get fund event cash flows
    ###############################################
    
    def get_fund_event_cash_flows(self, fund_id: int = None, fund_event_id: int = None) -> ControllerResponseDTO:
        """
        Get all cash flows for a specific fund event.
        
        Args:
            fund_id: ID of the fund
            fund_event_id: ID of the event

        Search parameters (all optional):
            fund_id: ID of the fund
            fund_event_id: ID of the event

        Returns:
            ControllerResponseDTO: DTO containing cash flow data or error
        """
        try:
            search_data = getattr(request, 'validated_data', {})
            if fund_id is None:
                fund_id = search_data.get('fund_id')
            if fund_event_id is None:
                fund_event_id = search_data.get('fund_event_id')
            bank_account_id = search_data.get('bank_account_id')
            session = self._get_session()
            try:
                fund_event_cash_flows = self.fund_event_cash_flow_service.get_fund_event_cash_flows(
                    session=session,
                    fund_id=fund_id,
                    fund_event_id=fund_event_id,
                    bank_account_id=bank_account_id
                )
                if fund_event_cash_flows is None:
                    return ControllerResponseDTO(error="Cash flows not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                formatted_cash_flows = [format_fund_event_cash_flow(cash_flow) for cash_flow in fund_event_cash_flows]
                return ControllerResponseDTO(data=formatted_cash_flows, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting fund event cash flows: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting fund event cash flows: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting fund event cash flows: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_fund_event_cash_flow_by_id(self, fund_event_cash_flow_id: int) -> ControllerResponseDTO:
        """
        Get a cash flow by ID.
        """
        try:
            session = self._get_session()
            try:
                fund_event_cash_flow = self.fund_event_cash_flow_service.get_fund_event_cash_flow_by_id(fund_event_cash_flow_id, session)
                if fund_event_cash_flow is None:
                    return ControllerResponseDTO(error="Cash flow not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                formatted_cash_flow = format_fund_event_cash_flow(fund_event_cash_flow)
                return ControllerResponseDTO(data=formatted_cash_flow, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting fund event cash flow by ID: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting fund event cash flow by ID: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting fund event cash flow by ID: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create fund event cash flow
    ###############################################
    
    def create_fund_event_cash_flow(self, fund_event_id: int) -> ControllerResponseDTO:
        """
        Add a cash flow to a fund event with pre-validated data.
        
        Args:
            fund_event_id: ID of the fund event
            
        Returns:
            ControllerResponseDTO: DTO containing cash flow data or error
        """
        try:
            fund_event_cash_flow_data = getattr(request, 'validated_data', {})
            if not fund_event_cash_flow_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)
            
            session = self._get_session()
            
            try:
                fund_event_cash_flow = self.fund_event_cash_flow_service.create_fund_event_cash_flow(fund_event_id, fund_event_cash_flow_data, session)
                if fund_event_cash_flow is None:
                    return ControllerResponseDTO(error="Cash flow not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                formatted_cash_flow = format_fund_event_cash_flow(fund_event_cash_flow)
                return ControllerResponseDTO(data=formatted_cash_flow, response_code=ApiResponseCode.CREATED)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error adding fund event cash flow: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error adding fund event cash flow: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error in create_fund_event_cash_flow: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Delete fund event cash flow
    ###############################################
    
    def delete_fund_event_cash_flow(self, cash_flow_event_id: int) -> ControllerResponseDTO:
        """
        Delete a cash flow from a fund event.
        
        Args:
            cash_flow_event_id: ID of the cash flow to delete
            
        Returns:
            ControllerResponseDTO: DTO containing status or error
        """
        try:
            session = self._get_session()
            try:
                success = self.fund_event_cash_flow_service.delete_fund_event_cash_flow(cash_flow_event_id, session)
                if not success:
                    return ControllerResponseDTO(error="Cash flow not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting fund event cash flow: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting fund event cash flow: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error in delete_fund_event_cash_flow: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ################################################################################
    # FUND TAX STATEMENT ENDPOINTS
    ################################################################################

    ###############################################
    # Get fund tax statements
    ###############################################

    def get_fund_tax_statements(self, fund_id: Optional[int] = None) -> ControllerResponseDTO:
        """
        Get all tax statements for a specific fund.

        Args:
            fund_id: ID of the fund

        Search parameters (all optional):
            fund_id: ID of the fund
            entity_id: ID of the entity
            financial_year: Financial year
            start_tax_payment_date: Start tax payment date
            end_tax_payment_date: End tax payment date

        Returns:
            ControllerResponseDTO: DTO containing tax statement data or error
        """
        try:
            search_data = getattr(request, 'validated_data', {})
            if fund_id is None:
                fund_id = search_data.get('fund_id')
            entity_id = search_data.get('entity_id')
            financial_year = search_data.get('financial_year')
            start_tax_payment_date = search_data.get('start_tax_payment_date')
            end_tax_payment_date = search_data.get('end_tax_payment_date')
            session = self._get_session()
            try:
                fund_tax_statements = self.fund_tax_statement_service.get_fund_tax_statements(
                    session=session,
                    fund_id=fund_id,
                    entity_id=entity_id,
                    financial_year=financial_year,
                    start_tax_payment_date=start_tax_payment_date,
                    end_tax_payment_date=end_tax_payment_date
                )
                if fund_tax_statements is None:
                    return ControllerResponseDTO(error="Tax statements not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_fund_tax_statements = [format_fund_tax_statement(fund_tax_statement) for fund_tax_statement in fund_tax_statements]
                return ControllerResponseDTO(data=formatted_fund_tax_statements, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting fund tax statements: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting fund tax statements: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting fund tax statements: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_fund_tax_statement_by_id(self, fund_tax_statement_id: int) -> ControllerResponseDTO:
        """
        Get a tax statement by ID.

        Args:
            fund_tax_statement_id: ID of the tax statement
            
        Returns:
            ControllerResponseDTO: DTO containing tax statement data or error
        """
        try:
            session = self._get_session()
            try:
                fund_tax_statement = self.fund_tax_statement_service.get_fund_tax_statement_by_id(fund_tax_statement_id, session)
                if fund_tax_statement is None:
                    return ControllerResponseDTO(error="Tax statement not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_fund_tax_statement = format_fund_tax_statement(fund_tax_statement)
                return ControllerResponseDTO(data=formatted_fund_tax_statement, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting fund tax statement by ID: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting fund tax statement by ID: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting fund tax statement by ID: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create fund tax statement
    ###############################################
    
    def create_fund_tax_statement(self, fund_id: int) -> ControllerResponseDTO:
        """
        Create a tax statement.

        Args:
            fund_id: ID of the fund

        Returns:
            ControllerResponseDTO: DTO containing tax statement data or error
        """
        try:
            fund_tax_statement_data = getattr(request, 'validated_data', {})
            if not fund_tax_statement_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)
            
            session = self._get_session()
            try:
                fund_tax_statement = self.fund_tax_statement_service.create_fund_tax_statement(fund_id, fund_tax_statement_data, session)
                
                session.commit()
                
                formatted_fund_tax_statement = format_fund_tax_statement(fund_tax_statement)
                return ControllerResponseDTO(data=formatted_fund_tax_statement, response_code=ApiResponseCode.CREATED)
            
            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating fund tax statement: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating fund tax statement: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error creating fund tax statement: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Delete fund tax statement
    ###############################################
    
    def delete_fund_tax_statement(self, fund_tax_statement_id: int) -> ControllerResponseDTO:
        """
        Delete a tax statement.

        Args:
            fund_tax_statement_id: ID of the tax statement
            
        Returns:
            ControllerResponseDTO: DTO containing tax statement data or error
        """
        try:
            session = self._get_session()
            try:
                success = self.fund_tax_statement_service.delete_fund_tax_statement(fund_tax_statement_id, session)
                if not success:
                    return ControllerResponseDTO(error="Tax statement not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting fund tax statement: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting fund tax statement: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error deleting fund tax statement: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


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