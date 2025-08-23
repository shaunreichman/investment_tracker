"""
Company Portfolio Service.

This service handles portfolio operations and fund coordination for investment companies,
implementing clean separation of concerns and enterprise-grade architecture.

Key responsibilities:
- Portfolio operations and fund coordination
- Fund creation coordination with fund domain
- Portfolio summary calculations
- Fund relationship management
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.investment_company.repositories import CompanyRepository, ContactRepository
from src.investment_company.models import InvestmentCompany, Contact
from src.fund.models import Fund
from src.fund.enums import FundStatus


class CompanyPortfolioService:
    """
    Service for company portfolio operations and fund coordination.
    
    This service coordinates between company and fund domains without
    duplicating fund business logic. It handles portfolio operations,
    fund coordination, and portfolio updates.
    
    Attributes:
        company_repository (CompanyRepository): Repository for company data access
        contact_repository (ContactRepository): Repository for contact data access
    """
    
    def __init__(self):
        """Initialize the company portfolio service."""
        self.company_repository = CompanyRepository()
        self.contact_repository = ContactRepository()
    
    def get_funds_with_summary(self, company: InvestmentCompany, session: Session) -> List[Dict[str, Any]]:
        """
        Get funds with summary data for a company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
            
        Returns:
            List of fund summary data dictionaries
        """
        funds_data = []
        for fund in company.funds:
            funds_data.append(fund.get_summary_data(session=session))
        return funds_data
    
    def get_total_funds_under_management(self, company: InvestmentCompany, session: Session) -> int:
        """
        Get the total number of funds managed by an investment company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        
        Returns:
            int: Total number of funds
        """
        from src.investment_company.calculations import calculate_total_funds_under_management
        return calculate_total_funds_under_management(company, session)
    
    def get_total_commitments(self, company: InvestmentCompany, session: Session) -> float:
        """
        Get the total commitments across all funds managed by an investment company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        
        Returns:
            float: Total commitments across all funds
        """
        from src.investment_company.calculations import calculate_total_commitments
        return calculate_total_commitments(company, session)
    
    def create_fund(self, company: InvestmentCompany, entity, name: str, fund_type: str, 
                   tracking_type, currency: str = "AUD", description: str = None, 
                   commitment_amount: float = None, expected_irr: float = None, 
                   expected_duration_months: int = None, session: Session = None) -> Fund:
        """
        Create a new fund for an investment company.
        
        This method coordinates fund creation between company and fund domains
        without duplicating fund business logic.
        
        Args:
            company: InvestmentCompany object
            entity: The entity that will invest in the fund
            name: Fund name
            fund_type: Type of fund (e.g., "Private Debt", "Equity")
            tracking_type: Tracking type (COST_BASED or NAV_BASED)
            currency: Currency code (default: "AUD")
            description: Fund description
            commitment_amount: Commitment amount for cost-based funds
            expected_irr: Expected IRR percentage
            expected_duration_months: Expected duration in months
            session: Database session
        
        Returns:
            Fund: The created fund
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate entity
        if entity is None:
            raise ValueError("Entity is required")
        
        # Create fund data dictionary for fund domain service
        fund_data = {
            'name': name,
            'entity_id': entity.id,
            'investment_company_id': company.id,
            'fund_type': fund_type,
            'tracking_type': tracking_type,
            'currency': currency,
            'description': description,
            'commitment_amount': commitment_amount,
            'expected_irr': expected_irr,
            'expected_duration_months': expected_duration_months
        }
        
        # Delegate fund creation to fund domain service (single source of truth)
        from src.fund.services.fund_service import FundService
        fund_service = FundService()
        fund_result = fund_service.create_fund(fund_data, session)
        
        # Get the created fund from the result
        fund = self._get_fund_by_id(fund_result['id'], session)
        
        # Publish company domain event for portfolio update
        self._publish_portfolio_updated_event(company, fund, 'added', session)
        
        return fund
    
    def _get_fund_by_id(self, fund_id: int, session: Session) -> Fund:
        """
        Get fund by ID from the fund domain.
        
        Args:
            fund_id: Fund ID
            session: Database session
            
        Returns:
            Fund: The fund instance
        """
        from src.fund.repositories.fund_repository import FundRepository
        fund_repository = FundRepository()
        return fund_repository.get_by_id(fund_id, session)
    
    def _publish_portfolio_updated_event(self, company: InvestmentCompany, fund: Fund, 
                                       operation: str, session: Session) -> None:
        """
        Publish portfolio updated event for cross-domain coordination.
        
        Args:
            company: InvestmentCompany object
            fund: Fund that was added/updated/removed
            operation: Operation type ('added', 'updated', 'removed')
            session: Database session
        """
        from src.investment_company.events.domain.portfolio_updated_event import PortfolioUpdatedEvent
        from src.investment_company.events.registry import CompanyEventHandlerRegistry
        
        # Create and publish the event
        event = PortfolioUpdatedEvent(
            company_id=company.id,
            event_date=date.today(),
            fund_id=fund.id,
            operation=operation
        )
        
        # Get the registry and publish the event
        registry = CompanyEventHandlerRegistry()
        registry.publish_event(event, session)
    
    def get_portfolio_summary(self, company: InvestmentCompany, session: Session) -> Dict[str, Any]:
        """
        Get portfolio summary data for a company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
            
        Returns:
            dict: Portfolio summary data
        """
        funds = company.funds
        
        # Calculate portfolio summary
        total_committed_capital = sum(fund.commitment_amount or 0 for fund in funds)
        total_current_value = sum(fund.current_equity_balance or 0 for fund in funds)
        total_invested_capital = sum(fund.current_equity_balance or 0 for fund in funds)
        
        # Count funds by status
        active_funds_count = sum(1 for fund in funds if fund.status == FundStatus.ACTIVE)
        completed_funds_count = sum(1 for fund in funds if fund.status == FundStatus.COMPLETED)
        suspended_funds_count = sum(1 for fund in funds if fund.status == FundStatus.SUSPENDED)
        realized_funds_count = sum(1 for fund in funds if fund.status == FundStatus.REALIZED)
        
        fund_status_breakdown = {
            "active_funds_count": active_funds_count,
            "completed_funds_count": completed_funds_count,
            "suspended_funds_count": suspended_funds_count,
            "realized_funds_count": realized_funds_count
        }
        
        return {
            "total_committed_capital": total_committed_capital,
            "total_current_value": total_current_value,
            "total_invested_capital": total_invested_capital,
            "active_funds_count": active_funds_count,
            "completed_funds_count": completed_funds_count,
            "fund_status_breakdown": fund_status_breakdown
        }
    
    def get_last_activity_info(self, company: InvestmentCompany, session: Session) -> Dict[str, Any]:
        """
        Get last activity information for a company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
            
        Returns:
            dict: Last activity information
        """
        funds = company.funds
        
        last_activity_date = None
        days_since_last_activity = None
        
        if funds:
            # Find the most recent event date across all funds
            all_event_dates = []
            for fund in funds:
                if fund.fund_events:
                    fund_event_dates = [event.event_date for event in fund.fund_events]
                    all_event_dates.extend(fund_event_dates)
            
            if all_event_dates:
                last_activity_date = max(all_event_dates)
                from datetime import date
                days_since_last_activity = (date.today() - last_activity_date).days
        
        return {
            "last_activity_date": last_activity_date.isoformat() if last_activity_date else None,
            "days_since_last_activity": days_since_last_activity
        }
    
    def remove_fund_from_portfolio(self, company: InvestmentCompany, fund_id: int, session: Session) -> None:
        """
        Remove a fund from a company's portfolio.
        
        This method coordinates fund removal between company and fund domains
        without duplicating fund business logic.
        
        Args:
            company: InvestmentCompany object
            fund_id: ID of the fund to remove
            session: Database session
            
        Raises:
            ValueError: If fund is not found in company portfolio
        """
        # Find the fund in the company's portfolio
        fund = next((f for f in company.funds if f.id == fund_id), None)
        if not fund:
            raise ValueError(f"Fund {fund_id} not found in company {company.id} portfolio")
        
        # Publish company domain event for portfolio update
        self._publish_portfolio_updated_event(company, fund, 'removed', session)
        
        # Note: We don't delete the fund here - that's handled by the fund domain
        # We just remove it from the company's portfolio relationship
        # The fund domain will handle the actual fund deletion logic
    
    def update_fund_in_portfolio(self, company: InvestmentCompany, fund_id: int, 
                               fund_data: Dict[str, Any], session: Session) -> Fund:
        """
        Update a fund in a company's portfolio.
        
        This method coordinates fund updates between company and fund domains
        without duplicating fund business logic.
        
        Args:
            company: InvestmentCompany object
            fund_id: ID of the fund to update
            fund_data: Updated fund data
            session: Database session
            
        Returns:
            Fund: The updated fund instance
            
        Raises:
            ValueError: If fund is not found in company portfolio
        """
        # Find the fund in the company's portfolio
        fund = next((f for f in company.funds if f.id == fund_id), None)
        if not fund:
            raise ValueError(f"Fund {fund_id} not found in company {company.id} portfolio")
        
        # Delegate fund update to fund domain service
        from src.fund.services.fund_service import FundService
        fund_service = FundService()
        updated_fund = fund_service.update_fund(fund_id, fund_data, session)
        
        # Publish company domain event for portfolio update
        self._publish_portfolio_updated_event(company, fund, 'updated', session)
        
        return fund
    
    def update_portfolio_summary(self, company: InvestmentCompany, session: Session) -> None:
        """
        Update portfolio summary for a company.
        
        This method recalculates and updates portfolio summary information
        when portfolio data changes.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        """
        try:
            # Recalculate portfolio summary data
            summary_data = self.get_portfolio_summary(company, session)
            
            # Update portfolio summary fields if they exist
            # Note: This is a placeholder for future summary field updates
            # Currently, summaries are calculated on-demand
            
            # Log the update
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Updated portfolio summary for company {company.id}")
            
        except Exception as error:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to update portfolio summary: {error}")
            # Don't fail the main operation for summary update failures
