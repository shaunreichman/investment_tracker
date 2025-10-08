"""
Fund Date Service.
"""

from src.fund.models import Fund
from src.shared.models import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.shared.enums.shared_enums import SortOrder, EventOperation
from src.fund.enums.fund_event_enums import EventType
from src.fund.enums.fund_enums import FundStatus, FundTaxStatementFinancialYearType
from src.fund.repositories import FundEventRepository, FundRepository
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import date

class FundDateService:
    """
    Fund Date Service.

    This module provides the FundDateService class, which handles fund date operations and business logic.
    The service provides clean separation of concerns for:
    - Update the start date of a fund
    - Update the end date of a fund
    - Update the duration of a fund
    - Get the financial years of a fund
    """
    def __init__(self):
        """
        Initialize the FundDateService.

        Args:
            fund_repository: Fund repository to use. If None, creates a new one.
            fund_event_repository: Fund event repository to use. If None, creates a new one.
        """
        self.fund_repository = FundRepository()
        self.fund_event_repository = FundEventRepository()
    
    def update_fund_start_date(self, fund: Fund, session: Session, fund_event_id: Optional[int] = None, fund_event_operation: EventOperation = None) -> Optional[DomainFieldChange]:
        """
        Update the start date of a fund.

        Args:
            fund: Fund object to update
            session: Database session
            fund_event_id: ID of the event to update the start date from
            fund_event_operation: Operation of the fund event
            
        Returns:
            DomainFieldChange object if the start date was updated, None otherwise
            
        Raises:
            ValueError: If the fund is not found
        """
        if fund is None:
            return None
        
        old_start_date = fund.start_date

        if fund_event_operation == EventOperation.CREATE:
            # Faster to update the start date of the fund by looking at the event
            event = self.fund_event_repository.get_fund_event_by_id(fund_event_id, session)
            if not event or event.fund_id != fund.id:
                return None
            if event.event_type == EventType.CAPITAL_CALL or event.event_type == EventType.UNIT_PURCHASE:
                if not fund.start_date or event.event_date < fund.start_date:
                    fund.start_date = event.event_date

        else:
            # Update the start date of the fund by looking at all the fund events
            events = self.fund_event_repository.get_fund_events(session=session, fund_ids=[fund.id],
                                            event_types=[EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE],
                                            sort_order=SortOrder.ASC)
            if events:
                if not fund.start_date or fund.start_date > events[0].event_date:
                    fund.start_date = events[0].event_date

        if old_start_date != fund.start_date:
            return DomainFieldChange(domain_object_type=DomainObjectType.FUND, domain_object_id=fund.id, field_name='start_date', old_value=old_start_date, new_value=fund.start_date)
        return None

    def update_fund_end_date(self, fund: Fund, session: Session) -> Optional[DomainFieldChange]:
        """
        Update the end date of a fund.
        
        Args:
            fund: Fund object to update
            session: Database session
            
        Returns:
            DomainFieldChange object if the end date was updated, None otherwise
            
        Raises:
            ValueError: If the fund is not found
        """
        if fund is None:
            return None
        
        old_end_date = fund.end_date
        
        if fund.status == FundStatus.REALIZED or fund.status == FundStatus.COMPLETED:
            events = self.fund_event_repository.get_fund_events(session=session, fund_ids=[fund.id],
                                            event_types=[EventType.RETURN_OF_CAPITAL, EventType.UNIT_SALE],
                                            sort_order=SortOrder.DESC)
            if events:
                if not fund.end_date or events[0].event_date > fund.end_date:
                    fund.end_date = events[0].event_date

        if old_end_date != fund.end_date:
            return DomainFieldChange(domain_object_type=DomainObjectType.FUND, domain_object_id=fund.id, field_name='end_date', old_value=old_end_date, new_value=fund.end_date)
        return None

    def update_fund_duration(self, fund: Fund, session: Session) -> Optional[DomainFieldChange]:
        """
        Update the duration of a fund.

        Args:
            fund: The fund object
            session: Database session
            
        Returns:
            DomainFieldChange object if the duration was updated, None otherwise
            
        Raises:
            ValueError: If the fund is not found
            ValueError: If the fund start date is not set
        """
        if not fund.start_date:
            raise ValueError ("Fund.start_date not set - can't set the current_duration") 
        old_duration = fund.current_duration

        if fund.end_date:
            end = fund.end_date
        else:
            end = date.today()

        from src.shared.calculators.duration_months_calculator import DurationMonthsCalculator
        fund.current_duration = DurationMonthsCalculator.calculate_duration_months(fund.start_date, end)
        if old_duration != fund.current_duration:
            return DomainFieldChange(domain_object_type=DomainObjectType.FUND, domain_object_id=fund.id, field_name='current_duration', old_value=old_duration, new_value=fund.current_duration)
        return None

    def get_fund_financial_years(self, fund: Fund) -> List[str]:
        """
        Get all financial years from fund start date to current date.
        
        Args:
            fund: The fund object
            
        Returns:
            List[str]: List of financial years in descending order (most recent first)
            
        Raises:
            ValueError: If the fund start date is not set
            ValueError: If the financial year type is invalid
        """
        # Get fund start date (use events if available, otherwise creation date)
        start_date = fund.start_date
        if not start_date:
            raise ValueError("Fund.start_date is not set")

        end_date = date.today()

        financial_years = set()
        
        financial_year_type = fund.tax_statement_financial_year_type
        if financial_year_type == FundTaxStatementFinancialYearType.CALENDAR_YEAR:
            for year in range(start_date.year, end_date.year + 1):
                financial_years.add(str(year))
        elif financial_year_type == FundTaxStatementFinancialYearType.HALF_YEAR:
            if start_date.month <= 6:
                start_year = start_date.year
            else:
                start_year = start_date.year + 1
            if end_date.month <= 6:
                end_year = end_date.year
            else:
                end_year = end_date.year + 1
            for year in range(start_year, end_year + 1):
                financial_years.add(str(year))
        else:
            raise ValueError(f"Invalid financial year type: {financial_year_type}")
        
        return financial_years