"""
Distribution Event Handler.

This handler processes distribution events for funds,
updating equity balances and triggering dependent calculations.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, DistributionType, GroupType
from src.fund.models import FundEvent
from src.fund.repositories.fund_event_repository import FundEventRepository


class DistributionHandler(BaseFundEventHandler):
    """
    Handler for distribution events.
    
    This handler processes distribution events for all fund types.
    It handles both simple distributions and complex distributions
    with withholding tax calculations.
    """
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate distribution event data structure.
        
        Note: Business validation is handled by FundValidationService.
        This method only validates basic event structure.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If basic structure validation fails
        """
        # Validate required event structure
        if not isinstance(event_data, dict):
            raise ValueError("event_data must be a dictionary")
        
        # Validate event_id is present (event should be pre-created by service)
        event_id = event_data.get('event_id')
        if not event_id:
            raise ValueError("event_id is required - event should be created by service first")
        
        # Validate basic required fields for handler processing
        if 'fund_id' not in event_data:
            raise ValueError("fund_id is required for event processing")
        
        if 'event_date' not in event_data:
            raise ValueError("event_date is required for event processing")

        if 'has_withholding_tax' not in event_data:
            raise ValueError("has_withholding_tax is required for event processing")
        
        if event_data.get('has_withholding_tax', True):
            if event_data.get('tax_withholding', 0) <= 0:
                raise ValueError("tax_withholding must be greater than 0 when has_withholding_tax is True")
            if event_data.get('group_id') is None:
                raise ValueError("group_id is required when has_withholding_tax is True")
            if event_data.get('group_type') is None or event_data.get('group_type') != GroupType.INTEREST_WITHHOLDING:
                raise ValueError("group_type must be INTEREST_WITHHOLDING when has_withholding_tax is True")
            if event_data.get('group_position') is None or event_data.get('group_position') != 0:
                raise ValueError("group_position must be 0 when has_withholding_tax is True")
            if event_data.get('is_grouped') is None or event_data.get('is_grouped') != True:
                raise ValueError("is_grouped must be True when has_withholding_tax is True")
            
            # Check if the withholding tax event is present
            from src.fund.repositories import TaxEventRepository
            tax_event_repo = TaxEventRepository()
            tax_event = tax_event_repo.get_tax_event_by_group_id(event_data.get('group_id'), self.session)
            if not tax_event:
                raise ValueError(f"Tax event with group id {event_data.get('group_id')} not found - event should be created by service first")

    
    def handle_create_event(self, event_data: Dict[str, Any]) -> FundEvent:
        """
        Handle a distribution event.
        
        This method processes side effects for pre-created distribution events:
        1. Updates fund state
        2. Publishes domain events
        3. Handles status transitions
        
        Args:
            event_data: Dictionary containing event parameters with event_id
            
        Returns:
            FundEvent: The distribution event
            
        Raises:
            ValueError: If event_id is missing or event not found
        """
        # Event validation is handled by the service layer
        
        event_id = event_data.get('event_id')
        if not event_id:
            raise ValueError("event_id is required - event should be created by service first")
        
        fund_event_repository = FundEventRepository(self.session)
        event = fund_event_repository.get_event_by_id(event_id)
        if not event:
            raise ValueError(f"Event with id {event_id} not found - event should be created by service first")
        
        # Update fund state after distribution
        self._update_fund_after_distribution(event)
        
        # Handle status transitions
        self._handle_status_transition(event)
        
        # Publish domain events
        self._publish_dependent_events(event)
        
        return event

    def handle_delete_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Handle a distribution event deletion.
        
        Args:
            event_data: Dictionary containing event parameters

        Returns:
            bool: True if the event was deleted successfully

        Raises:
            ValueError: If event data is invalid
        """
        event_id = event_data.get('event_id')
        if not event_id:
            raise ValueError("event_id is required - event should have existed first before deletion")
        
        # We need to confirm the event doesn't exist anymore by calling the repository layer
        fund_event_repository = FundEventRepository(self.session)
        if fund_event_repository.get_event_by_id(event_id):
            raise ValueError(f"Event with id {event_id} still exists - event should have been deleted first")
        
        return True
    
    
    def _update_fund_after_distribution(self, event: FundEvent) -> None:
        """
        Update fund state after a distribution event.
        
        Args:
            event: The distribution event that was created
        """
        # For distributions, we typically don't need to recalculate
        # the entire capital chain, but we may need to update
        # specific fields or trigger other updates
        pass
    
    
    def _publish_dependent_events(self, event: FundEvent) -> None:
        """
        Publish domain events for dependent updates.
        
        This method creates and stores domain events for significant
        state changes, enabling loose coupling between components.
        
        Args:
            event: The distribution event that was processed
        """
        # Call the base class implementation which handles all domain event creation
        super()._publish_dependent_events(event)
