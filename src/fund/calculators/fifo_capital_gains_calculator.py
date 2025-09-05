"""
FIFO Capital Gains Calculator.

Pure mathematical calculations for FIFO-based capital gains calculations.
Follows calculator layer rules: stateless, pure functions, no dependencies.

This calculator extracts the FIFO capital gains calculation logic from
FundCalculationService to provide clean separation of concerns and improved testability.

Key principles:
- Pure functions with no side effects
- No database operations (use services for database updates)
- Reusable across handlers, services, and other components
- Single source of truth for FIFO capital gains calculations
- Easy to unit test and maintain
"""

from typing import List, Tuple, Optional
from datetime import date
from dataclasses import dataclass
from collections import deque

from src.fund.enums import EventType
from src.fund.models import FundEvent


@dataclass
class FifoUnit:
    """
    Represents a unit purchase in FIFO queue.
    
    Attributes:
        units: Number of units purchased
        unit_price: Price per unit at purchase
        effective_price: Unit price including apportioned brokerage fee
        purchase_date: Date of purchase
        brokerage_fee: Total brokerage fee for this purchase
    """
    units: float
    unit_price: float
    effective_price: float  # unit_price + (brokerage_fee / units)
    purchase_date: date
    brokerage_fee: float


@dataclass
class CapitalGainResult:
    """
    Result of capital gains calculation.
    
    Attributes:
        total_capital_gains: Total capital gains from all sales
        units_sold: Total number of units sold
        average_cost_per_unit: Average cost per unit sold
        average_sale_price_per_unit: Average sale price per unit
        brokerage_fees_paid: Total brokerage fees paid on sales
        remaining_units: Units remaining in FIFO queue after all sales
    """
    total_capital_gains: float
    units_sold: float
    average_cost_per_unit: float
    average_sale_price_per_unit: float
    brokerage_fees_paid: float
    remaining_units: float


class FifoCapitalGainsCalculator:
    """
    Pure calculator for FIFO-based capital gains calculations.
    
    This calculator provides stateless, pure mathematical operations
    for FIFO capital gains calculations without any dependencies. It extracts
    the complex calculation logic from FundCalculationService to follow
    the calculator layer rules.
    
    Business context:
        Used for tax calculations and performance reporting in NAV-based funds.
        Implements FIFO (First In, First Out) method for calculating capital gains
        on unit purchases and sales, including proper handling of brokerage fees.
    """
    
    @staticmethod
    def calculate_capital_gains(events: List[FundEvent]) -> CapitalGainResult:
        """
        Calculate total capital gains using FIFO method.
        
        This is the main entry point for capital gains calculations. It processes
        all unit purchase and sale events in chronological order and calculates
        the total capital gains using the FIFO method.
        
        Args:
            events: List of FundEvent objects (unit purchases/sales)
            
        Returns:
            CapitalGainResult with detailed calculation results
            
        Business rules:
            - Purchase: cost base per unit = (units * unit_price + brokerage_fee) / units
            - Sale: proceeds per unit = unit_price - (brokerage_fee / units_sold)
            - FIFO: First purchased units are sold first
        """
        # Filter and sort events by date
        unit_events = [
            e for e in events 
            if e.event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]
        ]
        unit_events.sort(key=lambda e: e.event_date)
        
        fifo_queue = deque()
        total_capital_gains = 0.0
        total_units_sold = 0.0
        total_sale_proceeds = 0.0
        total_brokerage_fees = 0.0
        
        for event in unit_events:
            if event.event_type == EventType.UNIT_PURCHASE:
                # Skip invalid purchase events (zero units or price)
                if (event.units_purchased or 0) <= 0 or (event.unit_price or 0) <= 0:
                    continue
                fifo_unit = FifoCapitalGainsCalculator.process_purchase_event(event)
                fifo_queue.append(fifo_unit)
                
            elif event.event_type == EventType.UNIT_SALE:
                # Skip invalid sale events (zero units or price)
                if (event.units_sold or 0) <= 0 or (event.unit_price or 0) <= 0:
                    continue
                capital_gain, sale_proceeds, brokerage_fee = FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
                    event, fifo_queue
                )
                total_capital_gains += capital_gain
                total_units_sold += event.units_sold or 0
                total_sale_proceeds += sale_proceeds
                total_brokerage_fees += brokerage_fee
        
        # Calculate averages
        average_cost_per_unit = 0.0
        average_sale_price_per_unit = 0.0
        if total_units_sold > 0:
            average_sale_price_per_unit = total_sale_proceeds / total_units_sold
            # Calculate average cost from FIFO queue (simplified)
            total_cost = sum(unit.effective_price * unit.units for unit in fifo_queue)
            average_cost_per_unit = total_cost / total_units_sold if total_units_sold > 0 else 0.0
        
        # Calculate remaining units
        remaining_units = sum(unit.units for unit in fifo_queue)
        
        return CapitalGainResult(
            total_capital_gains=total_capital_gains,
            units_sold=total_units_sold,
            average_cost_per_unit=average_cost_per_unit,
            average_sale_price_per_unit=average_sale_price_per_unit,
            brokerage_fees_paid=total_brokerage_fees,
            remaining_units=remaining_units
        )
    
    @staticmethod
    def process_purchase_event(purchase_event: FundEvent) -> FifoUnit:
        """
        Convert purchase event to FIFO unit.
        
        Args:
            purchase_event: The unit purchase event
            
        Returns:
            FifoUnit object representing the purchase
            
        Raises:
            ValueError: If purchase event data is invalid
        """
        units = purchase_event.units_purchased or 0
        unit_price = purchase_event.unit_price or 0
        brokerage_fee = getattr(purchase_event, 'brokerage_fee', 0.0) or 0.0
        
        if units <= 0:
            raise ValueError("Units purchased must be positive")
        if unit_price <= 0:
            raise ValueError("Unit price must be positive")
        if brokerage_fee < 0:
            raise ValueError("Brokerage fee cannot be negative")
        
        # Calculate effective price per unit (including apportioned brokerage)
        effective_price = unit_price + (brokerage_fee / units) if units > 0 else unit_price
        
        return FifoUnit(
            units=units,
            unit_price=unit_price,
            effective_price=effective_price,
            purchase_date=purchase_event.event_date,
            brokerage_fee=brokerage_fee
        )
    
    @staticmethod
    def calculate_capital_gains_for_sale(
        sale_event: FundEvent, 
        fifo_queue: deque
    ) -> Tuple[float, float, float]:
        """
        Calculate capital gains for a single sale using FIFO.
        
        Args:
            sale_event: The unit sale event
            fifo_queue: Current FIFO queue of available units (modified in place)
            
        Returns:
            Tuple of (capital_gain, sale_proceeds, brokerage_fee)
            
        Raises:
            ValueError: If sale event data is invalid
        """
        units_to_sell = sale_event.units_sold or 0
        sale_price = sale_event.unit_price or 0
        sale_brokerage = getattr(sale_event, 'brokerage_fee', 0.0) or 0.0
        
        if units_to_sell <= 0:
            raise ValueError("Units sold must be positive")
        if sale_price <= 0:
            raise ValueError("Sale price must be positive")
        if sale_brokerage < 0:
            raise ValueError("Sale brokerage fee cannot be negative")
        
        # Calculate proceeds per unit (after deducting brokerage)
        proceeds_per_unit = sale_price - (sale_brokerage / units_to_sell) if units_to_sell > 0 else sale_price
        
        remaining_units = units_to_sell
        total_capital_gain = 0.0
        
        while remaining_units > 0 and fifo_queue:
            oldest_unit = fifo_queue[0]
            units_from_this_purchase = min(remaining_units, oldest_unit.units)
            
            # Calculate capital gain for these units
            capital_gain = units_from_this_purchase * (proceeds_per_unit - oldest_unit.effective_price)
            total_capital_gain += capital_gain
            
            remaining_units -= units_from_this_purchase
            
            # Update FIFO queue
            if units_from_this_purchase == oldest_unit.units:
                fifo_queue.popleft()
            else:
                # Update the remaining units in the oldest purchase
                fifo_queue[0] = FifoUnit(
                    units=oldest_unit.units - units_from_this_purchase,
                    unit_price=oldest_unit.unit_price,
                    effective_price=oldest_unit.effective_price,
                    purchase_date=oldest_unit.purchase_date,
                    brokerage_fee=oldest_unit.brokerage_fee
                )
        
        # Calculate total sale proceeds
        total_sale_proceeds = (units_to_sell - remaining_units) * proceeds_per_unit
        
        return total_capital_gain, total_sale_proceeds, sale_brokerage
    
    @staticmethod
    def build_fifo_queue(events: List[FundEvent]) -> List[FifoUnit]:
        """
        Build FIFO queue from purchase events only.
        
        This method is useful for incremental calculations where you need
        to build the FIFO state up to a certain point.
        
        Args:
            events: List of FundEvent objects (should be filtered to purchases only)
            
        Returns:
            List of FifoUnit objects in chronological order
        """
        purchase_events = [
            e for e in events 
            if e.event_type == EventType.UNIT_PURCHASE
        ]
        purchase_events.sort(key=lambda e: e.event_date)
        
        fifo_units = []
        for event in purchase_events:
            try:
                fifo_unit = FifoCapitalGainsCalculator.process_purchase_event(event)
                fifo_units.append(fifo_unit)
            except ValueError:
                # Skip invalid purchase events
                continue
        
        return fifo_units
    
    @staticmethod
    def calculate_remaining_units_after_sales(
        purchase_events: List[FundEvent],
        sale_events: List[FundEvent]
    ) -> List[FifoUnit]:
        """
        Calculate remaining units in FIFO queue after processing sales.
        
        This method is useful for determining what units remain available
        for future sales after processing a set of sales events.
        
        Args:
            purchase_events: List of unit purchase events
            sale_events: List of unit sale events
            
        Returns:
            List of remaining FifoUnit objects in FIFO order
        """
        # Build initial FIFO queue from purchases
        fifo_queue = deque(FifoCapitalGainsCalculator.build_fifo_queue(purchase_events))
        
        # Process sales
        for sale_event in sale_events:
            if sale_event.event_type == EventType.UNIT_SALE:
                try:
                    FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
                        sale_event, fifo_queue
                    )
                except ValueError:
                    # Skip invalid sale events
                    continue
        
        return list(fifo_queue)
    
    @staticmethod
    def validate_events(events: List[FundEvent]) -> List[str]:
        """
        Validate that events are suitable for FIFO capital gains calculation.
        
        Args:
            events: List of FundEvent objects to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        for i, event in enumerate(events):
            if event.event_type == EventType.UNIT_PURCHASE:
                if (event.units_purchased or 0) <= 0:
                    errors.append(f"Purchase event {i}: units_purchased must be positive")
                if (event.unit_price or 0) <= 0:
                    errors.append(f"Purchase event {i}: unit_price must be positive")
                    
            elif event.event_type == EventType.UNIT_SALE:
                if (event.units_sold or 0) <= 0:
                    errors.append(f"Sale event {i}: units_sold must be positive")
                if (event.unit_price or 0) <= 0:
                    errors.append(f"Sale event {i}: unit_price must be positive")
        
        return errors
