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
from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from src.fund.enums import EventType, DistributionType, FundEventOperation
from src.fund.repositories import DomainEventRepository
from typing import TYPE_CHECKING

# Configure logger for this module
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.fund.models import Fund, FundEvent
    from src.fund.repositories import CapitalEventRepository, UnitEventRepository, TaxEventRepository, FundEventQueryRepository, DistributionEventRepository
    from src.fund.services import FundValidationService


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
                 validation_service: 'FundValidationService' = None,
                 fund_event_secondary_service: 'FundEventSecondaryService' = None):
        """
        Initialize the FundEventService with specialized repositories.
        
        Args:
            capital_event_repository: Repository for capital events
            unit_event_repository: Repository for unit events
            tax_event_repository: Repository for tax events
            distribution_event_repository: Repository for distribution events
            fund_event_query_repository: Repository for complex queries
            validation_service: Service for validation logic
            fund_event_secondary_service: Service for handling secondary impacts
        """
        from src.fund.repositories import CapitalEventRepository, UnitEventRepository, TaxEventRepository, DistributionEventRepository, FundEventQueryRepository, DomainEventRepository
        from src.fund.services.fund_validation_service import FundValidationService
        from src.fund.services.fund_event_secondary_service import FundEventSecondaryService
        self.capital_event_repository = capital_event_repository or CapitalEventRepository()
        self.unit_event_repository = unit_event_repository or UnitEventRepository()
        self.tax_event_repository = tax_event_repository or TaxEventRepository()
        self.distribution_event_repository = distribution_event_repository or DistributionEventRepository()
        self.fund_event_query_repository = fund_event_query_repository or FundEventQueryRepository()
        self.validation_service = validation_service or FundValidationService()
        self.fund_event_secondary_service = fund_event_secondary_service or FundEventSecondaryService()
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

        # 3. Handle the secondary impacts
        all_changes = self.fund_event_secondary_service.handle_event_secondary_impact(fund=fund, event_id=event.id, 
                            fund_event_type=EventType.CAPITAL_CALL, fund_event_operation=FundEventOperation.EVENT_CREATED, session=session)

        # 4. Store the domain fund event containing the changes
        if all_changes:
            domain_event_repository = DomainEventRepository(session)
            domain_event = domain_event_repository.store_domain_fund_event(
                fund_id=fund.id,
                event_type=EventType.CAPITAL_CALL,
                event_operation=FundEventOperation.EVENT_CREATED,
                event_id=event.id,
                event_data={"changes": [change.to_dict() for change in all_changes]},
                session=session
            )
        
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
        
         # 3. Handle the secondary impacts
        all_changes = self.fund_event_secondary_service.handle_event_secondary_impact(fund=fund, event_id=event.id, 
                            fund_event_type=EventType.RETURN_OF_CAPITAL, fund_event_operation=FundEventOperation.EVENT_CREATED, session=session)

        # 4. Store the domain fund event containing the changes
        if all_changes:
            domain_event_repository = DomainEventRepository(session)
            domain_event = domain_event_repository.store_domain_fund_event(
                fund_id=fund.id,
                event_type=EventType.RETURN_OF_CAPITAL,
                event_operation=FundEventOperation.EVENT_CREATED,
                event_id=event.id,
                event_data={"changes": [change.to_dict() for change in all_changes]},
                session=session
            )
        
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
        
        # 3. Handle the secondary impacts
        all_changes = self.fund_event_secondary_service.handle_event_secondary_impact(fund=fund, event_id=event.id, 
                            fund_event_type=EventType.UNIT_PURCHASE, fund_event_operation=FundEventOperation.EVENT_CREATED, session=session)    

        # 4. Store the domain fund event containing the changes
        if all_changes:
            domain_event_repository = DomainEventRepository(session)
            domain_event = domain_event_repository.store_domain_fund_event(
                fund_id=fund.id,
                event_type=EventType.UNIT_PURCHASE,
                event_operation=FundEventOperation.EVENT_CREATED,
                event_id=event.id,
                event_data={"changes": [change.to_dict() for change in all_changes]},
                session=session
            )

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
        
        # 3. Handle the secondary impacts
        all_changes = self.fund_event_secondary_service.handle_event_secondary_impact(fund=fund, event_id=event.id, 
                            fund_event_type=EventType.UNIT_SALE, fund_event_operation=FundEventOperation.EVENT_CREATED, session=session)    

        # 4. Store the domain fund event containing the changes
        if all_changes:
            domain_event_repository = DomainEventRepository(session)
            domain_event = domain_event_repository.store_domain_fund_event(
                fund_id=fund.id,
                event_type=EventType.UNIT_SALE,
                event_operation=FundEventOperation.EVENT_CREATED,
                event_id=event.id,
                event_data={"changes": [change.to_dict() for change in all_changes]},
                session=session
            )

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
        # 1. Business validation using validation service (includes duplicate checking)
        validation_errors = self.validation_service.validate_nav_update(
            fund, nav_per_share, date, reference_number, session
        )
        if validation_errors:
            # Convert validation errors to ValueError with first error message
            first_error_field = next(iter(validation_errors))
            first_error_message = validation_errors[first_error_field][0]
            raise ValueError(first_error_message)
        
        # 2. Create the NAV update event directly (business logic)
        event = self.unit_event_repository.create_nav_update(fund.id, {
            'fund_id': fund.id,
            'event_type': EventType.NAV_UPDATE,
            'event_date': date,
            'nav_per_share': nav_per_share,
            'previous_nav_per_share': None,
            'nav_change_absolute': None,
            'nav_change_percentage': None,
            'description': description or f"NAV update to {nav_per_share}",
            'reference_number': reference_number
        }, session)

        # 3. Handle the secondary impacts
        all_changes = self.fund_event_secondary_service.handle_event_secondary_impact(fund=fund, event_id=event.id, 
                            fund_event_type=EventType.NAV_UPDATE, fund_event_operation=FundEventOperation.EVENT_CREATED, session=session)    

        # 4. Store the domain fund event containing the changes
        if all_changes:
            domain_event_repository = DomainEventRepository(session)
            domain_event = domain_event_repository.store_domain_fund_event(
                fund_id=fund.id,
                event_type=EventType.NAV_UPDATE,
                event_operation=FundEventOperation.EVENT_CREATED,
                event_id=event.id,
                event_data={"changes": [change.to_dict() for change in all_changes]},
                session=session
            )

        return event

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
        
        # 4. Handle the secondary impacts
        all_changes = self.fund_event_secondary_service.handle_event_secondary_impact(fund=fund, event_id=distribution_event.id, 
                            fund_event_type=EventType.DISTRIBUTION, fund_event_operation=FundEventOperation.EVENT_CREATED, session=session)    
        
        # 5. Store the domain fund event containing the changes
        if all_changes:
            domain_event_repository = DomainEventRepository(session)
            domain_event = domain_event_repository.store_domain_fund_event(
                fund_id=fund.id,
                event_type=EventType.DISTRIBUTION,
                event_operation=FundEventOperation.EVENT_CREATED,
                event_id=distribution_event.id,
                event_data={"changes": [change.to_dict() for change in all_changes]},
                session=session
            )

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
    
    def delete_fund_event(self, fund_id: int, event_id: int, session: Session) -> bool:
        """
        Delete a fund event and handle secondary operations.
        
        This method follows enterprise best practices:
        1. Business operation: Delete the event directly
        2. Delegate secondary impacts to orchestrator
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event to delete
            session: Database session
            
        Returns:
            True if event was deleted, False if not found
        """
        # 1. Business operation: Delete the event
        from src.fund.repositories import FundEventRepository, FundRepository
        
        fund_repository = FundRepository()
        fund = fund_repository.get_by_id(fund_id, session)
        if not fund:
            raise ValueError(f"Fund with id {fund_id} not found")

        fund_event_repository = FundEventRepository()
        event = fund_event_repository.get_by_id(event_id, session)
        if not event:
            raise ValueError(f"Event with id {event_id} not found")

        event_type = event.event_type

        success = fund_event_repository.delete(event_id, session)
        
        if success:
            # 2. Process the secondary operations
            all_changes = self.fund_event_secondary_service.handle_event_secondary_impact(fund=fund, event_id=event.id, 
                            fund_event_type=event_type, fund_event_operation=FundEventOperation.EVENT_DELETED, session=session)
            if all_changes:
                domain_event_repository = DomainEventRepository(session)
                domain_event = domain_event_repository.store_domain_fund_event(
                    fund_id=fund_id,
                    event_type=event_type,
                    event_operation=FundEventOperation.EVENT_DELETED,
                    event_id=event.id,
                    event_data={"changes": [change.to_dict() for change in all_changes]},
                    session=session
                )

        return success