"""
Fund Units Service.
"""

from src.fund.repositories import FundEventRepository
from src.fund.models import Fund, FundFieldChange
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import SortOrder
from sqlalchemy.orm import Session
from typing import List, Optional

class FundUnitsService:
    """
    Fund Units Service.
    
    This module provides the FundUnitsService class, which handles fund units operations and business logic.
    The service provides clean separation of concerns for:
    - Update the units owned of a fund
    """
    def __init__(self):
        """
        Initialize the FundUnitsService."""
        self.fund_event_repository = FundEventRepository()

    def update_fund_units(self, fund: Fund, session: Session) -> Optional[List[FundFieldChange]]:
        """
        Update the units owned of a fund.
        """
        events = self.fund_event_repository.get_fund_events(session, fund_ids=[fund.id], 
                    event_types=[EventType.UNIT_PURCHASE, EventType.UNIT_SALE, EventType.NAV_UPDATE],
                    sort_order=SortOrder.ASC)

        unit_changes = []

        units_owned = 0
        latest_unit_price = 0.0
        for event in events:
            # Update latest unit price from unit purchase/sale events
            if event.event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE] and event.unit_price is not None:
                latest_unit_price = event.unit_price
            # Update latest unit price from NAV update events
            elif event.event_type == EventType.NAV_UPDATE and event.nav_per_share is not None:
                latest_unit_price = event.nav_per_share
                
            if event.event_type == EventType.UNIT_PURCHASE:
                units_owned += event.units_purchased
            elif event.event_type == EventType.UNIT_SALE:
                units_owned -= event.units_sold
                
            # Update the fund event units owned
            if units_owned != event.units_owned:
                unit_changes.append(FundFieldChange(object='FUND_EVENT', object_id=event.id, field_name='units_owned', old_value=event.units_owned, new_value=units_owned))
                event.units_owned = units_owned

        # Update the fund units owned
        if units_owned != fund.current_units:
            unit_changes.append(FundFieldChange(object='FUND', object_id=fund.id, field_name='current_units', old_value=fund.current_units, new_value=units_owned))
            fund.current_units = units_owned

        # Update the fund unit price
        if latest_unit_price != fund.current_unit_price:
            unit_changes.append(FundFieldChange(object='FUND', object_id=fund.id, field_name='current_unit_price', old_value=fund.current_unit_price, new_value=latest_unit_price))
            fund.current_unit_price = latest_unit_price

        # Update the fund NAV total
        current_nav_total = units_owned * latest_unit_price
        if current_nav_total != fund.current_nav_total:
            unit_changes.append(FundFieldChange(object='FUND', object_id=fund.id, field_name='current_nav_total', old_value=fund.current_nav_total, new_value=current_nav_total))
            fund.current_nav_total = current_nav_total

        return unit_changes