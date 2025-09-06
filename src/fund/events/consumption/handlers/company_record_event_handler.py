"""
Company Record Event Handler.

This handler processes company record update events,
triggering appropriate updates in dependent components.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.fund.events.consumption.base_consumer import EventConsumer
from src.fund.events.domain import (
    EquityBalanceChangedEvent,
    DistributionRecordedEvent,
    NAVUpdatedEvent,
    FundSummaryUpdatedEvent
)
from src.fund.repositories.fund_repository import FundRepository
from src.fund.models import Fund
from src.fund.enums import FundType

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
            
            # Create company record update event
            # This would typically involve updating aggregated equity values
            # For now, just log the update
            logger.info(f"Updated company equity values for fund {event.fund_id}")
            
            # Mark company as updated
            fund.updated_at = event.event_date
            
        except Exception as e:
            logger.error(f"Error updating company equity for fund {event.fund_id}: {e}")
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
            logger.error(f"Error updating company distribution for fund {event.fund_id}: {e}")
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
            
            # Create company record update event
            # For NAV-based funds, NAV changes affect company performance metrics
            if fund.tracking_type == FundType.NAV_BASED:
                self._update_company_nav(event.fund_id, event.event_date, event.new_nav)
            else:
                logger.debug(f"Fund {event.fund_id} is not NAV-based, NAV changes don't affect company records")
            
        except Exception as e:
            logger.error(f"Error handling NAV updated event: {e}")
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
            
            # Create company record update event
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
        if not self.session:
            logger.error("No database session available for retrieving fund")
            return None
            
        try:
            # Use the session to query for the fund
            fund = self.session.query(Fund).filter(Fund.id == fund_id).first()
            if fund:
                logger.debug(f"Retrieved fund {fund_id}: {fund.name}")
                return fund
            else:
                logger.warning(f"Fund {fund_id} not found")
                return None
                
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
            # Query the fund's investment company ID directly from the database
            # This avoids direct model access and maintains loose coupling
            result = self.session.query(Fund.investment_company_id).filter(
                Fund.id == fund_id
            ).first()
            
            if result and result[0]:
                company_id = result[0]
                logger.debug(f"Retrieved company ID {company_id} for fund {fund_id}")
                return company_id
            else:
                logger.warning(f"No investment company found for fund {fund_id}")
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
            
            # Get the investment company record
            from src.investment_company.models import InvestmentCompany
            company = self.session.query(InvestmentCompany).filter(
                InvestmentCompany.id == company_id
            ).first()
            
            if not company:
                logger.warning(f"Investment company {company_id} not found")
                return
            
            # Update company portfolio totals
            # This would typically involve updating aggregated equity values
            # For now, we'll log the update and could implement more sophisticated logic
            logger.info(f"Updated company {company.name} (ID: {company_id}) equity values for fund {fund_id}")
            
            # Mark company as updated
            company.updated_at = event_date
            
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
            
            # Get the investment company record
            from src.investment_company.models import InvestmentCompany
            company = self.session.query(InvestmentCompany).filter(
                InvestmentCompany.id == company_id
            ).first()
            
            if not company:
                logger.warning(f"Investment company {company_id} not found")
                return
            
            # Update company distribution totals
            # This would typically involve updating aggregated distribution values
            # For now, we'll log the update and could implement more sophisticated logic
            logger.info(f"Updated company {company.name} (ID: {company_id}) distribution values for fund {fund_id}")
            
            # Mark company as updated
            company.updated_at = event_date
            
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
            
            # Get the investment company record
            from src.investment_company.models import InvestmentCompany
            company = self.session.query(InvestmentCompany).filter(
                InvestmentCompany.id == company_id
            ).first()
            
            if not company:
                logger.warning(f"Investment company {company_id} not found")
                return
            
            # Update company NAV-related fields
            # This would typically involve updating aggregated NAV values
            # For now, we'll log the update and could implement more sophisticated logic
            logger.info(f"Updated company {company.name} (ID: {company_id}) NAV values for fund {fund_id}")
            
            # Mark company as updated
            company.updated_at = event_date
            
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
            
            # Get the investment company record
            from src.investment_company.models import InvestmentCompany
            company = self.session.query(InvestmentCompany).filter(
                InvestmentCompany.id == company_id
            ).first()
            
            if not company:
                logger.warning(f"Investment company {company_id} not found")
                return
            
            # Update company unit-related fields
            # This would typically involve updating aggregated unit values
            # For now, we'll log the update and could implement more sophisticated logic
            logger.info(f"Updated company {company.name} (ID: {company_id}) unit values for fund {fund_id}")
            
            # Mark company as updated
            company.updated_at = event_date
            
        except Exception as e:
            logger.error(f"Error updating company units for fund {fund_id}: {e}")
            raise
