"""
Company Calculation Service.

This service extracts calculation logic from the InvestmentCompany model to provide
clean separation of concerns and improved testability.

Extracted functionality:
- Total funds under management calculations
- Total commitments calculations
- Portfolio performance metrics
- Company summary calculations
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.investment_company.models import InvestmentCompany
from src.fund.models import Fund
from src.fund.enums import FundStatus


class CompanyCalculationService:
    """
    Service for handling company calculations extracted from the InvestmentCompany model.
    
    This service provides clean separation of concerns for:
    - Portfolio calculations and metrics
    - Fund counting and commitment calculations
    - Company performance calculations
    - Summary data calculations
    """
    
    def __init__(self):
        """Initialize the CompanyCalculationService."""
        pass
    
    # ============================================================================
    # PORTFOLIO CALCULATIONS
    # ============================================================================
    
    def calculate_total_funds_under_management(self, company: InvestmentCompany, session: Session) -> int:
        """
        Calculate the total number of funds managed by an investment company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        
        Returns:
            int: Total number of funds
        """
        return len(company.funds) if company.funds else 0
    
    def calculate_total_commitments(self, company: InvestmentCompany, session: Session) -> float:
        """
        Calculate the total commitments across all funds managed by an investment company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        
        Returns:
            float: Total commitments across all funds
        """
        total_commitments = 0.0
        if company.funds:
            for fund in company.funds:
                if fund.commitment_amount:
                    total_commitments += fund.commitment_amount
        return total_commitments
    
    def calculate_active_funds_count(self, company: InvestmentCompany, session: Session) -> int:
        """
        Calculate the number of active funds managed by an investment company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        
        Returns:
            int: Number of active funds
        """
        if not company.funds:
            return 0
        
        active_count = 0
        for fund in company.funds:
            if fund.status == FundStatus.ACTIVE:
                active_count += 1
        return active_count
    
    def calculate_completed_funds_count(self, company: InvestmentCompany, session: Session) -> int:
        """
        Calculate the number of completed funds managed by an investment company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        
        Returns:
            int: Number of completed funds
        """
        if not company.funds:
            return 0
        
        completed_count = 0
        for fund in company.funds:
            if fund.status == FundStatus.COMPLETED:
                completed_count += 1
        return completed_count
    
    # ============================================================================
    # PERFORMANCE CALCULATIONS
    # ============================================================================
    
    def calculate_average_commitment_size(self, company: InvestmentCompany, session: Session) -> float:
        """
        Calculate the average commitment amount across all funds for an investment company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        
        Returns:
            float: Average commitment amount, 0.0 if no funds with commitments
        """
        if not company.funds:
            return 0.0
        
        # Count only funds with valid commitment amounts
        valid_funds_count = 0
        total_commitments = 0.0
        
        for fund in company.funds:
            if fund.commitment_amount is not None:
                valid_funds_count += 1
                total_commitments += fund.commitment_amount
        
        if valid_funds_count == 0:
            return 0.0
        
        return total_commitments / valid_funds_count
    
    def calculate_portfolio_diversification_score(self, company: InvestmentCompany, session: Session) -> float:
        """
        Calculate a simple diversification score based on fund count and size distribution.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        
        Returns:
            float: Diversification score (0.0 to 1.0)
        """
        total_funds = self.calculate_total_funds_under_management(company, session)
        
        if total_funds <= 1:
            return 0.0  # No diversification with 0 or 1 fund
        
        # Simple scoring: more funds = higher diversification
        # Cap at 10 funds for realistic scoring
        max_funds_for_scoring = 10
        if total_funds >= max_funds_for_scoring:
            return 1.0
        
        return total_funds / max_funds_for_scoring
    
    # ============================================================================
    # SUMMARY CALCULATIONS
    # ============================================================================
    
    def calculate_company_summary_metrics(self, company: InvestmentCompany, session: Session) -> Dict[str, Any]:
        """
        Calculate comprehensive summary metrics for an investment company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        
        Returns:
            Dict containing all summary metrics
        """
        return {
            'total_funds': self.calculate_total_funds_under_management(company, session),
            'active_funds': self.calculate_active_funds_count(company, session),
            'completed_funds': self.calculate_completed_funds_count(company, session),
            'total_commitments': self.calculate_total_commitments(company, session),
            'average_commitment_size': self.calculate_average_commitment_size(company, session),
            'diversification_score': self.calculate_portfolio_diversification_score(company, session)
        }
    
    def calculate_portfolio_summary(self, company: InvestmentCompany, session: Session) -> Dict[str, Any]:
        """
        Calculate portfolio-specific summary data for an investment company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
        
        Returns:
            Dict containing portfolio summary data
        """
        if not company.funds:
            return {
                'fund_count': 0,
                'total_commitments': 0.0,
                'active_commitments': 0.0,
                'completed_commitments': 0.0,
                'funds_by_status': {}
            }
        
        funds_by_status = {}
        total_commitments = 0.0
        active_commitments = 0.0
        completed_commitments = 0.0
        
        for fund in company.funds:
            status = fund.status.value if fund.status else 'UNKNOWN'
            commitment = fund.commitment_amount or 0.0
            
            if status not in funds_by_status:
                funds_by_status[status] = {
                    'count': 0,
                    'total_commitments': 0.0
                }
            
            funds_by_status[status]['count'] += 1
            funds_by_status[status]['total_commitments'] += commitment
            total_commitments += commitment
            
            if fund.status == FundStatus.ACTIVE:
                active_commitments += commitment
            elif fund.status == FundStatus.COMPLETED:
                completed_commitments += commitment
        
        return {
            'fund_count': len(company.funds),
            'total_commitments': total_commitments,
            'active_commitments': active_commitments,
            'completed_commitments': completed_commitments,
            'funds_by_status': funds_by_status
        }
