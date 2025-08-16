"""
Fund Manager.

This module provides a comprehensive interface for all fund operations using
the event-driven architecture. It maintains backward compatibility while
enabling the new system and provides a clean, service-oriented API.
"""

from typing import Dict, Any, Optional, Union, List
from datetime import date
from sqlalchemy.orm import Session

from src.fund.models import Fund, FundEvent
from src.fund.events.orchestrator import FundUpdateOrchestrator
from src.fund.enums import EventType, DistributionType, FundType, FundStatus
from src.fund.services.fund_calculation_service import FundCalculationService
from src.fund.services.fund_status_service import FundStatusService
from src.fund.services.tax_calculation_service import TaxCalculationService
from src.fund.services.fund_event_service import FundEventService


class FundManager:
    """
    Fund manager that uses the event-driven architecture.
    
    This class provides a clean, service-oriented API for all fund operations
    while maintaining backward compatibility and enabling the new system.
    """
    
    def __init__(self, fund: Fund):
        """
        Initialize the new fund manager.
        
        Args:
            fund: Original Fund model instance to wrap
        """
        self.fund = fund
        self.orchestrator = FundUpdateOrchestrator()
        
        # Initialize services for backward compatibility
        self._calculation_service = None
        self._status_service = None
        self._tax_service = None
        self._event_service = None
    
    # ============================================================================
    # NEW ARCHITECTURE METHODS - Route to orchestrator
    # ============================================================================
    
    def add_capital_call(self, amount: float, date: date, description: Optional[str] = None, 
                        reference_number: Optional[str] = None, session: Optional[Session] = None) -> FundEvent:
        """
        Add a capital call event using the new event-driven architecture.
        
        Args:
            amount: Capital call amount (must be positive)
            date: Date of the capital call
            description: Description of the capital call
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created capital call event
            
        Raises:
            ValueError: If fund is not cost-based or amount is invalid
        """
        if self.fund.tracking_type != FundType.COST_BASED:
            raise ValueError("Capital calls are only applicable for cost-based funds")
        
        if not amount or amount <= 0:
            raise ValueError("Capital call amount must be a positive number")
        if not date:
            raise ValueError("Date is required")
        
        # Check for existing duplicate event (idempotent behavior)
        existing_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund.id,
            FundEvent.event_type == EventType.CAPITAL_CALL,
            FundEvent.event_date == date,
            FundEvent.amount == amount,
            FundEvent.reference_number == reference_number
        ).first()
        
        if existing_event:
            return existing_event
        
        # Route to new architecture
        event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': amount,
            'date': date,
            'description': description or f"Capital call: ${amount:,.2f}",
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, self.fund)
    
    def add_return_of_capital(self, amount: float, date: date, description: Optional[str] = None,
                             reference_number: Optional[str] = None, session: Optional[Session] = None) -> FundEvent:
        """
        Add a return of capital event using the new event-driven architecture.
        
        Args:
            amount: Return amount (must be positive)
            date: Date of the return
            description: Description of the return
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created return of capital event
        """
        if self.fund.tracking_type != FundType.COST_BASED:
            raise ValueError("Returns of capital are only applicable for cost-based funds")
        
        if not amount or amount <= 0:
            raise ValueError("Return amount must be a positive number")
        if not date:
            raise ValueError("Date is required")
        
        # Route to new architecture
        event_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'amount': amount,
            'date': date,
            'description': description or f"Return of capital: ${amount:,.2f}",
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, self.fund)
    
    def add_distribution(self, event_date: date, distribution_type: DistributionType,
                        distribution_amount: Optional[float] = None, has_withholding_tax: bool = False,
                        gross_interest_amount: Optional[float] = None, net_interest_amount: Optional[float] = None,
                        withholding_tax_amount: Optional[float] = None, withholding_tax_rate: Optional[float] = None,
                        description: Optional[str] = None, reference_number: Optional[str] = None,
                        session: Optional[Session] = None) -> Union[FundEvent, tuple[FundEvent, Optional[FundEvent]]]:
        """
        Add a distribution event using the new event-driven architecture.
        
        Args:
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
            FundEvent or tuple: Distribution event, or (distribution_event, tax_event) for withholding tax
        """
        # Route to new architecture
        event_data = {
            'event_type': EventType.DISTRIBUTION,
            'event_date': event_date,
            'distribution_type': distribution_type,
            'distribution_amount': distribution_amount,
            'has_withholding_tax': has_withholding_tax,
            'gross_interest_amount': gross_interest_amount,
            'net_interest_amount': net_interest_amount,
            'withholding_tax_amount': withholding_tax_amount,
            'withholding_tax_rate': withholding_tax_rate,
            'description': description,
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, self.fund)
    
    def add_nav_update(self, nav_per_share: float, date: date, description: Optional[str] = None,
                       reference_number: Optional[str] = None, session: Optional[Session] = None) -> FundEvent:
        """
        Add an NAV update event using the new event-driven architecture.
        
        Args:
            nav_per_share: NAV per share value
            date: Date of the NAV update
            description: Description of the update
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created NAV update event
        """
        if not nav_per_share or nav_per_share <= 0:
            raise ValueError("NAV per share must be a positive number")
        if not date:
            raise ValueError("Date is required")
        
        # Route to new architecture
        event_data = {
            'event_type': EventType.NAV_UPDATE,
            'nav_per_share': nav_per_share,
            'date': date,
            'description': description or f"NAV update: ${nav_per_share:.4f}",
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, self.fund)
    
    def add_unit_purchase(self, units: float, price: float, date: date, brokerage_fee: float = 0.0,
                          description: Optional[str] = None, reference_number: Optional[str] = None,
                          session: Optional[Session] = None) -> FundEvent:
        """
        Add a unit purchase event using the new event-driven architecture.
        
        Args:
            units: Number of units purchased
            price: Price per unit
            date: Date of the purchase
            brokerage_fee: Brokerage fee amount
            description: Description of the purchase
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created unit purchase event
        """
        if not units or units <= 0:
            raise ValueError("Units must be a positive number")
        if not price or price <= 0:
            raise ValueError("Price must be a positive number")
        if not date:
            raise ValueError("Date is required")
        
        # Route to new architecture
        event_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'units': units,
            'price': price,
            'date': date,
            'brokerage_fee': brokerage_fee,
            'description': description or f"Unit purchase: {units:.4f} units at ${price:.4f}",
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, self.fund)
    
    def add_unit_sale(self, units: float, price: float, date: date, brokerage_fee: float = 0.0,
                       description: Optional[str] = None, reference_number: Optional[str] = None,
                       session: Optional[Session] = None) -> FundEvent:
        """
        Add a unit sale event using the new event-driven architecture.
        
        Args:
            units: Number of units sold
            price: Price per unit
            date: Date of the sale
            brokerage_fee: Brokerage fee amount
            description: Description of the sale
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created unit sale event
        """
        if not units or units <= 0:
            raise ValueError("Units must be a positive number")
        if not price or price <= 0:
            raise ValueError("Price must be a positive number")
        if not date:
            raise ValueError("Date is required")
        
        # Route to new architecture
        event_data = {
            'event_type': EventType.UNIT_SALE,
            'units': units,
            'price': price,
            'date': date,
            'brokerage_fee': brokerage_fee,
            'description': description or f"Unit sale: {units:.4f} units at ${price:.4f}",
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, self.fund)
    
    # ============================================================================
    # CALCULATION METHODS - Route to calculation service
    # ============================================================================
    
    def calculate_irr(self, session: Optional[Session] = None) -> Optional[float]:
        """Calculate gross IRR for the fund."""
        return self.orchestrator.calculation_service.calculate_irr(
            fund=self.fund, session=session
        )
    
    def calculate_after_tax_irr(self, session: Optional[Session] = None) -> Optional[float]:
        """Calculate after-tax IRR for the fund."""
        return self.orchestrator.calculation_service.calculate_after_tax_irr(
            fund=self.fund, session=session
        )
    
    def calculate_real_irr(self, session: Optional[Session] = None, 
                          risk_free_rate_currency: Optional[str] = None) -> Optional[float]:
        """Calculate real IRR (after inflation) for the fund."""
        return self.orchestrator.calculation_service.calculate_real_irr(
            fund=self.fund, session=session, risk_free_rate_currency=risk_free_rate_currency
        )
    
    def calculate_average_equity_balance(self, session: Optional[Session] = None, 
                                       events: Optional[List] = None) -> float:
        """Calculate time-weighted average equity balance."""
        return self.orchestrator.calculation_service.calculate_average_equity_balance(
            fund=self.fund, session=session, events=events
        )
    
    def update_average_equity_balance(self, session: Optional[Session] = None) -> None:
        """Update the fund's average equity balance."""
        self.orchestrator.calculation_service.update_average_equity_balance(
            fund=self.fund, session=session
        )
    
    # ============================================================================
    # STATUS AND METRICS METHODS - Route to status service
    # ============================================================================
    
    def get_summary_data(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """Get comprehensive fund summary data."""
        return self.orchestrator.status_service.get_summary_data(
            fund=self.fund, session=session
        )
    
    def update_status(self, session: Optional[Session] = None) -> None:
        """Update fund status based on current state."""
        self.orchestrator.status_service.update_status(
            fund=self.fund, session=session
        )
    
    def update_status_after_equity_event(self, session: Optional[Session] = None) -> None:
        """Update fund status after an equity event."""
        self.orchestrator.status_service.update_status_after_equity_event(
            fund=self.fund, session=session
        )
    
    def update_status_after_tax_statement(self, session: Optional[Session] = None) -> None:
        """Update fund status after a tax statement."""
        self.orchestrator.status_service.update_status_after_tax_statement(
            fund=self.fund, session=session
        )
    
    # ============================================================================
    # QUERY AND RETRIEVAL METHODS - Route to event service
    # ============================================================================
    
    def get_recent_events(self, limit: int = 10, exclude_system_events: bool = True, 
                         session: Optional[Session] = None) -> List[FundEvent]:
        """Get recent fund events."""
        return self.orchestrator.event_service.get_recent_events(
            fund=self.fund, limit=limit, exclude_system_events=exclude_system_events, 
            session=session
        )
    
    def get_all_fund_events(self, exclude_system_events: bool = True, 
                           session: Optional[Session] = None) -> List[FundEvent]:
        """Get all fund events."""
        return self.orchestrator.event_service.get_all_fund_events(
            fund=self.fund, exclude_system_events=exclude_system_events, 
            session=session
        )
    
    def get_events(self, event_types: Optional[List[EventType]] = None,
                   start_date: Optional[date] = None, end_date: Optional[date] = None,
                   session: Optional[Session] = None) -> List[FundEvent]:
        """Get fund events with optional filtering."""
        return self.orchestrator.event_service.get_events(
            fund=self.fund, event_types=event_types, start_date=start_date, 
            end_date=end_date, session=session
        )
    
    def delete_event(self, event_id: int, session: Optional[Session] = None) -> None:
        """Delete a fund event."""
        self.orchestrator.event_service.delete_event(
            fund=self.fund, event_id=event_id, session=session
        )
    
    # ============================================================================
    # DISTRIBUTION AND TAX METHODS - Route to tax service
    # ============================================================================
    
    def get_distributions_by_type(self, session: Optional[Session] = None) -> Dict[str, float]:
        """Get distributions grouped by type."""
        return self.orchestrator.tax_service.get_distributions_by_type(
            fund=self.fund, session=session
        )
    
    def get_total_distributions(self, session: Optional[Session] = None) -> float:
        """Get total distributions amount."""
        return self.orchestrator.tax_service.get_total_distributions(
            fund=self.fund, session=session
        )
    
    def get_taxable_distributions(self, session: Optional[Session] = None) -> float:
        """Get total taxable distributions amount."""
        return self.orchestrator.tax_service.get_taxable_distributions(
            fund=self.fund, session=session
        )
    
    def get_total_tax_withheld(self, session: Optional[Session] = None) -> float:
        """Get total tax withheld amount."""
        return self.orchestrator.tax_service.get_total_tax_withheld(
            fund=self.fund, session=session
        )
    
    # ============================================================================
    # CAPITAL CHAIN METHODS - Route to calculation service
    # ============================================================================
    
    def recalculate_capital_chain_from(self, event: FundEvent, 
                                     session: Optional[Session] = None) -> None:
        """Recalculate capital chain from a specific event."""
        self.orchestrator.calculation_service.recalculate_capital_chain_from(
            fund=self.fund, event=event, session=session
        )
    
    def update_capital_chain_incrementally(self, event: FundEvent, 
                                         session: Optional[Session] = None) -> None:
        """Update capital chain incrementally after an event."""
        self.orchestrator.calculation_service.update_capital_chain_incrementally(
            fund=self.fund, event=event, session=session
        )
    
    def update_fund_summary_fields_after_capital_event(self, 
                                                     session: Optional[Session] = None) -> None:
        """Update fund summary fields after a capital event."""
        self.orchestrator.calculation_service.update_fund_summary_fields_after_capital_event(
            fund=self.fund, session=session
        )
    
    # ============================================================================
    # BACKWARD COMPATIBILITY - Delegate to original Fund model
    # ============================================================================
    
    @property
    def calculation_service(self) -> FundCalculationService:
        """Get the calculation service (backward compatibility)."""
        if self._calculation_service is None:
            self._calculation_service = FundCalculationService()
        return self._calculation_service
    
    @property
    def status_service(self) -> FundStatusService:
        """Get the status service (backward compatibility)."""
        if self._status_service is None:
            self._status_service = FundStatusService()
        return self._status_service
    
    @property
    def tax_service(self) -> TaxCalculationService:
        """Get the tax service (backward compatibility)."""
        if self._tax_service is None:
            self._tax_service = TaxCalculationService()
        return self._tax_service
    
    @property
    def event_service(self) -> FundEventService:
        """Get the event service (backward compatibility)."""
        if self._event_service is None:
            self._event_service = FundEventService()
        return self._event_service
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate all other attributes and methods to the original Fund model.
        
        This ensures backward compatibility for all existing functionality.
        """
        return getattr(self.fund, name)
    
    def __repr__(self) -> str:
        """String representation of the fund manager."""
        return f"<FundManager(fund_id={self.fund.id}, name='{self.fund.name}')>"

    # ============================================================================
    # UTILITY AND HELPER METHODS
    # ============================================================================
    
    def is_active(self) -> bool:
        """Check if fund is active."""
        return self.fund.status == FundStatus.ACTIVE
    
    def is_completed(self) -> bool:
        """Check if fund is completed."""
        return self.fund.status == FundStatus.COMPLETED
    
    def is_realized(self) -> bool:
        """Check if fund is realized."""
        return self.fund.status == FundStatus.REALIZED
    
    def has_equity_balance(self) -> bool:
        """Check if fund has equity balance."""
        return self.fund.current_equity_balance > 0
    
    def get_commitment_utilization(self) -> float:
        """Get commitment utilization percentage."""
        if not self.fund.commitment_amount or self.fund.commitment_amount <= 0:
            return 0.0
        return (self.fund.current_equity_balance / self.fund.commitment_amount) * 100
    
    def get_remaining_commitment(self) -> float:
        """Get remaining commitment amount."""
        if not self.fund.commitment_amount:
            return 0.0
        return max(0, self.fund.commitment_amount - self.fund.current_equity_balance)
    
    def start_date(self) -> Optional[date]:
        """Get fund start date (first event date)."""
        events = self.get_all_fund_events(session=None)
        if not events:
            return None
        return min(event.event_date for event in events if event.event_date)
    
    def total_capital_called(self) -> float:
        """Get total capital called amount."""
        events = self.get_all_fund_events(session=None)
        return sum(
            event.amount for event in events 
            if event.event_type == EventType.CAPITAL_CALL and event.amount
        )
    
    def remaining_commitment(self) -> float:
        """Get remaining commitment amount."""
        return self.get_remaining_commitment()
    
    def calculate_end_date(self, session: Optional[Session] = None) -> Optional[date]:
        """Calculate fund end date based on events."""
        return self.orchestrator.status_service.calculate_end_date(
            fund=self.fund, session=session
        )
