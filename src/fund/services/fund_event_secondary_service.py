"""
FundEventSecondaryService is responsible for handling secondary impacts of fund events.
"""

from src.fund.models import Fund, FundFieldChange
import logging
from src.fund.enums import EventType
from src.shared.enums.shared_enums import EventOperation
from sqlalchemy.orm import Session
from src.fund.services.fund_equity_service import FundEquityService
from src.fund.services.fund_status_service import FundStatusService
from src.fund.services.fund_date_service import FundDateService
from src.fund.services.fund_irr_service import FundIrRService
from src.fund.services.fund_pnl_service import FundPnlService
from src.fund.services.fund_nav_service import FundNavService

class FundEventSecondaryService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def handle_event_secondary_impact(self, fund_id: int, fund_event_type: EventType, 
                                    fund_event_operation: EventOperation,
                                    session: Session,
                                    event_id: int):            
        
        fund_date_service = FundDateService(session)
        fund_equity_service = FundEquityService(session)
        fund_status_service = FundStatusService(session)
        fund_irr_service = FundIrRService(session)
        fund_pnl_service = FundPnlService(session)
        fund_nav_service = FundNavService(session)
        
        all_changes: list[FundFieldChange] = []

        fund = self.fund_repository.get_fund_by_id(fund_id, session)

        # 1. Update the Start Date of the Fund
        if EventType.is_equity_call_event(fund_event_type):
            if fund_event_operation == EventOperation.CREATE:
                all_changes.append(fund_date_service.update_fund_start_date(fund_id=fund.id, event_id=event_id, fund_event_operation=fund_event_operation, session=session))
            else:
                all_changes.append(fund_date_service.update_fund_start_date(fund_id=fund.id, fund_event_operation=fund_event_operation, session=session))
        
        # 2. Update the current equity balance of the fund
        if EventType.is_equity_event(fund_event_type):
            all_changes.append(fund_equity_service.update_fund_equity_fields(fund, session, current_equity_flag=True))

        # 3. Update the End Date of the Fund
        if EventType.is_equity_return_event(fund_event_type):
            all_changes.append(fund_date_service.update_fund_end_date(fund.id, session))

        # 4. Update the other balances of the fund
        if EventType.is_equity_event(fund_event_type):
            all_changes.append(fund_equity_service.update_fund_equity_fields(fund, session, current_equity_flag=False))

        # 5. Update the Fund Status
        if EventType.is_equity_event(fund_event_type):
            all_changes.append(fund_status_service.update_status_after_equity_event(fund, session))
        if EventType.is_tax_statement_event(fund_event_type):
            all_changes.append(fund_status_service.update_status_after_tax_statement(fund, session))

        # 6. Update the Duration of the Fund
        if EventType.is_equity_event(fund_event_type):
            all_changes.append(fund_date_service.update_fund_duration(fund, session))

        # 7. Update the IRRs of the fund
        all_changes.append(fund_irr_service.update_irrs(fund, session))

        ##### If deleting a capital event, we should check if a debt cost exists on this date and if so we should recalculate the debt costs for the fund

        # 8. Update the NAV of the Fund
        if fund_event_type == EventType.NAV_UPDATE:
            all_changes.append(fund_nav_service.update_nav_fund_fields(fund, session))

        # 9. Update the Profitability of the Fund
        all_changes.append(fund_pnl_service.update_fund_pnl(fund, session))

        return all_changes