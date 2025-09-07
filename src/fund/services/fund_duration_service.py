"""
Fund Duration Service.

Business logic and coordination for fund duration operations.
"""

from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from src.fund.models import Fund
from src.fund.enums import FundStatus
from src.fund.calculators.fund_duration_calculator import FundDurationCalculator


class FundDurationService:
    """Service for fund duration business logic and coordination."""
    
    def __init__(self):
        """Initialize the duration service."""
        self.calculator = FundDurationCalculator()
    
    def calculate_fund_duration(self, fund: Fund) -> Optional[int]:
        """Calculate fund duration based on business rules.
        
        For ACTIVE funds: calculates duration from start_date to today
        For REALIZED/COMPLETED funds: calculates duration from start_date to end_date
        
        Args:
            fund: The fund to calculate duration for
            
        Returns:
            int or None: Calculated duration in months
        """
        if not fund.start_date:
            return None
        
        # Determine the end date based on fund status (business logic)
        if fund.status in [FundStatus.REALIZED, FundStatus.COMPLETED]:
            if not fund.end_date:
                return None
            end_date = fund.end_date
        else:
            end_date = date.today()
        
        # Use calculator for pure mathematical calculation
        return self.calculator.calculate_duration_months(fund.start_date, end_date)
    
    def update_fund_duration(self, fund: Fund, session: Session) -> Optional[int]:
        """Update fund duration and persist changes.
        
        Args:
            fund: The fund to update
            session: Database session
            
        Returns:
            int or None: Calculated duration in months
        """
        calculated_duration = self.calculate_fund_duration(fund)
        fund.current_duration = calculated_duration
        return calculated_duration
    
    def daily_update_fund_duration(self, fund: Fund, session: Session) -> Optional[int]:
        """Update fund duration only if fund is active (daily update logic).
        
        Args:
            fund: The fund to update
            session: Database session
            
        Returns:
            int or None: Calculated duration in months
        """
        if fund.is_active():
            return self.calculator.calculate_duration_months(fund.start_date, date.today())
        return None
