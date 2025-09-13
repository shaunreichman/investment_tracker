"""
Fund Event Deletion Handler.

This handler processes fund event deletion side effects,
including equity recalculation and status updates.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date

logger = logging.getLogger(__name__)

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, FundType
from src.fund.models import FundEvent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.fund.models import Fund


class FundEventDeletionHandler(BaseFundEventHandler):
    """
    Handler for fund event deletion side effects.
    
    This handler processes the side effects that occur when a fund event
    is deleted, including:
    - Recalculating equity fields
    - Updating fund status
    - Publishing domain events
    """
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate event deletion data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        fund_id = event_data.get('fund_id')
        deleted_event_id = event_data.get('deleted_event_id')
        event_date = event_data.get('event_date')
        
        if not fund_id:
            raise ValueError("fund_id is required")
        if not deleted_event_id:
            raise ValueError("deleted_event_id is required")
        if not event_date:
            raise ValueError("event_date is required")
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        """
        Handle fund event deletion side effects.
        
        This method:
        1. Validates the event data
        2. Recalculates fund equity fields
        3. Updates fund status
        4. Publishes domain events
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        try:
            logger.info(f"Processing fund event deletion side effects: {event_data}")
            
            # Extract parameters
            fund_id = event_data['fund_id']
            deleted_event_id = event_data['deleted_event_id']
            event_date = self._parse_date(event_data['event_date'])
            
            # Get the fund
            fund = self.session.get(Fund, fund_id)
            if not fund:
                raise ValueError(f"Fund with id {fund_id} not found")
            
            # Recalculate fund equity fields after deletion
            self._recalculate_fund_equity_after_deletion(fund)
            
            # Update fund status based on new equity balance
            self._update_fund_status_after_deletion(fund)
            
            # Publish domain events for dependent components
            self._publish_deletion_events(fund, deleted_event_id, event_date)
            
            logger.info(f"Successfully processed fund event deletion side effects for fund {fund.name}")
            
        except Exception as e:
            logger.error(f"Error processing fund event deletion side effects: {e}")
            raise RuntimeError(f"Failed to process fund event deletion side effects: {e}") from e
    
    def _recalculate_fund_equity_after_deletion(self, fund: 'Fund') -> None:
        """
        Recalculate fund equity fields after event deletion.
        
        Args:
            fund: The fund to recalculate
        """
        from src.fund.calculators.fund_equity_calculator import FundEquityCalculator
        
        # Use domain calculators for consistent calculations
        equity_fields = FundEquityCalculator.recalculate_all_equity_fields(fund, self.session)
        
        # Update fund fields using calculated values
        fund.current_equity_balance = equity_fields['current_equity_balance']
        fund.average_equity_balance = equity_fields['average_equity_balance']
        fund.total_cost_basis = equity_fields['total_cost_basis']
        
        logger.info(f"Recalculated equity fields for fund {fund.name}: "
                   f"current_equity_balance={fund.current_equity_balance}")
    
    def _update_fund_status_after_deletion(self, fund: 'Fund') -> None:
        """
        Update fund status after event deletion.
        
        Args:
            fund: The fund to update
        """
        from src.fund.services.fund_status_service import FundStatusService
        
        # Update fund status based on current equity balance
        status_service = FundStatusService()
        status_service.update_status(fund, self.session)
        
        logger.info(f"Updated fund status for {fund.name}: {fund.status}")
    
    def _publish_deletion_events(self, fund: 'Fund', deleted_event_id: int, event_date: date) -> None:
        """
        Publish domain events for dependent components.
        
        Args:
            fund: The fund that had an event deleted
            deleted_event_id: ID of the deleted event
            event_date: Date of the deletion
        """
        from src.fund.events.domain import EquityBalanceChangedEvent
        from src.fund.events.consumption.event_bus import event_bus
        
        # Publish equity balance changed event
        equity_event = EquityBalanceChangedEvent(
            fund_id=fund.id,
            event_date=event_date,
            new_equity_balance=fund.current_equity_balance,
            previous_equity_balance=None,  # We don't track previous balance for deletions
            metadata={
                "deleted_event_id": deleted_event_id,
                "event_type": "EVENT_DELETED",
                "trigger": "event_deletion"
            }
        )
        event_bus.publish(equity_event, self.session)
        
        logger.info(f"Published equity balance changed event for fund {fund.name}")
