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
        
        # Create the fund using the fund domain method
        fund = Fund.create(
            investment_company_id=company.id,
            entity_id=entity.id,
            name=name,
            fund_type=fund_type,
            tracking_type=tracking_type,
            currency=currency,
            description=description,
            commitment_amount=commitment_amount,
            expected_irr=expected_irr,
            expected_duration_months=expected_duration_months,
            session=session
        )
        
        return fund
    
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
