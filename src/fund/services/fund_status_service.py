"""
Fund Status Service.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from src.fund.enums import FundStatus
from src.fund.models import Fund
from src.shared.models import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.fund.repositories import FundTaxStatementRepository

class FundStatusService:
    """
    Fund Status Service.

    This module provides the FundStatusService class, which handles fund status operations and business logic.
    The service provides clean separation of concerns for:
    - Status transition logic and business rules
    - Status updates triggered by equity events
    - Status updates triggered by tax statements
    - Status determination logic
    - End date calculation logic

    The service uses the FundRepository to perform operations.
    The service is used by the FundEventSecondaryService to update the status of a fund.
    """
    
    def __init__(self):
        """
        Initialize the FundStatusService.
        
        Args:
            None
        """
        self.fund_tax_statement_repository = FundTaxStatementRepository()
    
    # ============================================================================
    # STATUS TRANSITION LOGIC AND BUSINESS RULES
    # ============================================================================
    
    def update_status_after_equity_event(self, fund: Fund, session: Optional[Session] = None) -> Optional[List[DomainFieldChange]]:
        """
        Update the fund status based on current equity balance and tax statement status.
        
        Args:
            fund: The fund object
            session: Database session (optional)

        Returns:
            Optional[List[DomainFieldChange]]: List of field changes if status updated, None otherwise
        """
        old_status = fund.status
        
        if fund.current_equity_balance > 0 and fund.status != FundStatus.ACTIVE:
            fund.status = FundStatus.ACTIVE
        elif fund.current_equity_balance <= 0 and fund.status == FundStatus.ACTIVE:
            fund.status = FundStatus.REALIZED
            if self._is_final_tax_statement_received(fund, session):
                fund.status = FundStatus.COMPLETED

        status_changes = []
        if old_status != fund.status:
            status_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.FUND, domain_object_id=fund.id, field_name='status', old_value=old_status, new_value=fund.status))
        return status_changes if status_changes else None
    
    def update_status_after_tax_statement(self, fund: Fund, session: Optional[Session] = None) -> Optional[List[DomainFieldChange]]:
        """
        Update fund status after a tax statement event.
                
        Args:
            fund: The fund object
            session: Database session (optional)

        Returns:
            Optional[List[DomainFieldChange]]: List of field changes if status updated, None otherwise
        """
        old_status = fund.status
        if fund.status != FundStatus.ACTIVE:
            # Check if this tax statement makes the fund completed
            if self._is_final_tax_statement_received(fund, session):
                if fund.status != FundStatus.COMPLETED:
                    fund.status = FundStatus.COMPLETED                    
            else:
                # Tax statement removed, revert to realized if was completed
                if fund.status == FundStatus.COMPLETED:
                    fund.status = FundStatus.REALIZED
                    
        status_changes = []
        if old_status != fund.status:
            status_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.FUND, domain_object_id=fund.id, field_name='status', old_value=old_status, new_value=fund.status))
        return status_changes if status_changes else None
    
    def _is_final_tax_statement_received(self, fund: Fund, session: Optional[Session] = None) -> bool:
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
        
        tax_statements = self.fund_tax_statement_repository.get_fund_tax_statements(fund_ids=[fund.id], start_tax_payment_date=end_date, session=session)
        
        # Return True if any tax statement has a payment date after the end date
        return len(tax_statements) > 0