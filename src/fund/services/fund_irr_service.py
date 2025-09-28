"""
Fund IRR Service.
"""

from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy.orm import Session

from src.fund.models import Fund, FundEvent, FundFieldChange
from src.fund.enums.fund_event_enums import EventType
from src.fund.enums.fund_enums import FundStatus
from src.fund.repositories import FundEventRepository
from src.shared.services.shared_irr_service import SharedIrRService


class FundIrRService:
    """
    Fund IRR Service.

    This module provides the FundIrRService class, which handles fund IRR operations and business logic.
    The service provides clean separation of concerns for:
    - Update the IRRs of a fund
        - Update the completed IRRs of a fund
        - Update the completed after-tax IRRs of a fund
        - Update the completed real IRRs of a fund
    - Calculate the completed IRRs of a fund
    - Calculate the completed after-tax IRRs of a fund
    - Calculate the completed real IRRs of a fund

    The service uses the FundEventRepository and IRRCalculator to perform operations.
    The service is used by the FundEventSecondaryService to update the IRRs of a fund.
    """
    
    def __init__(self):
        """
        Initialize the FundIrRService.
        
        Args:
            fund_event_repository: Fund event repository to use. If None, creates a new one.
            irr_calculator: IRR calculator to use. If None, creates a new one.
        """
        self.fund_event_repository = FundEventRepository()
        self.shared_irr_service = SharedIrRService()

    def update_irrs(self, fund: Fund, session: Session) -> Optional[List[FundFieldChange]]:
        """
        Calculate and store IRRs for a specific fund status.
                
        Args:
            fund: The fund object
            session: Database session (optional)
        """
        old_completed_irr_gross = fund.completed_irr_gross
        old_completed_irr_after_tax = fund.completed_irr_after_tax
        old_completed_irr_real = fund.completed_irr_real
        
        if fund.status == FundStatus.ACTIVE:
            # ACTIVE: No IRRs meaningful (fund has capital at risk)
            fund.completed_irr_gross = None
            fund.completed_irr_after_tax = None
            fund.completed_irr_real = None
            
        elif fund.status == FundStatus.REALIZED:
            # REALIZED: Only gross IRR is meaningful (all capital returned)
            events = self.fund_event_repository.get_fund_events(session, fund_ids=[fund.id])
            fund.completed_irr_gross = self.shared_irr_service.calculate_irr_base(events, include_tax_payments=False, include_risk_free_charges=False, include_eofy_debt_cost=False)
            fund.completed_irr_after_tax = None  # Not meaningful until completed
            fund.completed_irr_real = None       # Not meaningful until completed

        elif fund.status == FundStatus.COMPLETED:
            # COMPLETED: All IRRs are meaningful (tax obligations complete)
            events = self.fund_event_repository.get_fund_events(session, fund_ids=[fund.id])
            fund.completed_irr_gross = self.shared_irr_service.calculate_irr_base(events, include_tax_payments=False, include_risk_free_charges=False, include_eofy_debt_cost=False)
            fund.completed_irr_after_tax = self.shared_irr_service.calculate_irr_base(events, include_tax_payments=True, include_risk_free_charges=False, include_eofy_debt_cost=False)
            fund.completed_irr_real = self.shared_irr_service.calculate_irr_base(events, include_tax_payments=True, include_risk_free_charges=True, include_eofy_debt_cost=True)

        irr_changes = []
        if old_completed_irr_gross != fund.completed_irr_gross:
            irr_changes.append(FundFieldChange(fund_or_company='FUND', object_id=fund.id, field_name='completed_irr_gross', old_value=old_completed_irr_gross, new_value=fund.completed_irr_gross))
        if old_completed_irr_after_tax != fund.completed_irr_after_tax:
            irr_changes.append(FundFieldChange(fund_or_company='FUND', object_id=fund.id, field_name='completed_irr_after_tax', old_value=old_completed_irr_after_tax, new_value=fund.completed_irr_after_tax))
        if old_completed_irr_real != fund.completed_irr_real:
            irr_changes.append(FundFieldChange(fund_or_company='FUND', object_id=fund.id, field_name='completed_irr_real', old_value=old_completed_irr_real, new_value=fund.completed_irr_real))
        
        return irr_changes if irr_changes else None
    