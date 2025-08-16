"""
Company Record Event Handler.

This module provides the event handler for updating company records
based on fund events. It handles events like equity balance changes,
distributions, and NAV updates to maintain company record consistency.
"""

import logging
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..base_consumer import EventConsumer
from ...domain import (
    EquityBalanceChangedEvent,
    DistributionRecordedEvent,
    NAVUpdatedEvent,
    UnitsChangedEvent,
    FundSummaryUpdatedEvent
)
from ....repositories.fund_repository import FundRepository
from ....models import Fund
from ....enums import FundType

logger = logging.getLogger(__name__)


class CompanyRecordEventHandler(EventConsumer):
    """
    Event handler for company record updates.
    
    This handler processes fund-related events and updates company records
    accordingly to maintain consistency across the system.
    """
    
    def __init__(self):
        """Initialize the company record event handler."""
        super().__init__(
            name="CompanyRecordEventHandler",
            event_types=[
                EquityBalanceChangedEvent,
                DistributionRecordedEvent,
                NAVUpdatedEvent,
                UnitsChangedEvent,
                FundSummaryUpdatedEvent
            ]
        )
        
        logger.info("Initialized CompanyRecordEventHandler")
    
    def handle_event(self, event) -> None:
        """
        Handle a domain event and update company records accordingly.
        
        Args:
            event: The domain event to handle
        """
        event_type = type(event)
        
        if event_type == EquityBalanceChangedEvent:
            self._handle_equity_balance_changed(event)
        elif event_type == DistributionRecordedEvent:
            self._handle_distribution_recorded(event)
        elif event_type == NAVUpdatedEvent:
            self._handle_nav_updated(event)
        elif event_type == UnitsChangedEvent:
            self._handle_units_changed(event)
        elif event_type == FundSummaryUpdatedEvent:
            self._handle_fund_summary_updated(event)
        else:
            logger.warning(f"CompanyRecordEventHandler received unexpected event type: {event_type}")
    
    def _handle_equity_balance_changed(self, event: EquityBalanceChangedEvent) -> None:
        """
        Handle equity balance changed events.
        
        Args:
            event: Equity balance changed event
        """
        logger.info(f"Processing equity balance change for fund {event.fund_id}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping company record update")
                return
            
            # Update company equity values
            self._update_company_equity(event.fund_id, event.event_date, event.new_balance)
            
        except Exception as e:
            logger.error(f"Error handling equity balance change event: {e}")
            raise
    
    def _handle_distribution_recorded(self, event: DistributionRecordedEvent) -> None:
        """
        Handle distribution recorded events.
        
        Args:
            event: Distribution recorded event
        """
        logger.info(f"Processing distribution for fund {event.fund_id}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping company record update")
                return
            
            # Update company distribution information
            self._update_company_distribution(
                event.fund_id, 
                event.event_date, 
                event.amount, 
                event.tax_withheld
            )
            
        except Exception as e:
            logger.error(f"Error handling distribution recorded event: {e}")
            raise
    
    def _handle_nav_updated(self, event: NAVUpdatedEvent) -> None:
        """
        Handle NAV updated events.
        
        Args:
            event: NAV updated event
        """
        logger.info(f"Processing NAV update for fund {event.fund_id}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping company record update")
                return
            
            # For NAV-based funds, NAV changes affect company performance metrics
            if fund.tracking_type == FundType.NAV_BASED:
                self._update_company_nav(event.fund_id, event.event_date, event.new_nav)
            else:
                logger.debug(f"Fund {event.fund_id} is not NAV-based, NAV changes don't affect company records")
            
        except Exception as e:
            logger.error(f"Error handling NAV updated event: {e}")
            raise
    
    def _handle_units_changed(self, event: UnitsChangedEvent) -> None:
        """
        Handle units changed events.
        
        Args:
            event: Units changed event
        """
        logger.info(f"Processing units change for fund {event.fund_id}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping company record update")
                return
            
            # Update company unit values
            self._update_company_units(event.fund_id, event.event_date, event.new_units)
            
        except Exception as e:
            logger.error(f"Error handling units changed event: {e}")
            raise
    
    def _handle_fund_summary_updated(self, event: FundSummaryUpdatedEvent) -> None:
        """
        Handle fund summary updated events.
        
        Args:
            event: Fund summary updated event
        """
        logger.info(f"Processing fund summary update for fund {event.fund_id}, type: {event.event_type}")
        
        try:
            # Get the fund to determine its type and current status
            fund = self._get_fund(event.fund_id)
            if not fund:
                logger.warning(f"Fund {event.fund_id} not found, skipping company record update")
                return
            
            # Update company summary information based on the event type
            if event.summary_type == "CAPITAL_EVENT_PROCESSED":
                # Capital events affect company portfolio totals
                self._update_company_portfolio_totals(event.fund_id, event.event_date)
            elif event.summary_type == "NAV_UPDATE":
                # NAV updates affect company portfolio values
                self._update_company_portfolio_values(event.fund_id, event.event_date)
            else:
                logger.debug(f"Unknown fund summary update type: {event.summary_type}")
            
        except Exception as e:
            logger.error(f"Error handling fund summary updated event: {e}")
            raise
    
    def _update_company_portfolio_totals(self, fund_id: int, event_date: date) -> None:
        """
        Update company portfolio totals after capital events.
        
        Args:
            fund_id: ID of the fund that was updated
            event_date: Date of the event
        """
        logger.info(f"Updating company portfolio totals for fund {fund_id}")
        # This would trigger company portfolio recalculation
        # For now, just log the update
        
    def _update_company_portfolio_values(self, fund_id: int, event_date: date) -> None:
        """
        Update company portfolio values after NAV updates.
        
        Args:
            fund_id: ID of the fund that was updated
            event_date: Date of the event
        """
        logger.info(f"Updating company portfolio values for fund {fund_id}")
        # This would trigger company portfolio value recalculation
        # For now, just log the update
    
    def _get_fund(self, fund_id: int) -> Optional[Fund]:
        """
        Get fund information for the given fund ID.
        
        Args:
            fund_id: ID of the fund to retrieve
            
        Returns:
            Fund object if found, None otherwise
        """
        # Note: In a real implementation, this would get a session from the context
        # For now, we'll use a placeholder approach
        try:
            # This would typically get a session from the event context
            # For now, we'll create a temporary repository instance
            fund_repo = FundRepository()
            # Note: This won't work without a session, but shows the intended approach
            logger.debug(f"Would retrieve fund {fund_id} using repository")
            return None  # Placeholder - would return actual fund in real implementation
        except Exception as e:
            logger.error(f"Error retrieving fund {fund_id}: {e}")
            return None
    
    def _get_company_id_from_fund(self, fund_id: int) -> Optional[int]:
        """
        Get the investment company ID associated with a fund.
        
        Args:
            fund_id: ID of the fund
            
        Returns:
            Investment company ID if found, None otherwise
        """
        try:
            # Get the fund to find its investment company
            fund = self._get_fund(fund_id)
            if fund and hasattr(fund, 'investment_company_id'):
                return fund.investment_company_id
            return None
        except Exception as e:
            logger.error(f"Error getting company ID for fund {fund_id}: {e}")
            return None
    
    def _update_company_equity(self, fund_id: int, event_date: date, new_equity: float) -> None:
        """
        Update company equity values.
        
        Args:
            fund_id: ID of the fund
            event_date: Date of the event
            new_equity: New equity balance
        """
        logger.info(f"Updating company equity for fund {fund_id} to {new_equity}")
        
        try:
            # Get the investment company ID for this fund
            company_id = self._get_company_id_from_fund(fund_id)
            if not company_id:
                logger.warning(f"Could not determine company ID for fund {fund_id}")
                return
            
            # Note: In a real implementation, this would update the company record
            # For now, we'll use a placeholder approach
            logger.debug(f"Would update company {company_id} equity values for fund {fund_id}")
            
            # This would typically involve:
            # 1. Getting the company record
            # 2. Updating total equity across all funds
            # 3. Recalculating company performance metrics
            # 4. Updating company status if needed
            
        except Exception as e:
            logger.error(f"Error updating company equity for fund {fund_id}: {e}")
            raise
    
    def _update_company_distribution(self, fund_id: int, event_date: date, amount: float, tax_withheld: float) -> None:
        """
        Update company distribution information.
        
        Args:
            fund_id: ID of the fund
            event_date: Date of the event
            amount: Distribution amount
            tax_withheld: Tax withheld amount
        """
        logger.info(f"Updating company distribution for fund {fund_id}: amount={amount}, tax={tax_withheld}")
        
        try:
            # Get the investment company ID for this fund
            company_id = self._get_company_id_from_fund(fund_id)
            if not company_id:
                logger.warning(f"Could not determine company ID for fund {fund_id}")
                return
            
            # Note: In a real implementation, this would update the company record
            # For now, we'll use a placeholder approach
            logger.debug(f"Would update company {company_id} distribution values for fund {fund_id}")
            
            # This would typically involve:
            # 1. Getting the company record
            # 2. Updating total distributions for the period
            # 3. Updating tax withholding totals
            # 4. Recalculating company performance metrics
            
        except Exception as e:
            logger.error(f"Error updating company distribution for fund {fund_id}: {e}")
            raise
    
    def _update_company_nav(self, fund_id: int, event_date: date, new_nav: float) -> None:
        """
        Update company NAV values.
        
        Args:
            fund_id: ID of the fund
            event_date: Date of the event
            new_nav: New NAV value
        """
        logger.info(f"Updating company NAV for fund {fund_id} to {new_nav}")
        
        try:
            # Get the investment company ID for this fund
            company_id = self._get_company_id_from_fund(fund_id)
            if not company_id:
                logger.warning(f"Could not determine company ID for fund {fund_id}")
                return
            
            # Note: In a real implementation, this would update the company record
            # For now, we'll use a placeholder approach
            logger.debug(f"Would update company {company_id} NAV values for fund {fund_id}")
            
            # This would typically involve:
            # 1. Getting the company record
            # 2. Updating NAV-related fields
            # 3. Recalculating unrealized gains/losses across all funds
            # 4. Updating company performance metrics
            
        except Exception as e:
            logger.error(f"Error updating company NAV for fund {fund_id}: {e}")
            raise
    
    def _update_company_units(self, fund_id: int, event_date: date, new_units: float) -> None:
        """
        Update company unit values.
        
        Args:
            fund_id: ID of the fund
            event_date: Date of the event
            new_units: New unit value
        """
        logger.info(f"Updating company units for fund {fund_id} to {new_units}")
        
        try:
            # Get the investment company ID for this fund
            company_id = self._get_company_id_from_fund(fund_id)
            if not company_id:
                logger.warning(f"Could not determine company ID for fund {fund_id}")
                return
            
            # Note: In a real implementation, this would update the company record
            # For now, we'll use a placeholder approach
            logger.debug(f"Would update company {company_id} unit values for fund {fund_id}")
            
            # This would typically involve:
            # 1. Getting the company record
            # 2. Updating total units across all funds
            # 3. Recalculating company performance metrics
            # 4. Updating company status if needed
            
        except Exception as e:
            logger.error(f"Error updating company units for fund {fund_id}: {e}")
            raise
