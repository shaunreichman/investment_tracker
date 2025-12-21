"""
Fund API Controller.
"""

from flask import request, current_app
from sqlalchemy.orm import Session

from src.fund.services.fund_service import FundService
from src.fund.services.fund_event_service import FundEventService
from src.fund.services.fund_event_cash_flow_service import FundEventCashFlowService
from src.fund.services.fund_tax_statement_service import FundTaxStatementService
from src.api.controllers.formatters.fund_formatter import format_fund_comprehensive, format_fund, format_fund_event, format_fund_event_cash_flow, format_fund_tax_statement, format_fund_event_comprehensive
from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.dto.response_codes import ApiResponseCode
from typing import Optional
from src.fund.enums.fund_event_enums import EventType
from src.shared.exceptions import ValidationException


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

        Search parameters (all optional):
            company_id: Filter by company ID
            company_ids: Filter by company IDs
            entity_id: Filter by entity ID
            entity_ids: Filter by entity IDs
            fund_status: Filter by fund status
            fund_statuses: Filter by fund statuses
            fund_tracking_type: Filter by fund tracking type
            fund_tracking_types: Filter by fund tracking types
            start_start_date: Filter by start start date
            end_start_date: Filter by end start date
            start_end_date: Filter by start end date
            end_end_date: Filter by end end date
            sort_by: Sort by
            sort_order: Sort order
            include_fund_events: Whether to include events
            include_fund_event_cash_flows: Whether to include cash flows
            include_fund_tax_statements: Whether to include tax statements

        Returns:
            ControllerResponseDTO containing funds data or error
        """
        try:
            # Get search data from middleware (all optional)
            search_data = getattr(request, 'validated_data', {})
            
            # Normalize single values to arrays for service layer
            if 'company_id' in search_data:
                search_data['company_ids'] = [search_data['company_id']]
            if 'entity_id' in search_data:
                search_data['entity_ids'] = [search_data['entity_id']]
            if 'fund_status' in search_data:
                search_data['fund_statuses'] = [search_data['fund_status']]
            if 'fund_tracking_type' in search_data:
                search_data['fund_tracking_types'] = [search_data['fund_tracking_type']]

            # Extract search parameters (None if not provided)
            company_ids = search_data.get('company_ids')
            entity_ids = search_data.get('entity_ids')
            fund_statuses = search_data.get('fund_statuses')
            fund_tracking_types = search_data.get('fund_tracking_types')
            start_start_date = search_data.get('start_start_date')
            end_start_date = search_data.get('end_start_date')
            start_end_date = search_data.get('start_end_date')
            end_end_date = search_data.get('end_end_date')
            sort_by = search_data.get('sort_by')
            sort_order = search_data.get('sort_order')

            include_fund_events = search_data.get('include_fund_events', False)
            include_fund_event_cash_flows = search_data.get('include_fund_event_cash_flows', False)
            include_fund_tax_statements = search_data.get('include_fund_tax_statements', False)

            session = self._get_session()

            try:
                funds = self.fund_service.get_funds(
                    session=session,
                    company_ids=company_ids,
                    entity_ids=entity_ids,
                    fund_statuses=fund_statuses,
                    fund_tracking_types=fund_tracking_types,
                    start_start_date=start_start_date,
                    end_start_date=end_start_date,
                    start_end_date=start_end_date,
                    end_end_date=end_end_date,
                    sort_by=sort_by,
                    sort_order=sort_order,
                    include_fund_events=include_fund_events,
                    include_fund_event_cash_flows=include_fund_event_cash_flows,
                    include_fund_tax_statements=include_fund_tax_statements
                )

                if funds is None:
                    return ControllerResponseDTO(error="No funds found matching the specified criteria", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_funds = [format_fund_comprehensive(fund, include_fund_events, include_fund_event_cash_flows, include_fund_tax_statements) for fund in funds]
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
            
        Search parameters (all optional):
            include_fund_events: Whether to include events
            include_fund_event_cash_flows: Whether to include cash flows
            include_fund_tax_statements: Whether to include tax statements

        Returns:
            ControllerResponseDTO containing fund data or error
        """
        try:
            search_data = getattr(request, 'validated_data', {})

            include_fund_events = search_data.get('include_fund_events', False)
            include_fund_event_cash_flows = search_data.get('include_fund_event_cash_flows', False)
            include_fund_tax_statements = search_data.get('include_fund_tax_statements', False)

            session = self._get_session()
            
            try:
                fund = self.fund_service.get_fund_by_id(fund_id, session, include_fund_events, include_fund_event_cash_flows, include_fund_tax_statements)
                if not fund:
                    return ControllerResponseDTO(error=f"Fund with ID {fund_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_fund = format_fund_comprehensive(fund, include_fund_events, include_fund_event_cash_flows, include_fund_tax_statements)

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
            ControllerResponseDTO containing fund data or error            
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
                
            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating fund: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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
            ControllerResponseDTO containing status or error
        """
        try:
            # Get database session
            session = self._get_session()
            
            try:
                # Delete the fund (now includes validation)
                success = self.fund_service.delete_fund(fund_id, session)
                
                if not success:
                    return ControllerResponseDTO(error=f"Fund with ID {fund_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                # Commit the transaction
                session.commit()
                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED, message="Fund deleted successfully")
                
            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting fund {fund_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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

        Search parameters (all optional):
            fund_id: Filter by fund ID
            fund_ids: Filter by fund IDs
            event_type: Filter by event type
            event_types: Filter by event types
            distribution_type: Filter by distribution type
            distribution_types: Filter by distribution types
            tax_payment_type: Filter by tax payment type
            tax_payment_types: Filter by tax payment types
            group_id: Filter by group ID
            group_ids: Filter by group IDs
            group_type: Filter by group type
            group_types: Filter by group types
            is_cash_flow_complete: Filter by cash flow completeness
            start_event_date: Filter by start event date
            end_event_date: Filter by end event date
            sort_by: Sort by
            sort_order: Sort order
            include_fund_event_cash_flows: Whether to include cash flows
            
        Returns:
            ControllerResponseDTO containing events or error
        """
        try:
            search_data = getattr(request, 'validated_data', {})
            
            # Normalize single values to arrays for service layer
            if fund_id:
                search_data['fund_ids'] = [fund_id]
            elif 'fund_id' in search_data:
                search_data['fund_ids'] = [search_data['fund_id']]
            if 'event_type' in search_data:
                search_data['event_types'] = [search_data['event_type']]
            if 'distribution_type' in search_data:
                search_data['distribution_types'] = [search_data['distribution_type']]
            if 'tax_payment_type' in search_data:
                search_data['tax_payment_types'] = [search_data['tax_payment_type']]
            if 'group_id' in search_data:
                search_data['group_ids'] = [search_data['group_id']]
            if 'group_type' in search_data:
                search_data['group_types'] = [search_data['group_type']]
                
            fund_ids = search_data.get('fund_ids')
            event_types = search_data.get('event_types')
            distribution_types = search_data.get('distribution_types')
            tax_payment_types = search_data.get('tax_payment_types')
            group_ids = search_data.get('group_ids')
            group_types = search_data.get('group_types')
            start_event_date = search_data.get('start_event_date')
            end_event_date = search_data.get('end_event_date')
            sort_by = search_data.get('sort_by')
            sort_order = search_data.get('sort_order')

            include_fund_event_cash_flows = search_data.get('include_fund_event_cash_flows', False)

            session = self._get_session()

            try:
                # Get fund events - service returns a list directly
                events = self.fund_event_service.get_fund_events(
                    session=session,
                    fund_ids=fund_ids,
                    event_types=event_types,
                    distribution_types=distribution_types,
                    tax_payment_types=tax_payment_types,
                    group_ids=group_ids,
                    group_types=group_types,
                    start_event_date=start_event_date,
                    end_event_date=end_event_date,
                    sort_by=sort_by,
                    sort_order=sort_order,
                    include_fund_event_cash_flows=include_fund_event_cash_flows
                )

                if events is None:
                    return ControllerResponseDTO(error="No fund events found matching the specified criteria", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
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

        Search parameters (all optional):
            include_fund_event_cash_flows: Whether to include cash flows
            
        Returns:
            ControllerResponseDTO: DTO containing event data or error
        """
        try:
            search_data = getattr(request, 'validated_data', {})

            include_fund_event_cash_flows = search_data.get('include_fund_event_cash_flows', False)

            session = self._get_session()
            try:
                fund_event = self.fund_event_service.get_fund_event_by_id(fund_event_id, session, include_fund_event_cash_flows)
                if fund_event is None:
                    return ControllerResponseDTO(error=f"Fund event with ID {fund_event_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_fund_event = format_fund_event_comprehensive(fund_event, include_fund_event_cash_flows)
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

                session.commit()
                
                return ControllerResponseDTO(data=format_fund_event(event), response_code=ApiResponseCode.CREATED)
            
            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating fund event: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating fund event: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error in create_fund_event: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()
        except Exception as e:
            current_app.logger.error(f"Error in create_fund_event: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    

    ###############################################
    # Delete fund event
    ###############################################
    
    def delete_fund_event(self, fund_event_id: int) -> ControllerResponseDTO:
        """
        Delete a fund event.
        
        Args:
            fund_event_id: ID of the fund event to delete
            
        Returns:
            ControllerResponseDTO: DTO containing status or error
        """
        try:
            # Get database session
            session = self._get_session()
            try:
                success = self.fund_event_service.delete_fund_event(fund_event_id, session)
                if not success:
                    return ControllerResponseDTO(error=f"Fund event with ID {fund_event_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                session.commit()
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
            
            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting fund event {fund_event_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting fund event {fund_event_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting fund event {fund_event_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()
        except Exception as e:
            current_app.logger.error(f"Error in delete_fund_event {fund_event_id}: {str(e)}")
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
            fund_ids: IDs of the funds
            fund_event_id: ID of the event
            fund_event_ids: IDs of the events
            bank_account_id: ID of the bank account
            bank_account_ids: IDs of the bank accounts
            different_month: Whether the transfer date is in a different month to the fund event date
            adjusted_bank_account_balance_id: ID of the bank account balance
            adjusted_bank_account_balance_ids: IDs of the bank account balances
            currency: Currency
            currencies: Currencies
            start_transfer_date: Start date of the transfer date
            end_transfer_date: End date of the transfer date
            start_fund_event_date: Start date of the fund event date
            end_fund_event_date: End date of the fund event date
            sort_by: Field to sort by
            sort_order: Sort order

        Returns:
            ControllerResponseDTO: DTO containing cash flow data or error
        """
        try:
            search_data = getattr(request, 'validated_data', {})
            
            # Normalize single values to arrays for service layer
            if fund_id:
                search_data['fund_ids'] = [fund_id]
            elif 'fund_id' in search_data:
                search_data['fund_ids'] = [search_data['fund_id']]
            if fund_event_id:
                search_data['fund_event_ids'] = [fund_event_id]
            elif 'fund_event_id' in search_data:
                search_data['fund_event_ids'] = [search_data['fund_event_id']]
            if 'bank_account_id' in search_data:
                search_data['bank_account_ids'] = [search_data['bank_account_id']]
            if 'adjusted_bank_account_balance_id' in search_data:
                search_data['adjusted_bank_account_balance_ids'] = [search_data['adjusted_bank_account_balance_id']]
            if 'currency' in search_data:
                search_data['currencies'] = [search_data['currency']]
            
            fund_ids = search_data.get('fund_ids')
            fund_event_ids = search_data.get('fund_event_ids')
            bank_account_ids = search_data.get('bank_account_ids')
            adjusted_bank_account_balance_ids = search_data.get('adjusted_bank_account_balance_ids')
            currencies = search_data.get('currencies')
            start_transfer_date = search_data.get('start_transfer_date')
            end_transfer_date = search_data.get('end_transfer_date')
            start_fund_event_date = search_data.get('start_fund_event_date')
            end_fund_event_date = search_data.get('end_fund_event_date')
            sort_by = search_data.get('sort_by')
            sort_order = search_data.get('sort_order')

            session = self._get_session()
            try:
                fund_event_cash_flows = self.fund_event_cash_flow_service.get_fund_event_cash_flows(
                    session=session,
                    fund_ids=fund_ids,
                    fund_event_ids=fund_event_ids,
                    bank_account_ids=bank_account_ids,
                    adjusted_bank_account_balance_ids=adjusted_bank_account_balance_ids,
                    currencies=currencies,
                    start_transfer_date=start_transfer_date,
                    end_transfer_date=end_transfer_date,
                    start_fund_event_date=start_fund_event_date,
                    end_fund_event_date=end_fund_event_date,
                    sort_by=sort_by,
                    sort_order=sort_order
                )
                if fund_event_cash_flows is None:
                    return ControllerResponseDTO(error="No fund event cash flows found matching the specified criteria", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
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
        Get a fund event cash flow by ID.

        Args:
            fund_event_cash_flow_id: ID of the cash flow

        Returns:
            ControllerResponseDTO: DTO containing cash flow data or error
        """
        try:
            session = self._get_session()
            try:
                fund_event_cash_flow = self.fund_event_cash_flow_service.get_fund_event_cash_flow_by_id(fund_event_cash_flow_id, session)
                if fund_event_cash_flow is None:
                    return ControllerResponseDTO(error=f"Fund event cash flow with ID {fund_event_cash_flow_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
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
                    return ControllerResponseDTO(error=f"Failed to create fund event cash flow for event ID {fund_event_id}", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
                formatted_cash_flow = format_fund_event_cash_flow(fund_event_cash_flow)
                return ControllerResponseDTO(data=formatted_cash_flow, response_code=ApiResponseCode.CREATED)

            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating fund event cash flow: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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
                    return ControllerResponseDTO(error=f"Fund event cash flow with ID {cash_flow_event_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
            
            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting fund event cash flow {cash_flow_event_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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
        Get all tax statements.

        Args:
            fund_id: ID of the fund

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
            ControllerResponseDTO: DTO containing tax statement data or error
        """
        try:
            search_data = getattr(request, 'validated_data', {})
            
            # Normalize single values to arrays for service layer
            if fund_id:
                search_data['fund_ids'] = [fund_id]
            elif 'fund_id' in search_data:
                search_data['fund_ids'] = [search_data['fund_id']]
            if 'entity_id' in search_data:
                search_data['entity_ids'] = [search_data['entity_id']]
            if 'financial_year' in search_data:
                search_data['financial_years'] = [search_data['financial_year']]
            
            fund_ids = search_data.get('fund_ids')
            entity_ids = search_data.get('entity_ids')
            financial_years = search_data.get('financial_years')
            start_tax_payment_date = search_data.get('start_tax_payment_date')
            end_tax_payment_date = search_data.get('end_tax_payment_date')
            sort_by = search_data.get('sort_by')
            sort_order = search_data.get('sort_order')

            session = self._get_session()
            try:
                fund_tax_statements = self.fund_tax_statement_service.get_fund_tax_statements(
                    session=session,
                    fund_ids=fund_ids,
                    entity_ids=entity_ids,
                    financial_years=financial_years,
                    start_tax_payment_date=start_tax_payment_date,
                    end_tax_payment_date=end_tax_payment_date,
                    sort_by=sort_by,
                    sort_order=sort_order
                )
                if fund_tax_statements is None:
                    return ControllerResponseDTO(error="No fund tax statements found matching the specified criteria", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

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
        Get a fund tax statement by ID.

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
                    return ControllerResponseDTO(error=f"Fund tax statement with ID {fund_tax_statement_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

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
        Create a fund tax statement.

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
            
            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating fund tax statement: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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
                    return ControllerResponseDTO(error=f"Fund tax statement with ID {fund_tax_statement_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)

            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting fund tax statement {fund_tax_statement_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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


    ###############################################
    # Get fund financial years
    ###############################################
    
    def get_fund_financial_years_and_last_day_of_financial_year(self, fund_id: int) -> ControllerResponseDTO:
        """
        Get the financial years and last day of financial year for a fund.

        Args:
            fund_id: ID of the fund

        Returns:
            ControllerResponseDTO: DTO containing financial years and last day of financial year data or error
        """
        try:
            session = self._get_session()
            try:
                from src.fund.services.fund_date_service import FundDateService
                fund_date_service = FundDateService()
                financial_years_and_last_day_of_financial_year = fund_date_service.get_fund_financial_years_and_last_day_of_financial_year(fund_id, session)
                if financial_years_and_last_day_of_financial_year is None:
                    return ControllerResponseDTO(error=f"Fund financial years and last day of financial year not found for fund ID {fund_id}", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                return ControllerResponseDTO(data=financial_years_and_last_day_of_financial_year, response_code=ApiResponseCode.SUCCESS)
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting fund financial years and last day of financial year: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting fund financial years and last day of financial year: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting fund financial years and last day of financial year: {str(e)}")
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