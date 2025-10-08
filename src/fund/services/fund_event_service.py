"""
Fund Event Service.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from src.fund.models import FundEvent
from src.fund.enums.fund_event_enums import EventType, DistributionType, TaxPaymentType, GroupType, SortFieldFundEvent
from src.shared.enums.shared_enums import EventOperation, SortOrder
from src.fund.repositories import FundEventRepository
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.services.fund_event_secondary_service import FundEventSecondaryService
from src.shared.enums.domain_update_event_enums import DomainObjectType

class FundEventService:
    """
    Fund Event Service.

    This module provides the FundEventService class, which handles fund event operations and business logic.
    The service provides clean separation of concerns for:
    - Fund event retrieval
    - Fund event creation
        - Calculation of distribution event data
        - Calculation of tax event data
        - Handling of secondary impacts
    - Fund event deletion with dependency checking

    The service uses the FundEventRepository to perform CRUD operations and the FundValidationService to validate fund events.
    The service is used by the FundEventController to handle fund event operations.
    """
    
    def __init__(self): 
        """
        Initialize the FundEventService with specialized repositories.

        Args:
            fund_event_repository: Fund event repository to use. If None, creates a new one.
            fund_validation_service: Fund validation service to use. If None, creates a new one.
            fund_event_secondary_service: Fund event secondary service to use. If None, creates a new one.
        """
        self.fund_event_repository = FundEventRepository()
        self.fund_validation_service = FundValidationService()
        self.fund_event_secondary_service = FundEventSecondaryService()
    

    def get_fund_events(self, session: Session,
                       fund_ids: Optional[List[int]] = None,
                       event_types: Optional[List[EventType]] = None,
                       distribution_types: Optional[List[DistributionType]] = None,
                       tax_payment_types: Optional[List[TaxPaymentType]] = None,
                       group_ids: Optional[List[int]] = None,
                       group_types: Optional[List[GroupType]] = None,
                       is_cash_flow_complete: Optional[bool] = None,
                       start_event_date: Optional[date] = None,
                       end_event_date: Optional[date] = None,
                       sort_by: Optional[SortFieldFundEvent] = SortFieldFundEvent.EVENT_DATE,
                       sort_order: Optional[SortOrder] = SortOrder.ASC,
                       include_fund_event_cash_flows: Optional[bool] = False
    ) -> List['FundEvent']:
        """
        Get events for a specific fund or list of funds.
        
        Args:
            session: Database session
            fund_ids: Optional list of fund IDs
            event_types: Optional list of event types to filter by
            distribution_types: Optional list of distribution types to filter by
            tax_payment_types: Optional list of tax payment types to filter by
            group_ids: Optional list of group IDs to filter by
            group_types: Optional list of group types to filter by
            is_cash_flow_complete: Optional flag to filter by cash flow completeness
            start_event_date: Optional start event date to filter by
            end_event_date: Optional end event date to filter by
            sort_by: Optional sort field to sort by
            sort_order: Optional sort order to sort by
            include_fund_event_cash_flows: Optional flag to eager load cash flows relationship (optional)

        Returns:
            List of FundEvent objects
        """
        return self.fund_event_repository.get_fund_events(
            session, fund_ids, event_types, distribution_types, tax_payment_types, group_ids, group_types, is_cash_flow_complete, start_event_date, end_event_date, sort_by, sort_order, include_fund_event_cash_flows
        )
    
    def get_fund_event_by_id(self, event_id: int, session: Session, include_fund_event_cash_flows: Optional[bool] = False) -> Optional['FundEvent']:
        """
        Get a specific fund event by ID.
        
        Args:
            event_id: ID of the event
            session: Database session
            include_fund_event_cash_flows: Optional flag to eager load cash flows relationship (optional)
            
        Returns:
            FundEvent object if found, None otherwise
        """
        # Get the specific event
        event = self.fund_event_repository.get_fund_event_by_id(event_id, session, include_fund_event_cash_flows)
        if not event:
            return None
        
        return event


    ################################################################################
    # Create Fund Event
    ################################################################################

    def create_fund_event(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Add a fund event.

        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session

        Returns:
            FundEvent object
        """
        processed_data = event_data.copy()

        # 1. Add the fund id to the event data
        processed_data['fund_id'] = fund_id

        # 2. Business validation using validation service
        errors = self.fund_validation_service.validate_fund_event_creation(processed_data, session)
        if errors:
            raise ValueError(f"Validation errors for fund event creation for fund ID {fund_id}: {errors}")

        # 2a. Calculate the distribution event data
        if processed_data['event_type'] == EventType.DISTRIBUTION:
            processed_data = self._calculate_distribution_event_data(processed_data, session)
            if processed_data['has_withholding_tax']:
                # Create the tax event
                tax_data = self._calculate_tax_event_data(processed_data)
                tax_event = self.fund_event_repository.create_fund_event(tax_data, session)
        
        # 2b. Calculate the unit transaction event data
        elif processed_data['event_type'] in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]:
            processed_data = self._calculate_unit_transaction_event_data(processed_data)

        # 3. Create the fund event
        fund_event = self.fund_event_repository.create_fund_event(processed_data, session)
        
        # 3a. Flush the event to database so it's available for secondary service
        session.flush()

        # 4. Handle the secondary impacts
        self.fund_event_secondary_service.handle_event_secondary_impact(
            fund_id=fund_event.fund_id,
            domain_object_type=DomainObjectType.FUND_EVENT,
            event_operation=EventOperation.CREATE,
            session=session,
            fund_event_type=processed_data['event_type'],
            object_id=fund_event.id
        )
        
        return fund_event
    
    def _calculate_distribution_event_data(self, event_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
        """
        Calculate distribution event data based on parameters.
        
        This method handles the complex logic for both simple distributions
        and withholding tax distributions.
        """        
        processed_data = event_data.copy()

        if processed_data['has_withholding_tax']:
            # Complex withholding tax distribution
            from src.fund.calculators.withholding_tax_calculator import WithholdingTaxCalculator
            gross_amount, tax_amount = WithholdingTaxCalculator.calculate_withholding_tax_amounts(
                processed_data.get('gross_interest_amount'), processed_data.get('net_interest_amount'), processed_data.get('withholding_tax_amount'), processed_data.get('withholding_tax_rate'))
            
            processed_data.update({
                'amount': gross_amount,  # Store gross amount for IRR calculations
                'tax_withholding': tax_amount,  # Tax amount withheld
                'has_withholding_tax': True
            })

            # Clean up temporary calculation fields
            temp_fields = ['gross_interest_amount', 'net_interest_amount', 'withholding_tax_amount', 'withholding_tax_rate']
            for field in temp_fields:
                processed_data.pop(field, None)

            group_id = self.fund_event_repository.generate_group_id(session)
            processed_data['group_id'] = group_id
            processed_data['group_type'] = GroupType.INTEREST_WITHHOLDING
            processed_data['is_grouped'] = True
            processed_data['group_position'] = 0
        else:
            processed_data.update({
                'tax_withholding': 0.0,
                'has_withholding_tax': False
            })
        
        return processed_data

    def _calculate_tax_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate tax event data based on parameters.
        """
        tax_event_data = dict()
        tax_event_data['event_type'] = EventType.TAX_PAYMENT
        tax_event_data['event_date'] = event_data.get('event_date')
        tax_event_data['fund_id'] = event_data.get('fund_id')
        tax_event_data['description'] = event_data.get('description')
        tax_event_data['reference_number'] = event_data.get('reference_number')
        tax_event_data['amount'] = -event_data.get('tax_withholding', 0)
        tax_event_data['tax_payment_type'] = TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        tax_event_data['group_id'] = event_data.get('group_id')
        tax_event_data['group_type'] = GroupType.INTEREST_WITHHOLDING
        tax_event_data['is_grouped'] = True
        tax_event_data['group_position'] = 1
        
        return tax_event_data
    
    
    ################################################################################
    # Delete Fund Event
    ################################################################################
    
    def delete_fund_event(self, fund_event_id: int, session: Session) -> bool:
        """
        Delete a fund event and handle secondary operations.
        
        This method follows enterprise best practices:
        1. Business operation: Delete the fund event directly
        2. Delegate secondary impacts to orchestrator
        
        Args:
            fund_event_id: ID of the fund event to delete
            session: Database session
            
        Returns:
            True if fund event was deleted, False if not found
        """
        fund_event = self.fund_event_repository.get_fund_event_by_id(fund_event_id, session)
        if not fund_event:
            raise ValueError(f"Fund event with ID {fund_event_id} not found")

        fund_event_type = fund_event.event_type
        fund_id = fund_event.fund_id

        errors = self.fund_validation_service.validate_fund_event_deletion(fund_event, session)
        if errors:
            raise ValueError(f"Validation errors for fund event deletion for fund event ID {fund_event_id}: {errors}")

        success = self.fund_event_repository.delete_fund_event(fund_event_id, session)
        
        if success:
            # 2a. Flush the fund to database so it's available for secondary service
            session.flush()
            # 3. Process the secondary operations
            self.fund_event_secondary_service.handle_event_secondary_impact(
                fund_id=fund_id,
                domain_object_type=DomainObjectType.FUND_EVENT,
                event_operation=EventOperation.DELETE,
                session=session,
                fund_event_type=fund_event_type,
                object_id=fund_event_id
            )
        else:
            raise ValueError(f"Failed to delete fund event with ID {fund_event_id}")

        return success
    
    def _calculate_unit_transaction_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate unit transaction event data based on parameters.
        
        This method calculates the amount field for unit purchase and sale events
        based on the units, unit price, and brokerage fee.
        
        Args:
            event_data: Dictionary containing event data
            
        Returns:
            Dictionary with calculated amount field
        """
        processed_data = event_data.copy()
        
        if processed_data['event_type'] == EventType.UNIT_PURCHASE:
            units = processed_data.get('units_purchased', 0.0)
        elif processed_data['event_type'] == EventType.UNIT_SALE:
            units = processed_data.get('units_sold', 0.0)
        else:
            return processed_data
            
        unit_price = processed_data.get('unit_price', 0.0)
        brokerage_fee = processed_data.get('brokerage_fee', 0.0)
        
        # Calculate total amount: (units * unit_price) + brokerage_fee
        if processed_data['event_type'] == EventType.UNIT_PURCHASE:
            total_amount = (units * unit_price) + brokerage_fee
        elif processed_data['event_type'] == EventType.UNIT_SALE:
            total_amount = (units * unit_price) - brokerage_fee
        
        processed_data['amount'] = total_amount
        
        return processed_data