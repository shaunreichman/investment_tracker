"""
Company Equity Service.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from src.fund.models.domain_fund_event import FundFieldChange
from src.investment_company.repositories import CompanyRepository
from src.fund.repositories import FundEventRepository
from src.investment_company.calculators.company_equity_balance_calculator import CompanyEquityBalanceCalculator
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import SortOrder
from src.shared.calculators.duration_months_calculator import DurationMonthsCalculator

class CompanyEquityService:
    """
    Company Equity Service.

    This module provides the CompanyEquityService class, which handles company equity operations and business logic.
    The service provides clean separation of concerns for:
    - Update the equity fields of a company
        - Update the average equity balance of a company
        - Update the current equity balance of a company
        - Update the end date of a company
        - Update the duration of a company

    The service uses the CompanyRepository, FundEventRepository, and CompanyEquityBalanceCalculator to perform operations.
    The service is used by the CompanyEventSecondaryService to update the equity fields of a company.
    """
    def __init__(self):
        """
        Initialize the CompanyEquityService.

        Args:
            company_repository: Company repository to use. If None, creates a new one.
            fund_event_repository: Fund event repository to use. If None, creates a new one.
            company_equity_calculator: Company equity calculator to use. If None, creates a new one.
        """
        self.company_repository = CompanyRepository()
        self.fund_event_repository = FundEventRepository()
        self.company_equity_calculator = CompanyEquityBalanceCalculator()

    def update_company_equity_fields(self, company_id: int, fund_ids: List[int], session: Session) -> Optional[List[FundFieldChange]]:
        """
        Update the equity fields of a company.
        """

        company = self.company_repository.get_company_by_id(company_id, session)
        if not company:
            raise ValueError(f"Company not found")

        changes: list[FundFieldChange] = []

        old_average_equity_balance = company.average_equity_balance
        old_current_equity_balance = company.current_equity_balance
        old_end_date = company.end_date

        fund_events = self.fund_event_repository.get_fund_events(session, fund_ids=fund_ids,
            event_types=[EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
            sort_order=SortOrder.ASC
        )
        average_equity_balance, current_equity_balance, last_event_date = self.company_equity_calculator.calculate_company_equity_balance(fund_events)

        if old_average_equity_balance != average_equity_balance:
            changes.append(FundFieldChange(object='COMPANY', object_id=company_id, field_name='average_equity_balance', old_value=old_average_equity_balance, new_value=average_equity_balance))
            company.average_equity_balance = average_equity_balance
        if old_current_equity_balance != current_equity_balance:
            changes.append(FundFieldChange(object='COMPANY', object_id=company_id, field_name='current_equity_balance', old_value=old_current_equity_balance, new_value=current_equity_balance))
            company.current_equity_balance = current_equity_balance
        if old_end_date != last_event_date:
            changes.append(FundFieldChange(object='COMPANY', object_id=company_id, field_name='end_date', old_value=old_end_date, new_value=last_event_date))
            company.end_date = last_event_date

            # If the end Date changes we need to update the duration
            old_duration = company.current_duration
            new_duration = DurationMonthsCalculator.calculate_duration_months(company.start_date, last_event_date)
            if old_duration != new_duration:
                changes.append(FundFieldChange(object='COMPANY', object_id=company_id, field_name='current_duration', old_value=old_duration, new_value=new_duration))
                company.current_duration = new_duration

        return changes if changes else None