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

from src.fund.enums import EventType, DistributionType
from typing import TYPE_CHECKING

# Configure logger for this module
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.fund.models import Fund, FundEvent
    from src.fund.repositories import CapitalEventRepository, UnitEventRepository, TaxEventRepository, FundEventQueryRepository, DistributionEventRepository
    from src.fund.services import FundValidationService
    from src.fund.calculators.withholding_tax_calculator import WithholdingTaxCalculator


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
                 distribution_event_repository: 'DistributionEventRepository' = None,
                 fund_event_query_repository: 'FundEventQueryRepository' = None,
                 validation_service: 'FundValidationService' = None):
        """
        Initialize the FundEventService with specialized repositories.
        
        Args:
            capital_event_repository: Repository for capital events
            unit_event_repository: Repository for unit events
            tax_event_repository: Repository for tax events
            distribution_event_repository: Repository for distribution events
            fund_event_query_repository: Repository for complex queries
            validation_service: Service for validation logic
        """
        from src.fund.repositories import CapitalEventRepository, UnitEventRepository, TaxEventRepository, DistributionEventRepository, FundEventQueryRepository
        from src.fund.services.fund_validation_service import FundValidationService
        
        self.capital_event_repository = capital_event_repository or CapitalEventRepository()
        self.unit_event_repository = unit_event_repository or UnitEventRepository()
        self.tax_event_repository = tax_event_repository or TaxEventRepository()
        self.distribution_event_repository = distribution_event_repository or DistributionEventRepository()
        self.fund_event_query_repository = fund_event_query_repository or FundEventQueryRepository()
        self.validation_service = validation_service or FundValidationService()
    
    # ============================================================================
    # CAPITAL CALL AND RETURN OF CAPITAL EVENTS
    # ============================================================================
    
    def add_capital_call(self, fund: 'Fund', amount: float, call_date: date, 
                        description: str = None, reference_number: str = None, 
                        session: Session = None) -> 'FundEvent':
        """
        Add capital call event - THE ONLY method for this operation.
        
        This method follows enterprise best practices:
        1. Business validation
        2. Create the event directly
        3. Delegate secondary impacts to orchestrator
        
        Args:
            fund: The fund object
            amount: Capital call amount
            call_date: Date of the capital call
            description: Description of the capital call
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created capital call event
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If fund not found
        """
        from src.fund.enums import EventType
        from src.fund.events.orchestrator import FundUpdateOrchestrator
        
        # 1. Business validation using validation service
        validation_errors = self.validation_service.validate_capital_call(
            fund, amount, call_date, reference_number, session
        )
        if validation_errors:
            # Convert validation errors to ValueError with first error message
            first_error_field = next(iter(validation_errors))
            first_error_message = validation_errors[first_error_field][0]
            raise ValueError(first_error_message)
        
        # 2. Create the capital call event directly (business logic)
        event = self.capital_event_repository.create_capital_call(fund.id, {
            'fund_id': fund.id,
            'event_type': EventType.CAPITAL_CALL,
            'amount': amount,
            'event_date': call_date,
            'description': description or f"Capital call: ${amount:,.2f}",
            'reference_number': reference_number
        }, session)
        
        # 3. Delegate secondary impacts to orchestrator (side effects)
        orchestrator = FundUpdateOrchestrator()
        event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_id': event.id,
            'fund_id': fund.id,
            'amount': amount,
            'event_date': call_date
        }
        logger.info(f"About to call orchestrator with event_data: {event_data}")
        orchestrator.process_fund_event(event_data, session, fund)
        logger.info("Orchestrator call completed")
        
        logger.info(f"Added capital call event: ${amount:,.2f} on {call_date} for fund {fund.name}")
        return event
    
    def add_return_of_capital(self, fund: 'Fund', amount: float, return_date: date,
                             description: str = None, reference_number: str = None,
                             session: Session = None) -> 'FundEvent':
        """
        Add return of capital event - THE ONLY method for this operation.
        
        This method follows enterprise best practices:
        1. Business validation
        2. Create the event directly
        3. Delegate secondary impacts to orchestrator
        
        Args:
            fund: The fund object
            amount: Return amount
            return_date: Date of the return
            description: Description of the return
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created return of capital event
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If fund not found
        """
        from src.fund.enums import EventType
        from src.fund.events.orchestrator import FundUpdateOrchestrator
        
        # 1. Business validation using validation service
        validation_errors = self.validation_service.validate_return_of_capital(
            fund, amount, return_date, reference_number, session
        )
        if validation_errors:
            # Convert validation errors to ValueError with first error message
            first_error_field = next(iter(validation_errors))
            first_error_message = validation_errors[first_error_field][0]
            raise ValueError(first_error_message)
        
        # 2. Create the return of capital event directly
        event = self.capital_event_repository.create_return_of_capital(fund.id, {
            'fund_id': fund.id,
            'event_type': EventType.RETURN_OF_CAPITAL,
            'amount': amount,
            'event_date': return_date,
            'description': description or f"Return of capital: ${amount:,.2f}",
            'reference_number': reference_number
        }, session)
        
        # 4. Delegate secondary impacts to orchestrator
        orchestrator = FundUpdateOrchestrator()
        event_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'event_id': event.id,
            'fund_id': fund.id,
            'amount': amount,
            'event_date': return_date
        }
        orchestrator.process_fund_event(event_data, session, fund)
        
        logger.info(f"Added return of capital event: ${amount:,.2f} on {return_date} for fund {fund.name}")
        return event
    
    # ============================================================================
    # UNIT PURCHASE AND SALE EVENTS
    # ============================================================================
    
    def add_unit_purchase(self, fund: 'Fund', units: float, price: float, date: date,
                         brokerage_fee: float = 0.0, description: Optional[str] = None,
                         reference_number: Optional[str] = None, session: Optional[Session] = None) -> 'FundEvent':
        """
        Add unit purchase event - THE ONLY method for this operation.
        
        This method follows enterprise best practices:
        1. Business validation
        2. Create the event directly
        3. Delegate secondary impacts to orchestrator
        
        Args:
            fund: The fund object
            units: Number of units to purchase
            price: Price per unit
            date: Date of the purchase
            brokerage_fee: Optional brokerage fee
            description: Optional description
            reference_number: Optional reference number
            session: Database session
            
        Returns:
            FundEvent: The created unit purchase event
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If fund not found
        """
        from src.fund.enums import EventType
        from src.fund.events.orchestrator import FundUpdateOrchestrator
        
        # 1. Business validation using validation service
        validation_errors = self.validation_service.validate_unit_purchase(
            fund, units, price, date, reference_number, session
        )
        if validation_errors:
            # Convert validation errors to ValueError with first error message
            first_error_field = next(iter(validation_errors))
            first_error_message = validation_errors[first_error_field][0]
            raise ValueError(first_error_message)
        
        # 2. Create the unit purchase event directly (business logic)
        total_amount = (units * price) + brokerage_fee
        event = self.unit_event_repository.create_unit_purchase(fund.id, {
            'fund_id': fund.id,
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date,
            'units_purchased': units,
            'unit_price': price,
            'brokerage_fee': brokerage_fee,
            'amount': total_amount,
            'description': description or f"Purchase of {units} units at {price}",
            'reference_number': reference_number
        }, session)
        
        # 3. Delegate secondary impacts to orchestrator (side effects)
        orchestrator = FundUpdateOrchestrator()
        event_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_id': event.id,
            'fund_id': fund.id,
            'units_purchased': units,
            'unit_price': price,
            'event_date': date
        }
        logger.info(f"About to call orchestrator with event_data: {event_data}")
        orchestrator.process_fund_event(event_data, session, fund)
        logger.info("Orchestrator call completed")
        
        logger.info(f"Added unit purchase event: {units} units at {price} on {date} for fund {fund.name}")
        return event
    
    def add_unit_sale(self, fund: 'Fund', units: float, price: float, date: date,
                      brokerage_fee: float = 0.0, description: Optional[str] = None,
                      reference_number: Optional[str] = None, session: Optional[Session] = None) -> 'FundEvent':
        """
        Add unit sale event - THE ONLY method for this operation.
        
        This method follows enterprise best practices:
        1. Business validation
        2. Create the event directly
        3. Delegate secondary impacts to orchestrator
        
        Args:
            fund: The fund object
            units: Number of units to sell
            price: Price per unit
            date: Date of the sale
            brokerage_fee: Optional brokerage fee
            description: Optional description
            reference_number: Optional reference number
            session: Database session
            
        Returns:
            FundEvent: The created unit sale event
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If fund not found
        """
        from src.fund.enums import EventType
        from src.fund.events.orchestrator import FundUpdateOrchestrator
        
        # 1. Business validation using validation service
        validation_errors = self.validation_service.validate_unit_sale(
            fund, units, price, date, reference_number, session
        )
        if validation_errors:
            # Convert validation errors to ValueError with first error message
            first_error_field = next(iter(validation_errors))
            first_error_message = validation_errors[first_error_field][0]
            raise ValueError(first_error_message)
        
        # 2. Create the unit sale event directly (business logic)
        total_amount = (units * price) - brokerage_fee
        event = self.unit_event_repository.create_unit_sale(fund.id, {
            'fund_id': fund.id,
            'event_type': EventType.UNIT_SALE,
            'event_date': date,
            'units_sold': units,
            'unit_price': price,
            'brokerage_fee': brokerage_fee,
            'amount': total_amount,
            'description': description or f"Unit sale of {units} units at {price}",
            'reference_number': reference_number
        }, session)
        
        # 3. Delegate secondary impacts to orchestrator (side effects)
        orchestrator = FundUpdateOrchestrator()
        event_data = {
            'event_type': EventType.UNIT_SALE,
            'event_id': event.id,
            'fund_id': fund.id,
            'units_sold': units,
            'unit_price': price,
            'event_date': date
        }
        logger.info(f"About to call orchestrator with event_data: {event_data}")
        orchestrator.process_fund_event(event_data, session, fund)
        logger.info("Orchestrator call completed")
        
        logger.info(f"Added unit sale event: {units} units at {price} on {date} for fund {fund.name}")
        return event
    
    # ============================================================================
    # NAV UPDATE EVENTS
    # ============================================================================
    
    def add_nav_update(self, fund: 'Fund', nav_per_share: float, date: date,
                      description: Optional[str] = None, reference_number: Optional[str] = None,
                      session: Optional[Session] = None) -> 'FundEvent':
        """
        Add NAV update event - THE ONLY method for this operation.
        
        This method follows enterprise best practices:
        1. Business validation
        2. Create the event directly
        3. Delegate secondary impacts to orchestrator
        
        Args:
            fund: The fund object
            nav_per_share: NAV per share value
            date: Date of the NAV update
            description: Optional description
            reference_number: Optional reference number
            session: Database session
            
        Returns:
            FundEvent: The created NAV update event
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If fund not found
        """
        from src.fund.enums import EventType
        from src.fund.events.orchestrator import FundUpdateOrchestrator
        
        # 1. Business validation using validation service (includes duplicate checking)
        validation_errors = self.validation_service.validate_nav_update(
            fund, nav_per_share, date, reference_number, session
        )
        if validation_errors:
            # Convert validation errors to ValueError with first error message
            first_error_field = next(iter(validation_errors))
            first_error_message = validation_errors[first_error_field][0]
            raise ValueError(first_error_message)
        
        # 2. Calculate NAV change fields (business logic)
        previous_nav, nav_change_absolute, nav_change_percentage = self._calculate_nav_change_fields(
            fund, nav_per_share, date, session
        )
        
        # 3. Create the NAV update event directly (business logic)
        event = self.unit_event_repository.create_nav_update(fund.id, {
            'fund_id': fund.id,
            'event_type': EventType.NAV_UPDATE,
            'event_date': date,
            'nav_per_share': nav_per_share,
            'previous_nav_per_share': previous_nav,
            'nav_change_absolute': nav_change_absolute,
            'nav_change_percentage': nav_change_percentage,
            'description': description or f"NAV update to {nav_per_share}",
            'reference_number': reference_number
        }, session)
        
        # 4. Delegate secondary impacts to orchestrator (side effects)
        orchestrator = FundUpdateOrchestrator()
        event_data = {
            'event_type': EventType.NAV_UPDATE,
            'event_id': event.id,
            'fund_id': fund.id,
            'nav_per_share': nav_per_share,
            'event_date': date
        }
        logger.info(f"About to call orchestrator with event_data: {event_data}")
        orchestrator.process_fund_event(event_data, session, fund)
        logger.info("Orchestrator call completed")
        
        logger.info(f"Added NAV update event: {nav_per_share} on {date} for fund {fund.name}")
        return event
    
    def _calculate_nav_change_fields(self, fund: 'Fund', nav_per_share: float, date: date, 
                                   session: Optional[Session] = None) -> tuple[Optional[float], Optional[float], Optional[float]]:
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
            nav_change_absolute = nav_per_share - prev_nav
            nav_change_percentage = (nav_change_absolute / prev_nav) * 100 if prev_nav > 0 else 0
        else:
            prev_nav = None
            nav_change_absolute = None
            nav_change_percentage = None
        
        return prev_nav, nav_change_absolute, nav_change_percentage
    
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
    # DISTRIBUTION EVENTS
    # ============================================================================

    def add_distribution(self, fund: 'Fund', event_date: date, distribution_type: 'DistributionType',
                        distribution_amount: float = None, has_withholding_tax: bool = False,
                        gross_interest_amount: float = None, net_interest_amount: float = None,
                        withholding_tax_amount: float = None, withholding_tax_rate: float = None,
                        description: str = None, reference_number: str = None,
                        session: Optional[Session] = None) -> 'FundEvent':
        """
        Add distribution event - THE ONLY method for this operation.
        
        This method follows enterprise best practices:
        1. Business validation
        2. Create the event directly
        3. Delegate secondary impacts to orchestrator
        
        Args:
            fund: The fund object
            event_date: Distribution date
            distribution_type: Type of distribution
            distribution_amount: Simple distribution amount (when has_withholding_tax=False)
            has_withholding_tax: Whether this distribution has withholding tax
            gross_interest_amount: Gross interest amount (when has_withholding_tax=True)
            net_interest_amount: Net interest amount (when has_withholding_tax=True)
            withholding_tax_amount: Tax amount withheld (when has_withholding_tax=True)
            withholding_tax_rate: Tax rate percentage (when has_withholding_tax=True)
            description: Event description
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created distribution event
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If fund not found
        """
        from src.fund.enums import EventType
        from src.fund.events.orchestrator import FundUpdateOrchestrator
        
        # 1. Business validation using validation service
        validation_errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, distribution_amount, has_withholding_tax,
            gross_interest_amount, net_interest_amount, withholding_tax_amount, 
            withholding_tax_rate, reference_number, session
        )
        if validation_errors:
            # Convert validation errors to ValueError with first error message
            first_error_field = next(iter(validation_errors))
            first_error_message = validation_errors[first_error_field][0]
            raise ValueError(first_error_message)
        
        # 2. Calculate distribution amounts and create event data
        event_data = self._calculate_distribution_event_data(
            fund, event_date, distribution_type, distribution_amount, has_withholding_tax,
            gross_interest_amount, net_interest_amount, withholding_tax_amount, 
            withholding_tax_rate, description, reference_number
        )
        
        # 3. Create the distribution event directly (business logic)
        # This handles tax event creation and grouping internally
        distribution_event = self.distribution_event_repository.create_distribution(fund.id, event_data, session)
        
        # 4. Delegate secondary impacts to orchestrator (side effects)
        orchestrator = FundUpdateOrchestrator()
        orchestrator_event_data = {
            'event_type': EventType.DISTRIBUTION,
            'event_id': distribution_event.id,
            'fund_id': fund.id,
            'event_date': event_date,
            'distribution_type': distribution_type
        }
        orchestrator.process_fund_event(orchestrator_event_data, session, fund)
        
        return distribution_event

    def _calculate_distribution_event_data(self, fund: 'Fund', event_date: date, distribution_type: 'DistributionType',
                                         distribution_amount: float = None, has_withholding_tax: bool = False,
                                         gross_interest_amount: float = None, net_interest_amount: float = None,
                                         withholding_tax_amount: float = None, withholding_tax_rate: float = None,
                                         description: str = None, reference_number: str = None) -> Dict[str, Any]:
        """
        Calculate distribution event data based on parameters.
        
        This method handles the complex logic for both simple distributions
        and withholding tax distributions.
        """
        from src.fund.enums import EventType
        
        event_data = {
            'fund_id': fund.id,
            'event_type': EventType.DISTRIBUTION,
            'event_date': event_date,
            'distribution_type': distribution_type.value if hasattr(distribution_type, 'value') else str(distribution_type),
            'description': description or f"Distribution: {distribution_type}",
            'reference_number': reference_number
        }
        
        if has_withholding_tax:
            # Complex withholding tax distribution
            from src.fund.calculators.withholding_tax_calculator import WithholdingTaxCalculator
            gross_amount, net_amount, tax_amount = WithholdingTaxCalculator.calculate_withholding_tax_amounts(
                gross_interest_amount, net_interest_amount, withholding_tax_amount, withholding_tax_rate
            )
            
            event_data.update({
                'amount': gross_amount,  # Store gross amount for IRR calculations
                'tax_withholding': tax_amount,  # Tax amount withheld
                'has_withholding_tax': True
            })
        else:
            # Simple distribution
            if not distribution_amount:
                raise ValueError("distribution_amount is required for simple distributions")
            
            event_data.update({
                'amount': distribution_amount,
                'tax_withholding': 0.0,  # Use correct field name from FundEvent model
                'has_withholding_tax': False
            })
        
        return event_data
    
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
    