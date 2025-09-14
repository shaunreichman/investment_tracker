"""
Service for handling fund date calculations.
"""

from src.fund.models import Fund, FundEvent, FundFieldChange
from src.shared.enums import SortOrder
from src.shared.enums import EventOperation
from src.fund.repositories import FundEventRepository, FundRepository
from src.entity.repositories import EntityRepository
from typing import Optional, List
from sqlalchemy.orm import Session
import logging
from datetime import date

class FundDateService:
    def __init__(self, session: Session):
        self.fund_repository = FundRepository()
        self.fund_event_repository = FundEventRepository()
        self.entity_repository = EntityRepository()
        self.logger = logging.getLogger(__name__)

    def update_fund_start_date(self, fund_id: int, session: Session, event_id: Optional[int] = None, fund_event_operation: EventOperation = None) -> Optional[FundFieldChange]:
        """
        Update the start date of a fund.
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None

        old_start_date = fund.start_date

        if fund_event_operation == EventOperation.CREATE:
            # Faster to update the start date of the fund by looking at the event
            event = self.fund_event_repository.get_by_id(event_id, session)
            if not event or event.fund_id != fund_id:
                return None
            if event.event_type == EventType.CAPITAL_CALL or event.event_type == EventType.UNIT_PURCHASE:
                if not fund.start_date or event.event_date < fund.start_date:
                    fund.start_date = event.event_date
                    self.logger.info(f"Updated fund {fund.id} start_date to {event.event_date}")
        else:
            # Update the start date of the fund by looking at all the fund events
            events = self.fund_event_repository.get_by_fund(fund_id=fund_id,
                                            session=session,
                                            event_types=[EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE],
                                            sort_order=SortOrder.ASC)
            if events:
                if not fund.start_date or fund.start_date > events[0].event_date:
                    fund.start_date = events[0].event_date
                    self.logger.info(f"Updated fund {fund.id} start_date to {events[0].event_date}")
        if old_start_date != fund.start_date:
            return FundFieldChange(field_name='start_date', old_value=old_start_date, new_value=fund.start_date)
        return None

    def update_fund_end_date(self, fund_id: int, session: Session) -> Optional[FundFieldChange]:
        """
        Update the end date of a fund.
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None

        old_end_date = fund.end_date
        
        if fund.status == FundStatus.REALIZED or fund.status == FundStatus.COMPLETED:
            events = self.fund_event_repository.get_by_fund(fund_id=fund_id,
                                            session=session,
                                            event_types=[EventType.RETURN_OF_CAPITAL, EventType.UNIT_SALE],
                                            sort_order=SortOrder.DESC)
            if events:
                if not fund.end_date or events[0].event_date > fund.end_date:
                    fund.end_date = events[0].event_date
                    self.logger.info(f"Updated fund {fund.id} end_date to {events[0].event_date}")

        if old_end_date != fund.end_date:
            return FundFieldChange(field_name='end_date', old_value=old_end_date, new_value=fund.end_date)
        return None

    def update_fund_duration(self, fund: 'Fund', session: Session) -> Optional[FundFieldChange]:
        """
        Update the duration of a fund.
        """
        if not fund.start_date:
            raise ValueError ("Fund.start_date not set - can't set the current_duration") 
        old_duration = fund.current_duration

        if fund.end_date:
            end = fund.end_date
        else:
            end = date.today()

        from src.fund.calculators.fund_duration_calculator import FundDurationCalculator
        fund.current_duration = FundDurationCalculator.calculate_duration_months(fund.start_date, end)
        self.logger.info(f"Updated fund {fund.id} duration to {fund.current_duration}")
        if old_duration != fund.current_duration:
            return FundFieldChange(field_name='current_duration', old_value=old_duration, new_value=fund.current_duration)
        return None

    def get_fund_financial_years(self, fund: 'Fund', session: Session) -> List[str]:
        """
        Get all financial years from fund start date to current date.
        
        Args:
            fund: The fund object
            session: Database session
            
        Returns:
            List[str]: List of financial years in descending order (most recent first)
        """
        # Get fund start date (use events if available, otherwise creation date)
        start_date = fund.start_date
        if not start_date:
            raise ValueError("Fund.start_date is not set")
        
        # Get entity for tax jurisdiction
        entity = self.entity_repository.get_by_id(fund.entity_id, session)
        if not entity:
            raise ValueError("Entity is not set")
        
        # Import calculation function from entity domain
        from src.entity.calculations import get_financial_years_for_fund_period
        
        # Calculate financial years from start date to current date
        end_date = date.today()
        financial_years = get_financial_years_for_fund_period(start_date, end_date, entity)
        
        # Return sorted list (most recent first)
        return sorted(list(financial_years), reverse=True)