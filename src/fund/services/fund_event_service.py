"""
Fund Event Service.

This service handles all fund event operations and calculations,
extracting complex event logic from the Fund model.

Key responsibilities:
- Event creation and validation
- Event field calculations
- Event grouping and relationships
- Event-based fund updates
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from src.fund.enums import EventType
from typing import TYPE_CHECKING

# Configure logger for this module
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.fund.models import Fund, FundEvent
    from src.fund.repositories import CapitalEventRepository, UnitEventRepository, TaxEventRepository, FundEventQueryRepository


class FundEventService:
    """
    Service for handling fund event operations extracted from the Fund model.
    
    This service provides clean separation of concerns for:
    - Capital call and return of capital event creation
    - Unit purchase and sale event creation
    - NAV update event creation and management
    - Event bulk operations and management
    - Event querying and filtering
    """
    
    def __init__(self, 
                 capital_event_repository: 'CapitalEventRepository' = None,
                 unit_event_repository: 'UnitEventRepository' = None,
                 tax_event_repository: 'TaxEventRepository' = None,
                 fund_event_query_repository: 'FundEventQueryRepository' = None):
        """
        Initialize the FundEventService with specialized repositories.
        
        Args:
            capital_event_repository: Repository for capital events
            unit_event_repository: Repository for unit events
            tax_event_repository: Repository for tax events
            fund_event_query_repository: Repository for complex queries
        """
        from src.fund.repositories import CapitalEventRepository, UnitEventRepository, TaxEventRepository, FundEventQueryRepository
        
        self.capital_event_repository = capital_event_repository or CapitalEventRepository()
        self.unit_event_repository = unit_event_repository or UnitEventRepository()
        self.tax_event_repository = tax_event_repository or TaxEventRepository()
        self.fund_event_query_repository = fund_event_query_repository or FundEventQueryRepository()
    
    # ============================================================================
    # CAPITAL CALL AND RETURN OF CAPITAL EVENTS
    # ============================================================================
    
    
    def add_return_of_capital(self, fund: 'Fund', amount: float, date: date,
                             description: Optional[str] = None, reference_number: Optional[str] = None,
                             session: Optional[Session] = None) -> 'FundEvent':
        """
        [EXTRACTED] Add a return of capital event to the fund.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            amount: Amount of capital to return
            date: Date of the return
            description: Optional description
            reference_number: Optional reference number
            session: Database session (optional)
            
        Returns:
            FundEvent: The created return of capital event
        """
        # Validate inputs
        if amount <= 0:
            raise ValueError("Return of capital amount must be positive")
        if not date:
            raise ValueError("Return of capital date is required")
        
        # Prepare event data
        event_data = {
            'fund_id': fund.id,
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_date': date,
            'amount': amount,
            'description': description or f"Return of capital of {amount}",
            'reference_number': reference_number
        }
        
        # Delegate to specialized repository
        event = self.capital_event_repository.create_return_of_capital(fund.id, event_data, session)
        
        logger.info(f"Added return of capital event: {amount} on {date} for fund {fund.name}")
        return event
    
    # ============================================================================
    # UNIT PURCHASE AND SALE EVENTS
    # ============================================================================
    
    def add_unit_purchase(self, fund: 'Fund', units: float, price: float, date: date,
                         brokerage_fee: float = 0.0, description: Optional[str] = None,
                         reference_number: Optional[str] = None, session: Optional[Session] = None) -> 'FundEvent':
        """
        [EXTRACTED] Add a unit purchase event to the fund.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            units: Number of units to purchase
            price: Price per unit
            date: Date of the purchase
            brokerage_fee: Optional brokerage fee
            description: Optional description
            reference_number: Optional reference number
            session: Database session (optional)
            
        Returns:
            FundEvent: The created unit purchase event
        """
        # Validate inputs
        if units <= 0:
            raise ValueError("Units must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")
        if not date:
            raise ValueError("Purchase date is required")
        if brokerage_fee < 0:
            raise ValueError("Brokerage fee cannot be negative")
        
        # Calculate total amount
        total_amount = (units * price) + brokerage_fee
        
        # Prepare event data
        event_data = {
            'fund_id': fund.id,
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date,
            'units_purchased': units,
            'unit_price': price,
            'brokerage_fee': brokerage_fee,
            'amount': total_amount,
            'description': description or f"Purchase of {units} units at {price}",
            'reference_number': reference_number
        }
        
        # Delegate to specialized repository
        event = self.unit_event_repository.create_unit_purchase(fund.id, event_data, session)
        
        logger.info(f"Added unit purchase event: {units} units at {price} on {date} for fund {fund.name}")
        return event
    
    def add_unit_sale(self, fund: 'Fund', units: float, price: float, date: date,
                      brokerage_fee: float = 0.0, description: Optional[str] = None,
                      reference_number: Optional[str] = None, session: Optional[Session] = None) -> 'FundEvent':
        """
        [EXTRACTED] Add a unit sale event to the fund.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            units: Number of units to sell
            price: Price per unit
            date: Date of the sale
            brokerage_fee: Optional brokerage fee
            description: Optional description
            reference_number: Optional reference number
            session: Database session (optional)
            
        Returns:
            FundEvent: The created unit sale event
        """
        # Validate inputs
        if units <= 0:
            raise ValueError("Units must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")
        if not date:
            raise ValueError("Sale date is required")
        if brokerage_fee < 0:
            raise ValueError("Brokerage fee cannot be negative")
        
        # Calculate total amount
        total_amount = (units * price) - brokerage_fee
        
        # Prepare event data
        event_data = {
            'fund_id': fund.id,
            'event_type': EventType.UNIT_SALE,
            'event_date': date,
            'units_sold': units,
            'unit_price': price,
            'brokerage_fee': brokerage_fee,
            'amount': total_amount,
            'description': description or f"Unit sale of {units} units at {price}",
            'reference_number': reference_number
        }
        
        # Delegate to specialized repository
        event = self.unit_event_repository.create_unit_sale(fund.id, event_data, session)
        
        logger.info(f"Added unit sale event: {units} units at {price} on {date} for fund {fund.name}")
        return event
    
    # ============================================================================
    # NAV UPDATE EVENTS
    # ============================================================================
    
    def add_nav_update(self, fund: 'Fund', nav_per_share: float, date: date,
                      description: Optional[str] = None, reference_number: Optional[str] = None,
                      session: Optional[Session] = None) -> 'FundEvent':
        """
        [EXTRACTED] Add a NAV update event to the fund.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            nav_per_share: NAV per share value
            date: Date of the NAV update
            description: Optional description
            reference_number: Optional reference number
            session: Database session (optional)
            
        Returns:
            FundEvent: The created NAV update event
        """
        # Validate inputs
        if nav_per_share < 0:
            raise ValueError("NAV per share cannot be negative")
        if not date:
            raise ValueError("NAV update date is required")
        
        # Prepare event data
        event_data = {
            'fund_id': fund.id,
            'event_type': EventType.NAV_UPDATE,
            'event_date': date,
            'nav_per_share': nav_per_share,
            'description': description or f"NAV update to {nav_per_share}",
            'reference_number': reference_number
        }
        
        # Delegate to specialized repository
        event = self.unit_event_repository.create_nav_update(fund.id, event_data, session)
        
        logger.info(f"Added NAV update event: {nav_per_share} on {date} for fund {fund.name}")
        return event
    
    def _calculate_nav_change_fields(self, fund: 'Fund', nav_per_share: float, date: date, 
                                   session: Optional[Session] = None) -> Dict[str, Any]:
        """
        [EXTRACTED] Calculate NAV change fields for a NAV update event.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            nav_per_share: NAV per share value
            date: Date of the NAV update
            session: Database session (optional)
            
        Returns:
            dict: NAV change field values
        """
        # Use query repository to get the previous NAV event
        if not self.fund_event_query_repository:
            from src.fund.repositories import FundEventQueryRepository
            self.fund_event_query_repository = FundEventQueryRepository()
        
        prev_nav_events = self.fund_event_query_repository.get_events_before_date(
            fund.id, EventType.NAV_UPDATE, date, session
        )
        
        prev_nav_event = prev_nav_events[0] if prev_nav_events else None
        
        if prev_nav_event and prev_nav_event.nav_per_share:
            prev_nav = prev_nav_event.nav_per_share
            nav_change = nav_per_share - prev_nav
            nav_change_percentage = (nav_change / prev_nav) * 100 if prev_nav > 0 else 0
        else:
            nav_change = 0
            nav_change_percentage = 0
        
        return {
            'nav_change': nav_change,
            'nav_change_percentage': nav_change_percentage
        }
    
    def _update_subsequent_nav_change_fields(self, fund: 'Fund', new_nav_event: 'FundEvent', 
                                           session: Optional[Session] = None) -> None:
        """
        [EXTRACTED] Update NAV change fields for subsequent NAV events.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            new_nav_event: The new NAV event
            session: Database session (optional)
        """
        # Use query repository to get subsequent NAV events
        if not self.fund_event_query_repository:
            from src.fund.repositories import FundEventQueryRepository
            self.fund_event_query_repository = FundEventQueryRepository()
        
        subsequent_events = self.fund_event_query_repository.get_events_after_date(
            fund.id, EventType.NAV_UPDATE, new_nav_event.event_date, session
        )
        
        # Update each subsequent event
        for event in subsequent_events:
            if event.nav_per_share:
                nav_fields = self._calculate_nav_change_fields(fund, event.nav_per_share, event.event_date, session)
                event.nav_change = nav_fields['nav_change']
                event.nav_change_percentage = nav_fields['nav_change_percentage']
    
    # ============================================================================
    # EVENT QUERYING AND FILTERING
    # ============================================================================
    
    def get_events(self, fund: 'Fund', event_types: Optional[List[str]] = None,
                   start_date: Optional[date] = None, end_date: Optional[date] = None,
                   session: Optional[Session] = None) -> List['FundEvent']:
        """
        [EXTRACTED] Get fund events with optional filtering.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            event_types: Optional list of event types to filter by
            start_date: Optional start date filter
            end_date: Optional end date filter
            session: Database session (optional)
            
        Returns:
            list: Filtered list of fund events
        """
        # Use repository for data access instead of direct model access
        if event_types:
            # Convert string event types to EventType enums
            from src.fund.enums import EventType
            event_type_enums = [EventType(et) if isinstance(et, str) else et for et in event_types]
            events = self.fund_event_query_repository.get_events_by_fund_and_types(
                fund.id, event_type_enums, session
            )
        else:
            events = self.fund_event_query_repository.get_events_by_fund(fund.id, session)
        
        # Apply date filters if specified
        if start_date:
            events = [e for e in events if e.event_date >= start_date]
        
        if end_date:
            events = [e for e in events if e.event_date <= end_date]
        
        # Sort by date
        events.sort(key=lambda e: e.event_date)
        
        return events
    
    def get_recent_events(self, fund: 'Fund', limit: int = 10, 
                         exclude_system_events: bool = True, session: Optional[Session] = None) -> List['FundEvent']:
        """
        [EXTRACTED] Get recent fund events.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            limit: Maximum number of events to return
            exclude_system_events: Whether to exclude system events
            session: Database session (optional)
            
        Returns:
            list: List of recent fund events
        """
        # Use repository for data access instead of direct model access
        events = self.fund_event_query_repository.get_events_by_fund(fund.id, session)
        
        # Exclude system events if requested
        if exclude_system_events:
            system_event_types = [EventType.DAILY_RISK_FREE_INTEREST_CHARGE, EventType.EOFY_DEBT_COST, EventType.TAX_PAYMENT]
            events = [e for e in events if e.event_type not in system_event_types]
        
        # Sort by date (most recent first) and limit
        events.sort(key=lambda e: e.event_date, reverse=True)
        return events[:limit]
    
    def get_all_fund_events(self, fund: 'Fund', exclude_system_events: bool = True,
                           session: Optional[Session] = None) -> List['FundEvent']:
        """
        [EXTRACTED] Get all fund events.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            exclude_system_events: Whether to exclude system events
            session: Database session (optional)
            
        Returns:
            list: List of all fund events
        """
        # Use repository for data access instead of direct model access
        events = self.fund_event_query_repository.get_events_by_fund(fund.id, session)
        
        # Exclude system events if requested
        if exclude_system_events:
            system_event_types = [EventType.DAILY_RISK_FREE_INTEREST_CHARGE, EventType.EOFY_DEBT_COST, EventType.TAX_PAYMENT]
            events = [e for e in events if e.event_type not in system_event_types]
        
        # Sort by date
        events.sort(key=lambda e: e.event_date)
        return events
    
    # ============================================================================
    # EVENT MANAGEMENT AND BULK OPERATIONS
    # ============================================================================
    
    def delete_event(self, fund: 'Fund', event_id: int, session: Optional[Session] = None) -> bool:
        """
        [EXTRACTED] Delete a fund event.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            event_id: ID of the event to delete
            session: Database session (optional)
            
        Returns:
            bool: True if event was deleted, False otherwise
        """
        from src.fund.repositories import FundEventRepository
        
        # Use repository to delete the event
        event_repository = FundEventRepository()
        success = event_repository.delete(event_id, session)
        
        if success:
            logger.info(f"Deleted event {event_id} from fund {fund.name}")
        
        return success
    
    def bulk_add_events(self, fund: 'Fund', events_data: List[Dict[str, Any]], 
                       session: Optional[Session] = None) -> List['FundEvent']:
        """
        [EXTRACTED] Add multiple events to the fund in bulk.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            events_data: List of event data dictionaries
            session: Database session (optional)
            
        Returns:
            list: List of created fund events
        """
        created_events = []
        
        for event_data in events_data:
            # Add fund_id to event data
            event_data['fund_id'] = fund.id
            
            # Determine which repository to use based on event type
            event_type = event_data.get('event_type')
            if isinstance(event_type, str):
                event_type = EventType(event_type)
            
            if event_type == EventType.CAPITAL_CALL:
                event = self.capital_event_repository.create_capital_call(fund.id, event_data, session)
            elif event_type == EventType.RETURN_OF_CAPITAL:
                event = self.capital_event_repository.create_return_of_capital(fund.id, event_data, session)
            elif event_type == EventType.UNIT_PURCHASE:
                event = self.unit_event_repository.create_unit_purchase(fund.id, event_data, session)
            elif event_type == EventType.UNIT_SALE:
                event = self.unit_event_repository.create_unit_sale(fund.id, event_data, session)
            elif event_type == EventType.NAV_UPDATE:
                event = self.unit_event_repository.create_nav_update(fund.id, event_data, session)
            elif event_type == EventType.TAX_PAYMENT:
                event = self.tax_event_repository.create_tax_payment(fund.id, event_data, session)
            elif event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE:
                event = self.tax_event_repository.create_daily_interest_charge(fund.id, event_data, session)
            elif event_type == EventType.EOFY_DEBT_COST:
                event = self.tax_event_repository.create_eofy_debt_cost(fund.id, event_data, session)
            else:
                # Fallback to generic creation (for other event types)
                from src.fund.repositories import FundEventRepository
                fund_event_repository = FundEventRepository()
                event = fund_event_repository.create(event_data, session)
            
            created_events.append(event)
        
        logger.info(f"Added {len(created_events)} events to fund {fund.name}")
        return created_events
    
    def _create_bulk_event_object(self, fund: 'Fund', event_data: Dict[str, Any]) -> 'FundEvent':
        """
        [EXTRACTED] Create a fund event object from bulk event data.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            event_data: Event data dictionary
            
        Returns:
            FundEvent: The created fund event object
        """
        # Extract required fields
        event_type = event_data.get('event_type')
        event_date = event_data.get('event_date')
        amount = event_data.get('amount')
        
        # Validate required fields
        if not event_type:
            raise ValueError("event_type is required")
        if not event_date:
            raise ValueError("event_date is required")
        
        # Create the event
        event = fund.fund_events.__class__(
            fund_id=fund.id,
            event_type=event_type if isinstance(event_type, EventType) else EventType(event_type),
            event_date=event_date,
            amount=amount,
            description=event_data.get('description'),
            reference_number=event_data.get('reference_number')
        )
        
        # Set optional fields based on event type
        if event_type == EventType.UNIT_PURCHASE:
            event.units_purchased = event_data.get('units_purchased')
            event.unit_price = event_data.get('unit_price')
            event.brokerage_fee = event_data.get('brokerage_fee', 0.0)
        elif event_type == EventType.UNIT_SALE:
            event.units_sold = event_data.get('units_sold')
            event.unit_price = event_data.get('unit_price')
            event.brokerage_fee = event_data.get('brokerage_fee', 0.0)
        elif event_type == EventType.NAV_UPDATE:
            event.nav_per_share = event_data.get('nav_per_share')
        elif event_type == EventType.DISTRIBUTION:
            event.distribution_type = event_data.get('distribution_type')
            event.tax_withheld = event_data.get('tax_withheld', 0.0)
        
        return event
