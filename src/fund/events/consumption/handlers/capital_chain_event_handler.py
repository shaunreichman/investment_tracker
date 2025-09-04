"""
Capital Chain Event Handler.

This handler processes capital chain recalculation events and performs
dependent updates for other components in the system.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from src.fund.events.consumption.base_consumer import EventConsumer
from src.fund.events.domain import CapitalChainRecalculatedEvent
from src.fund.repositories.fund_repository import FundRepository
from src.fund.models import Fund, FundEvent
from src.fund.enums import FundType, EventType
from src.fund.services.fund_calculation_service import FundCalculationService
from src.fund.calculators.fund_equity_calculator import FundEquityCalculator

logger = logging.getLogger(__name__)


class CapitalChainEventHandler(EventConsumer):
    """
    Event handler for capital chain recalculation events.
    
    This handler processes capital chain recalculation events and
    updates dependent components accordingly.
    """
    
    def __init__(self):
        """Initialize the capital chain event handler."""
        super().__init__(
            name="CapitalChainEventHandler",
            event_types=[CapitalChainRecalculatedEvent]
        )
        
        logger.info("Initialized CapitalChainEventHandler")
    
    def handle_event(self, event: CapitalChainRecalculatedEvent) -> None:
        """
        Handle a capital chain recalculation event.
        
        Args:
            event: The capital chain recalculation event to handle
        """
        logger.info(f"Processing capital chain recalculation for fund {event.fund_id}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping capital chain update")
                return
            
            # Update fund summary fields after capital chain recalculation
            self._update_fund_summary_fields(event, fund)
            
            # Publish additional events for dependent updates
            self._publish_dependent_events(event, fund)
            
        except Exception as e:
            logger.error(f"Error handling capital chain recalculation event: {e}")
            raise
    
    def _update_fund_summary_fields(self, event: CapitalChainRecalculatedEvent, fund: Fund) -> None:
        """
        Update fund summary fields after capital chain recalculation.
        
        Args:
            event: The capital chain recalculation event
            fund: The fund to update
        """
        logger.info(f"Updating fund summary fields for fund {event.fund_id}")
        
        try:
            # Get all capital events for this fund, ordered by date and ID
            capital_events = self._get_capital_events(fund)
            
            if not capital_events:
                logger.warning(f"No capital events found for fund {event.fund_id}")
                fund.current_equity_balance = 0.0
                return
            
            # Use the new FundEquityService to update equity fields efficiently
            from src.fund.services.fund_equity_service import FundEquityService
            equity_service = FundEquityService(self.session)
            equity_service.update_fund_equity_fields(fund)
            
            # Update other fund summary fields based on fund type
            if fund.tracking_type == FundType.NAV_BASED:
                # For cost-based funds, update capital-related fields
                self._update_nav_based_summary_fields(fund, capital_events)
            elif fund.tracking_type == FundType.COST_BASED:
                # For NAV-based funds, update unit-related fields
                self._update_cost_based_summary_fields(fund, capital_events)
            
            logger.info(f"Successfully updated fund summary fields for fund {event.fund_id}")
            
        except Exception as e:
            logger.error(f"Error updating fund summary fields: {e}")
            raise
    
    def _get_capital_events(self, fund: Fund) -> List[FundEvent]:
        """
        Get all capital events for the fund, ordered by date and ID.
        
        Args:
            fund: The fund to get capital events for
            
        Returns:
            List of capital events ordered by date and ID
        """
        if fund.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds, get unit purchase/sale events
            capital_event_types = [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]
        elif fund.tracking_type == FundType.COST_BASED:
            # For cost-based funds, get capital call/return events
            capital_event_types = [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]
        
        return self.session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_(capital_event_types)
        ).order_by(FundEvent.event_date, FundEvent.id).all()
    
    def _update_cost_based_summary_fields(self, fund: Fund, capital_events: List[FundEvent]) -> None:
        """
        Update summary fields for cost-based funds.
        
        Args:
            fund: The fund to update
            capital_events: List of capital events for the fund
        """
        try:
            # Calculate total cost basis from capital events
            total_calls = sum(e.amount or 0.0 for e in capital_events if e.event_type == EventType.CAPITAL_CALL)
            total_returns = sum(e.amount or 0.0 for e in capital_events if e.event_type == EventType.RETURN_OF_CAPITAL)
            fund.total_cost_basis = total_calls - total_returns
            
            # Update average equity balance
            if capital_events:
                fund.average_equity_balance = FundEquityCalculator.calculate_average_equity(
                    fund, self.session
                )
            
            logger.debug(f"Updated cost-based summary fields for fund {fund.id}")
            
        except Exception as e:
            logger.error(f"Error updating cost-based summary fields: {e}")
            raise
    
    def _update_nav_based_summary_fields(self, fund: Fund, capital_events: List[FundEvent]) -> None:
        """
        Update summary fields for NAV-based funds.
        
        Args:
            fund: The fund to update
            capital_events: List of capital events for the fund
        """
        try:
            if not capital_events:
                fund.current_units = 0.0
                fund.current_unit_price = 0.0
                fund.current_nav_total = 0.0
                return
            
            # Get the latest capital event for current units
            latest_event = capital_events[-1]
            fund.current_units = latest_event.units_owned or 0.0
            
            # Find the most recent NAV_UPDATE event for unit price
            latest_nav_event = self.session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id,
                FundEvent.event_type == EventType.NAV_UPDATE
            ).order_by(FundEvent.event_date.desc(), FundEvent.id.desc()).first()
            
            if latest_nav_event and latest_nav_event.nav_per_share is not None:
                fund.current_unit_price = latest_nav_event.nav_per_share
            elif latest_event.unit_price is not None:
                fund.current_unit_price = latest_event.unit_price
            else:
                fund.current_unit_price = 0.0
            
            # Update NAV total
            fund.current_nav_total = fund.current_units * fund.current_unit_price
            
            # Update average equity balance
            fund.average_equity_balance = FundEquityCalculator.calculate_average_equity(
                fund, self.session
            )
            
            logger.debug(f"Updated NAV-based summary fields for fund {fund.id}")
            
        except Exception as e:
            logger.error(f"Error updating NAV-based summary fields: {e}")
            raise
    
    def _publish_dependent_events(self, event: CapitalChainRecalculatedEvent, fund: Fund) -> None:
        """
        Publish events for dependent updates.
        
        Args:
            event: The capital chain recalculation event
            fund: The fund that was updated
        """
        try:
            # Publish events for other components that need to react to capital chain changes
            # This could include events for tax statements, company records, etc.
            
            from src.fund.events.domain import FundSummaryUpdatedEvent
            from src.fund.events.consumption.event_bus import event_bus
            
            # Publish fund summary update event
            summary_event = FundSummaryUpdatedEvent(
                fund_id=event.fund_id,
                event_date=event.event_date,
                summary_type="CAPITAL_CHAIN_RECALCULATED",
                metadata={
                    "trigger_event_id": event.trigger_event_id,
                    "trigger_event_type": event.trigger_event_type,
                    "old_equity_balance": event.old_equity_balance,
                    "new_equity_balance": event.new_equity_balance,
                    "change_reason": event.change_reason
                }
            )
            
            event_bus.publish(summary_event, self.session)
            logger.info(f"Published fund summary update event for fund {event.fund_id}")
            
        except Exception as e:
            logger.error(f"Error publishing dependent events: {e}")
            raise
    
    def _get_fund(self, fund_id: int) -> Optional[Fund]:
        """
        Get fund information for the given fund ID.
        
        Args:
            fund_id: ID of the fund to retrieve
            
        Returns:
            Fund object if found, None otherwise
        """
        if not self.session:
            logger.error("No database session available for retrieving fund")
            return None
            
        try:
            # Use the session to query for the fund
            fund = self.session.query(Fund).filter(Fund.id == fund_id).first()
            return fund
            
        except Exception as e:
            logger.error(f"Error retrieving fund {fund_id}: {e}")
            return None
