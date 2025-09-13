"""
Fund Status Service.

This service handles all fund status transitions and calculations,
extracting complex status logic from the Fund model.

Key responsibilities:
- Status transition validation
- End date calculations
- Status-based IRR calculations
- Tax statement status checks
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from src.fund.enums import FundStatus
from src.fund.models import Fund, FundFieldChange

# Configure logger for this module
logger = logging.getLogger(__name__)

class FundStatusService:
    """
    Service for handling fund status management extracted from the Fund model.
    
    This service provides clean separation of concerns for:
    - Status transition logic and business rules
    - Status updates triggered by equity events
    - Status updates triggered by tax statements
    - Status determination logic
    - End date calculation logic
    """
    
    def __init__(self):
        """
        Initialize the FundStatusService.
        
        Args:
            None
        """
        pass
    
    # ============================================================================
    # STATUS TRANSITION LOGIC AND BUSINESS RULES
    # ============================================================================
    
    def update_status_after_equity_event(self, fund: 'Fund', session: Optional[Session] = None) -> bool:
        """
        Update the fund status based on current equity balance and tax statement status.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)

        Returns:
            bool: True if status updated, False otherwise
        """
        old_status = fund.status
        # Trust the fund's current state - event handlers should maintain current_equity_balance
        if fund.current_equity_balance > 0 and fund.status != FundStatus.ACTIVE:
            fund.status = FundStatus.ACTIVE
            logger.info(f"Fund {fund.name} status updated to ACTIVE")
        elif fund.current_equity_balance <= 0 and fund.status == FundStatus.ACTIVE:
            fund.status = FundStatus.REALIZED
            if self._is_final_tax_statement_received(fund, session):
                fund.status = FundStatus.COMPLETED
                logger.info(f"Fund {fund.name} status updated to COMPLETED")
            else:
                logger.info(f"Fund {fund.name} status updated to REALIZED")
        status_changes = []
        if old_status != fund.status:
            status_changes.append(FundFieldChange(field_name='status', old_value=old_status, new_value=fund.status))
        return status_changes if status_changes else None
    
    def update_status_after_tax_statement(self, fund: 'Fund', session: Optional[Session] = None) -> bool:
        """
        Update fund status after a tax statement event.
                
        Args:
            fund: The fund object
            session: Database session (optional)

        Returns:
            bool: True if status updated, False otherwise
        """
        old_status = fund.status
        if fund.status != FundStatus.ACTIVE:
            # Check if this tax statement makes the fund completed
            if self._is_final_tax_statement_received(fund, session):
                if fund.status != FundStatus.COMPLETED:
                    fund.status = FundStatus.COMPLETED
                    logger.info(f"Fund {fund.name} status updated to COMPLETED")
                    
            else:
                # Tax statement removed, revert to realized if was completed
                if fund.status == FundStatus.COMPLETED:
                    fund.status = FundStatus.REALIZED
                    logger.info(f"Fund {fund.name} status reverted to REALIZED")
                    
        status_changes = []
        if old_status != fund.status:
            status_changes.append(FundFieldChange(field_name='status', old_value=old_status, new_value=fund.status))
        return status_changes if status_changes else None
    
    def _is_final_tax_statement_received(self, fund: 'Fund', session: Optional[Session] = None) -> bool:
        """
        Check if the final tax statement has been received for a realized fund.
        
        Business Logic:
        A fund is considered COMPLETED when it has received a tax statement for a tax period
        where the tax payment date is after the fund's end date. This indicates that all
        tax obligations for periods after the fund ended are now due and payable.
        
        Implementation:
        - Compare tax_payment_date to end_date (most accurate and reliable)
        - No fallback logic needed since tax_payment_date is already validated
                
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            bool: True if final tax statement received, False otherwise
        """
        if fund.status == FundStatus.ACTIVE:
            return False
        
        # Get the fund's end date
        end_date = fund.end_date
        if not end_date:
            return False
        
        # Use repository for data access instead of direct model access
        from src.fund.repositories import TaxStatementRepository
        tax_statement_repository = TaxStatementRepository()
        
        # Check if there's a tax statement with a tax payment date after the end date
        # This indicates that tax obligations for periods after the fund ended are now due
        tax_statements = tax_statement_repository.get_by_fund_after_date(fund.id, end_date, session)
        
        # Return True if any tax statement has a payment date after the end date
        return len(tax_statements) > 0