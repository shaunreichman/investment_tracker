"""
New Fund Manager.

This module provides a wrapper around the existing Fund model that routes
operations to the new event-driven architecture. It maintains backward
compatibility while enabling the new system.
"""

from typing import Dict, Any, Optional, Union
from datetime import date
from sqlalchemy.orm import Session

from .models import Fund, FundEvent
from .events.orchestrator import FundUpdateOrchestrator
from .enums import EventType, DistributionType, FundType
from .services.fund_calculation_service import FundCalculationService
from .services.fund_status_service import FundStatusService
from .services.tax_calculation_service import TaxCalculationService
from .services.fund_event_service import FundEventService


class NewFundManager:
    """
    New fund manager that uses the event-driven architecture.
    
    This class wraps the existing Fund model and routes operations to the
    new event handler system while maintaining backward compatibility.
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
        """String representation of the new fund manager."""
        return f"<NewFundManager(fund_id={self.fund.id}, name='{self.fund.name}')>"
