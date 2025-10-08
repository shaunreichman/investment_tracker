"""
Fund NAV Service.
"""

from sqlalchemy.orm import Session
from src.fund.repositories import FundEventRepository
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import SortOrder
from src.fund.models import Fund, FundEvent
from src.shared.models import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from typing import List

class FundNavService:
    """
    Fund NAV Service.

    This module provides the FundNavService class, which handles fund NAV operations and business logic.
    The service provides clean separation of concerns for:
    - Update the NAV of a fund
    - Update the NAV of a fund event
    """
    def __init__(self):
        """
        Initialize the FundNavService.
        
        Args:
            fund_event_repository: Fund event repository to use. If None, creates a new one.
        """
        self.fund_event_repository = FundEventRepository()


    def update_nav_fund_fields(self, fund: Fund, session: Session) -> List[DomainFieldChange]:
        """
        Update the NAV of a fund.

        Args:
            fund: The fund object
            session: Database session

        Returns:
            List[DomainFieldChange] with updated values and metadata
        """
        old_current_unit_price = fund.current_unit_price
        old_current_nav_total = fund.current_nav_total

        # Get the latest NAV update event
        nav_events = self.fund_event_repository.get_fund_events(session, fund_ids=[fund.id], 
                    event_types=[EventType.NAV_UPDATE],
                    sort_order=SortOrder.ASC)
        
        # Get the latest unit event to determine current units owned
        unit_events = self.fund_event_repository.get_fund_events(session, fund_ids=[fund.id], 
                    event_types=[EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
                    sort_order=SortOrder.ASC)
        
        if nav_events and unit_events:
            latest_nav_event = nav_events[-1]  # Get the most recent NAV update
            latest_unit_event = unit_events[-1]  # Get the most recent unit event
            
            fund.current_unit_price = latest_nav_event.nav_per_share
            fund.current_nav_total = latest_nav_event.nav_per_share * latest_unit_event.units_owned

        
        event_changes = self._update_nav_fund_event_fields(nav_events)

        nav_changes = []
        if event_changes:
            nav_changes.extend(event_changes)

        if old_current_unit_price != fund.current_unit_price:
            nav_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.FUND, domain_object_id=fund.id, field_name='current_unit_price', old_value=old_current_unit_price, new_value=fund.current_unit_price))
        if old_current_nav_total != fund.current_nav_total:
            nav_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.FUND, domain_object_id=fund.id, field_name='current_nav_total', old_value=old_current_nav_total, new_value=fund.current_nav_total))

        return nav_changes if nav_changes else None

    def _update_nav_fund_event_fields(self, events: List[FundEvent]) -> List[DomainFieldChange]:
        """
        Update the NAV fields of the nav update fund events.

        Args:
            events: List of FundEvent objects

        Returns:
            List[DomainFieldChange] with updated values and metadata
        """
        if events is None:
            return

        nav_changes = []

        previous_nav_per_share = None
        for event in events:
            if previous_nav_per_share is not None:
                old_previous_nav_per_share = event.previous_nav_per_share
                old_nav_change_absolute = event.nav_change_absolute
                old_nav_change_percentage = event.nav_change_percentage

                event.previous_nav_per_share = previous_nav_per_share
                event.nav_change_absolute = event.nav_per_share - previous_nav_per_share
                # Handle division by zero for percentage calculation
                if previous_nav_per_share != 0:
                    event.nav_change_percentage = (event.nav_per_share - previous_nav_per_share) / previous_nav_per_share
                else:
                    event.nav_change_percentage = None  # Cannot calculate percentage from zero

                if old_previous_nav_per_share != event.previous_nav_per_share:
                    nav_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.FUND_EVENT, domain_object_id=event.id, field_name='previous_nav_per_share', old_value=old_previous_nav_per_share, new_value=event.previous_nav_per_share))
                if old_nav_change_absolute != event.nav_change_absolute:
                    nav_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.FUND_EVENT, domain_object_id=event.id, field_name='nav_change_absolute', old_value=old_nav_change_absolute, new_value=event.nav_change_absolute))
                if old_nav_change_percentage != event.nav_change_percentage:
                    nav_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.FUND_EVENT, domain_object_id=event.id, field_name='nav_change_percentage', old_value=old_nav_change_percentage, new_value=event.nav_change_percentage))

            previous_nav_per_share = event.nav_per_share

        return nav_changes if nav_changes else None