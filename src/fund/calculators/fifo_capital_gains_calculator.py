"""
FIFO Capital Gains Calculator.

Pure mathematical calculations for FIFO-based capital gains calculations.
Follows calculator layer rules: stateless, pure functions, no dependencies.

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

from src.fund.enums.fund_event_enums import EventType
from src.fund.enums.fund_enums import TAX_JURISDICTION_TO_CAPITAL_GAINS_DISCOUNTING
from src.fund.models import FundEvent
from src.shared.enums.shared_enums import Country


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
class CapitalGainSaleDetail:
    """
    Detailed breakdown of a capital gain from a single sale.
    
    Attributes:
        sale_date: Date of the sale
        units_sold: Number of units sold
        capital_gain: Total capital gain from this sale
        discounted_capital_gain: Discounted capital gain (if applicable)
        holding_period_days: Average holding period in days for units sold
        qualified_for_discount: Whether this sale qualified for the discount
    """
    sale_date: date
    units_sold: float
    capital_gain: float
    discounted_capital_gain: float
    holding_period_days: float
    qualified_for_discount: bool


@dataclass
class CapitalGainResult:
    """
    Result of capital gains calculation.
    
    Attributes:
        capital_gains_total: Total capital gains from all sales (regardless of discounting)
        capital_gains_discounting_total: Total capital gains which are applicable for discounting
        capital_gains_discounting_taxable_total: Taxable capital gains from the discounted component (50% of discounting_total)
        capital_gains_taxable_total: Total taxable capital gains (discounting_taxable + non-discounting)
        units_sold: Total number of units sold
        average_cost_per_unit: Average cost per unit sold
        average_sale_price_per_unit: Average sale price per unit
        brokerage_fees_paid: Total brokerage fees paid on sales
        remaining_units: Units remaining in FIFO queue after all sales
        sale_details: Detailed breakdown of each sale for audit purposes
        tax_jurisdiction: Tax jurisdiction used for discount calculations
    """
    capital_gains_total: float
    capital_gains_discounting_total: float
    capital_gains_discounting_taxable_total: float
    capital_gains_taxable_total: float
    units_sold: float
    average_cost_per_unit: float
    average_sale_price_per_unit: float
    brokerage_fees_paid: float
    remaining_units: float
    sale_details: List[CapitalGainSaleDetail]
    tax_jurisdiction: Optional[Country]


class FifoCapitalGainsCalculator:
    """
    Pure calculator for FIFO-based capital gains calculations.
    
    Business context:
        Used for tax calculations and performance reporting in NAV-based funds.
        Implements FIFO (First In, First Out) method for calculating capital gains
        on unit purchases and sales, including proper handling of brokerage fees.
        Supports Australian 50% capital gains discount for assets held > 12 months.
    """
    
    @staticmethod
    def calculate_holding_period_days(purchase_date: date, sale_date: date) -> int:
        """
        Calculate holding period in days between purchase and sale dates.
        
        Args:
            purchase_date: Date when units were purchased
            sale_date: Date when units were sold
            
        Returns:
            Number of days between purchase and sale
            
        Raises:
            ValueError: If sale_date is before purchase_date
        """
        if sale_date < purchase_date:
            raise ValueError("Sale date cannot be before purchase date")
        
        # Calculate the difference in days
        holding_period = (sale_date - purchase_date).days
        return holding_period
    
    @staticmethod
    def qualifies_for_capital_gains_discount(holding_period_days: int, tax_jurisdiction: Optional[Country], discount_applicable: bool = True) -> bool:
        """
        Check if a holding period qualifies for capital gains discount based on tax jurisdiction rules.
        
        Args:
            holding_period_days: Number of days the asset was held
            tax_jurisdiction: Tax jurisdiction to check rules for
            discount_applicable: Whether capital gains discount is applicable (e.g., False for non-residents)
            
        Returns:
            True if the holding period qualifies for the discount
        """
        # If discount is not applicable (e.g., non-resident), return False regardless of jurisdiction rules
        if not discount_applicable:
            return False
            
        if not tax_jurisdiction or tax_jurisdiction not in TAX_JURISDICTION_TO_CAPITAL_GAINS_DISCOUNTING:
            return False
            
        discount_config = TAX_JURISDICTION_TO_CAPITAL_GAINS_DISCOUNTING[tax_jurisdiction]
        
        if not discount_config['enabled']:
            return False
            
        # Convert months to days (using 30.44 days per month for accuracy)
        required_days = discount_config['duration_months'] * 30.44
        
        # Must be held for MORE than the required duration
        return holding_period_days > required_days
    
    @staticmethod
    def calculate_discounted_capital_gain(capital_gain: float, tax_jurisdiction: Optional[Country], discount_applicable: bool = True) -> float:
        """
        Calculate discounted capital gain based on tax jurisdiction rules.
        
        Args:
            capital_gain: The original capital gain amount
            tax_jurisdiction: Tax jurisdiction to apply rules for
            discount_applicable: Whether capital gains discount is applicable (e.g., False for non-residents)
            
        Returns:
            Discounted capital gain amount
        """
        # If discount is not applicable (e.g., non-resident), return full capital gain
        if not discount_applicable or capital_gain <= 0:
            return capital_gain
            
        if not tax_jurisdiction or tax_jurisdiction not in TAX_JURISDICTION_TO_CAPITAL_GAINS_DISCOUNTING:
            return capital_gain
            
        discount_config = TAX_JURISDICTION_TO_CAPITAL_GAINS_DISCOUNTING[tax_jurisdiction]
        
        if not discount_config['enabled']:
            return capital_gain
            
        # Apply the discount percentage
        discount_percentage = discount_config['percentage'] / 100.0
        return capital_gain * (1 - discount_percentage)
    
    @staticmethod
    def calculate_capital_gains(fund_events: List[FundEvent], cg_start_date: Optional[date] = None, cg_end_date: Optional[date] = None, tax_jurisdiction: Optional[Country] = None, capital_gain_discount_applicable: bool = True) -> CapitalGainResult:
        """
        Calculate total capital gains using FIFO method from a list of sorted fund events.
        
        This is the main entry point for capital gains calculations. It processes
        all unit purchase and sale events in chronological order and calculates
        the total capital gains using the FIFO method.
        
        Args:
            fund_events: List of sorted FundEvent objects to process
            cg_start_date: Optional start date for capital gains calculation
            cg_end_date: Optional end date for capital gains calculation
            tax_jurisdiction: Optional tax jurisdiction to represent if we need to calculate discounted capital gain
            capital_gain_discount_applicable: Whether capital gains discount is applicable (e.g., False for non-residents)
            
        Returns:
            CapitalGainResult with detailed calculation results
            
        Business rules:
            - Purchase: cost base per unit = (units * unit_price + brokerage_fee) / units
            - Sale: proceeds per unit = unit_price - (brokerage_fee / units_sold)
            - FIFO: First purchased units are sold first
        """
        # Sort events by date to ensure chronological processing
        sorted_events = sorted(fund_events, key=lambda e: e.event_date)
        
        fifo_queue = deque()
        capital_gains_total = 0.0
        capital_gains_discounting_total = 0.0
        capital_gains_discounting_taxable_total = 0.0
        capital_gains_taxable_total = 0.0
        total_units_sold = 0.0
        total_sale_proceeds = 0.0
        total_brokerage_fees = 0.0
        sale_details = []
        
        for event in sorted_events:
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
                    
                # Calculate capital gains with discount support
                capital_gain, sale_proceeds, brokerage_fee, avg_holding_period_days, qualified_for_discount, discountable_capital_gain = FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
                    event, fifo_queue, tax_jurisdiction, capital_gain_discount_applicable
                )
                
                # Apply date filters
                if cg_start_date and cg_start_date > event.event_date:
                    continue
                if cg_end_date and event.event_date > cg_end_date:
                    continue
                
                # Accumulate totals
                capital_gains_total += capital_gain
                capital_gains_discounting_total += discountable_capital_gain
                
                # Calculate discounted amount on-demand using tax jurisdiction rules
                discounted_capital_gain = FifoCapitalGainsCalculator.calculate_discounted_capital_gain(discountable_capital_gain, tax_jurisdiction, capital_gain_discount_applicable)
                capital_gains_discounting_taxable_total += discounted_capital_gain
                
                # Calculate taxable amount: discounted portion + non-discountable portion
                non_discountable_gains = capital_gain - discountable_capital_gain
                capital_gains_taxable_total += discounted_capital_gain + non_discountable_gains
                total_units_sold += event.units_sold or 0
                total_sale_proceeds += sale_proceeds
                total_brokerage_fees += brokerage_fee
                
                # Calculate discounted capital gain for sale detail
                sale_discounted_capital_gain = FifoCapitalGainsCalculator.calculate_discounted_capital_gain(discountable_capital_gain, tax_jurisdiction, capital_gain_discount_applicable) if qualified_for_discount else capital_gain
                
                # Store detailed sale information
                sale_detail = CapitalGainSaleDetail(
                    sale_date=event.event_date,
                    units_sold=event.units_sold or 0,
                    capital_gain=capital_gain,
                    discounted_capital_gain=sale_discounted_capital_gain,
                    holding_period_days=avg_holding_period_days,
                    qualified_for_discount=qualified_for_discount
                )
                sale_details.append(sale_detail)

        # Calculate remaining units
        remaining_units = sum(unit.units for unit in fifo_queue)
        
        # Calculate averages
        average_cost_per_unit = 0.0
        average_sale_price_per_unit = 0.0
        if total_units_sold > 0:
            average_sale_price_per_unit = total_sale_proceeds / total_units_sold
            # Calculate average cost from FIFO queue (simplified)
            total_cost = sum(unit.effective_price * unit.units for unit in fifo_queue)
            average_cost_per_unit = total_cost / total_units_sold if total_units_sold > 0 else 0.0
        
        return CapitalGainResult(
            capital_gains_total=capital_gains_total,
            capital_gains_discounting_total=capital_gains_discounting_total,
            capital_gains_discounting_taxable_total=capital_gains_discounting_taxable_total,
            capital_gains_taxable_total=capital_gains_taxable_total,
            units_sold=total_units_sold,
            average_cost_per_unit=average_cost_per_unit,
            average_sale_price_per_unit=average_sale_price_per_unit,
            brokerage_fees_paid=total_brokerage_fees,
            remaining_units=remaining_units,
            sale_details=sale_details,
            tax_jurisdiction=tax_jurisdiction
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
        fifo_queue: deque,
        tax_jurisdiction: Optional[Country] = None,
        discount_applicable: bool = True
    ) -> Tuple[float, float, float, float, bool, float]:
        """
        Calculate capital gains for a single sale using FIFO with discount support.
        
        Args:
            sale_event: The unit sale event
            fifo_queue: Current FIFO queue of available units (modified in place)
            tax_jurisdiction: Tax jurisdiction for discount calculations
            discount_applicable: Whether capital gains discount is applicable (e.g., False for non-residents)
            
        Returns:
            Tuple of (capital_gain, sale_proceeds, brokerage_fee, avg_holding_period_days, qualified_for_discount, discountable_capital_gain)
            
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
        total_discountable_capital_gain = 0.0
        total_holding_period_days = 0.0
        units_processed = 0.0
        qualified_for_discount = False
        
        while remaining_units > 0 and fifo_queue:
            oldest_unit = fifo_queue[0]
            units_from_this_purchase = min(remaining_units, oldest_unit.units)
            
            # Calculate holding period for this purchase
            holding_period_days = FifoCapitalGainsCalculator.calculate_holding_period_days(
                oldest_unit.purchase_date, sale_event.event_date
            )
            
            # Calculate capital gain for these units
            capital_gain = units_from_this_purchase * (proceeds_per_unit - oldest_unit.effective_price)
            total_capital_gain += capital_gain
            
            # Track discountable amount if applicable
            if FifoCapitalGainsCalculator.qualifies_for_capital_gains_discount(holding_period_days, tax_jurisdiction, discount_applicable):
                total_discountable_capital_gain += capital_gain  # Track the amount that qualifies for discounting
                qualified_for_discount = True
            
            # Track weighted average holding period
            total_holding_period_days += holding_period_days * units_from_this_purchase
            units_processed += units_from_this_purchase
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
        
        # Calculate average holding period
        avg_holding_period_days = total_holding_period_days / units_processed if units_processed > 0 else 0.0
        
        return total_capital_gain, total_sale_proceeds, sale_brokerage, avg_holding_period_days, qualified_for_discount, total_discountable_capital_gain
    
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
                        sale_event, fifo_queue, tax_jurisdiction=None, discount_applicable=True
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
