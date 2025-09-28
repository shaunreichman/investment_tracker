"""
Fund Event Service.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from src.fund.models import FundEvent
from src.fund.enums.fund_event_enums import EventType, DistributionType, TaxPaymentType, GroupType, SortFieldFundEvent
from src.shared.enums.shared_enums import EventOperation, SortOrder
from src.fund.repositories import DomainFundEventRepository, FundEventRepository
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.services.fund_event_secondary_service import FundEventSecondaryService

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
        - Handling of domain fund event creation
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
                       group_types: Optional[List[GroupType]] = None,
                       start_event_date: Optional[date] = None,
                       end_event_date: Optional[date] = None,
                       sort_by: Optional[SortFieldFundEvent] = SortFieldFundEvent.EVENT_DATE,
                       sort_order: SortOrder = SortOrder.ASC) -> List['FundEvent']:
        """
        Get events for a specific fund or list of funds.
        
        Args:
            session: Database session
            fund_ids: Optional list of fund IDs
            event_types: Optional list of event types to filter by
            distribution_types: Optional list of distribution types to filter by
            tax_payment_types: Optional list of tax payment types to filter by
            group_types: Optional list of group types to filter by
            start_event_date: Optional start event date to filter by
            end_event_date: Optional end event date to filter by
            sort_by: Optional sort field to sort by
            sort_order: Optional sort order to sort by

        Returns:
            List of FundEvent objects
        """
        return self.fund_event_repository.get_fund_events(
            session, fund_ids, event_types, distribution_types, tax_payment_types, group_types, start_event_date, end_event_date, sort_by, sort_order
        )
    
    def get_fund_event_by_id(self, event_id: int, session: Session) -> Optional['FundEvent']:
        """
        Get a specific fund event by ID.
        
        Args:
            event_id: ID of the event
            session: Database session
            
        Returns:
            FundEvent object if found, None otherwise
        """
        # Get the specific event
        event = self.fund_event_repository.get_fund_event_by_id(event_id, session)
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
            raise ValueError(f"Validation errors: {errors}")

        # 2a. Calculate the distribution event data
        if processed_data['event_type'] == EventType.DISTRIBUTION:
            processed_data = self._calculate_distribution_event_data(processed_data, session)
            if processed_data['has_withholding_tax']:
                # Create the tax event
                tax_data = self._calculate_tax_event_data(processed_data)
                tax_event = self.fund_event_repository.create_fund_event(tax_data, session)

        # 3. Create the fund event
        fund_event = self.fund_event_repository.create_fund_event(processed_data, session)

        # 4. Handle the secondary impacts
        all_changes = self.fund_event_secondary_service.handle_event_secondary_impact(fund_id=fund_event.fund_id, event_id=fund_event.id, 
                            fund_event_type=processed_data['event_type'], fund_event_operation=EventOperation.CREATE, session=session)

        # 5. Store the domain fund event containing the changes
        if all_changes:
            domain_fund_event_repository = DomainFundEventRepository(session)
            domain_fund_event = domain_fund_event_repository.create_domain_fund_event(
                fund_id=fund_event.fund_id,
                event_type=processed_data['event_type'],
                event_operation=EventOperation.CREATE,
                event_id=fund_event.id,
                event_data={"changes": [change.to_dict() for change in all_changes]},
                session=session
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
                processed_data['gross_interest_amount'], processed_data['net_interest_amount'], processed_data['withholding_tax_amount'], processed_data['withholding_tax_rate']
            )
            
            processed_data.update({
                'amount': gross_amount,  # Store gross amount for IRR calculations
                'tax_withholding': tax_amount,  # Tax amount withheld
                'has_withholding_tax': True
            })

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
    
    def delete_fund_event(self, fund_id: int, event_id: int, session: Session) -> bool:
        """
        Delete a fund event and handle secondary operations.
        
        This method follows enterprise best practices:
        1. Business operation: Delete the event directly
        2. Delegate secondary impacts to orchestrator
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event to delete
            session: Database session
            
        Returns:
            True if event was deleted, False if not found
        """
        # 1. Business operation: Delete the event
        from src.fund.repositories import FundEventRepository, FundRepository
        
        fund_repository = FundRepository()
        fund = fund_repository.get_fund_by_id(fund_id, session)
        if not fund:
            raise ValueError(f"Fund with id {fund_id} not found")

        fund_event_repository = FundEventRepository()
        event = fund_event_repository.get_fund_event_by_id(event_id, session)
        if not event:
            raise ValueError(f"Event with id {event_id} not found")

        event_type = event.event_type

        success = fund_event_repository.delete_fund_event(event_id, session)
        
        if success:
            # 2. Process the secondary operations
            all_changes = self.fund_event_secondary_service.handle_event_secondary_impact(fund=fund, event_id=event.id, 
                            fund_event_type=event_type, fund_event_operation=EventOperation.DELETE, session=session)
            if all_changes:
                domain_fund_event_repository = DomainFundEventRepository()
                domain_fund_event = domain_fund_event_repository.create_domain_fund_event(
                    fund_id=fund_id,
                    event_type=event_type,
                    event_operation=EventOperation.DELETE,
                    fund_event_id=event.id,
                    event_data={"changes": [change.to_dict() for change in all_changes]},
                    session=session
                )
        else:
            raise ValueError(f"Failed to delete event")

        return success