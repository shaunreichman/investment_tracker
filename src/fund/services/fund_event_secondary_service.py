"""
Fund Event Secondary Service.
"""

from src.fund.models import FundFieldChange
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import EventOperation
from sqlalchemy.orm import Session
from src.fund.services.fund_equity_service import FundEquityService
from src.fund.services.fund_status_service import FundStatusService
from src.fund.services.fund_date_service import FundDateService
from src.fund.services.fund_irr_service import FundIrRService
from src.fund.services.fund_pnl_service import FundPnlService
from src.fund.services.fund_nav_service import FundNavService
from src.fund.repositories import FundRepository

class FundEventSecondaryService:
    """
    Fund Event Secondary Service.

    This module provides the FundEventSecondaryService class, which handles fund event secondary operations and business logic.
    The service provides clean separation of concerns for:
    - Fund event secondary impact handling
        - Update the Start Date of the Fund
        - Update the current equity balance of the fund
        - Update the End Date of the Fund
        - Update the other balances of the fund
        - Update the Fund Status
        - Update the Duration of the Fund
        - Update the IRRs of the fund
        - Update the NAV of the Fund
        - Update the Profitability of the Fund

    The service uses the FundEquityService, FundStatusService, FundDateService, FundIrRService, FundPnlService, FundNavService, and FundRepository to perform secondary operations.
    The service is used by the FundEventService to handle fund event secondary operations.
    """
    def __init__(self):
        """
        Initialize the FundEventSecondaryService.

        Args:
            fund_equity_service: Fund equity service to use. If None, creates a new one.
            fund_status_service: Fund status service to use. If None, creates a new one.
            fund_date_service: Fund date service to use. If None, creates a new one.
            fund_irr_service: Fund irr service to use. If None, creates a new one.
            fund_pnl_service: Fund pnl service to use. If None, creates a new one.
            fund_nav_service: Fund nav service to use. If None, creates a new one.
            fund_repository: Fund repository to use. If None, creates a new one.
        """
        self.fund_equity_service = FundEquityService()
        self.fund_status_service = FundStatusService()
        self.fund_date_service = FundDateService()
        self.fund_irr_service = FundIrRService()
        self.fund_pnl_service = FundPnlService()
        self.fund_nav_service = FundNavService()
        self.fund_repository = FundRepository()

    def handle_event_secondary_impact(self, fund_id: int, fund_event_type: EventType, 
                                    fund_event_operation: EventOperation,
                                    session: Session,
                                    event_id: int):            
        
        
        all_changes: list[FundFieldChange] = []

        fund = self.fund_repository.get_fund_by_id(fund_id, session)
        if not fund:
            raise ValueError(f"Fund not found")

        # 1. Update the Start Date of the Fund
        if EventType.is_equity_call_event(fund_event_type):
            if fund_event_operation == EventOperation.CREATE:
                all_changes.append(self.fund_date_service.update_fund_start_date(fund_id=fund.id, event_id=event_id, fund_event_operation=fund_event_operation, session=session))
            else:
                all_changes.append(self.fund_date_service.update_fund_start_date(fund_id=fund.id, fund_event_operation=fund_event_operation, session=session))
        
        # 2. Update the current equity balance of the fund
        if EventType.is_equity_event(fund_event_type):
            all_changes.append(self.fund_equity_service.update_fund_equity_fields(fund, session, current_equity_flag=True))

        # 3. Update the End Date of the Fund
        if EventType.is_equity_return_event(fund_event_type):
            all_changes.append(self.fund_date_service.update_fund_end_date(fund.id, session))

        # 4. Update the other balances of the fund
        if EventType.is_equity_event(fund_event_type):
            all_changes.append(self.fund_equity_service.update_fund_equity_fields(fund, session, current_equity_flag=False))

        # 5. Update the Fund Status
        if EventType.is_equity_event(fund_event_type):
            all_changes.append(self.fund_status_service.update_status_after_equity_event(fund, session))
        if EventType.is_tax_statement_event(fund_event_type):
            all_changes.append(self.fund_status_service.update_status_after_tax_statement(fund, session))

        # 6. Update the Duration of the Fund
        if EventType.is_equity_event(fund_event_type):
            all_changes.append(self.fund_date_service.update_fund_duration(fund, session))

        # 7. Update the IRRs of the fund
        all_changes.append(self.fund_irr_service.update_irrs(fund, session))

        ##### If deleting a capital event, we should check if a debt cost exists on this date and if so we should recalculate the debt costs for the fund

        # 8. Update the NAV of the Fund
        if fund_event_type == EventType.NAV_UPDATE:
            all_changes.append(self.fund_nav_service.update_nav_fund_fields(fund, session))

        # 9. Update the Profitability of the Fund
        all_changes.append(self.fund_pnl_service.update_fund_pnl(fund, session))

        return all_changes