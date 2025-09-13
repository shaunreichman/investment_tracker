"""
Service for handling fund NAV calculations.
"""

from sqlalchemy.orm import Session
from src.fund.repositories import FundEventRepository
from src.fund.enums import EventType, SortOrder
from src.fund.models import Fund, FundFieldChange, FundEvent
import logging
from typing import List

class FundNavService:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def update_nav_fund_fields(self, fund: Fund, session: Session) -> List[FundFieldChange]:
        """
        Update the NAV of a fund.
        """
        old_current_unit_price = fund.current_unit_price
        old_current_nav_total = fund.current_nav_total

        events = FundEventRepository.get_by_fund(fund.id, session, 
                    event_types=[EventType.NAV_UPDATE],
                    sort_order=SortOrder.ASC)
        if events:
            fund.current_unit_price = events[0].event_data['nav_per_share']
            fund.current_nav_total = events[0].event_data['nav_per_share'] * events[0].event_data['units_owned']

        self.update_nav_fund_event_fields(events)

        nav_changes = []
        if old_current_unit_price != fund.current_unit_price:
            nav_changes.append(FundFieldChange(field_name='current_unit_price', old_value=old_current_unit_price, new_value=fund.current_unit_price))
        if old_current_nav_total != fund.current_nav_total:
            nav_changes.append(FundFieldChange(field_name='current_nav_total', old_value=old_current_nav_total, new_value=fund.current_nav_total))

        return nav_changes if nav_changes else None

    def update_nav_fund_event_fields(self, events: List[FundEvent]) -> None:
        """
        Update the NAV fields of the nav update fund events.
        """
        previous_nav_per_share = None
        for event in events:
            if previous_nav_per_share is not None:
                event.previous_nav_per_share = previous_nav_per_share
                event.nav_change_absolute = event.event_data['nav_per_share'] - previous_nav_per_share
                event.nav_change_percentage = (event.event_data['nav_per_share'] - previous_nav_per_share) / previous_nav_per_share
            previous_nav_per_share = event.event_data['nav_per_share']