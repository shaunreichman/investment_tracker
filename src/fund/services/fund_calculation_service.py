"""
Fund Calculation Service.

This service extracts complex calculation logic from the Fund model to provide
clean separation of concerns and improved testability.

Extracted functionality:
- FIFO calculations for NAV-based funds
- Capital event field calculations
- Financial aggregation methods

Note: 
- Equity balance calculations have been moved to FundEquityCalculator
- IRR calculations have been moved to FundIrRCalculator and FundIrRService
for better separation of concerns and improved performance.
"""

from typing import List, Tuple, Optional, Dict, Any
from datetime import date, datetime
import numpy as np
import numpy_financial as npf
from sqlalchemy.orm import Session
from sqlalchemy import func

# Use string references to avoid circular imports
# from src.fund.models import Fund, FundEvent, EventType, FundType
# Migrated calculation functions are now internal utility methods

from src.shared.utils import with_session
from src.fund.enums import FundStatus, EventType
from src.fund.models import FundEvent


class FundCalculationService:
    """
    Service for handling complex fund calculations extracted from the Fund model.
    
    This service provides clean separation of concerns for:
    - FIFO calculations for NAV-based funds
    - Capital event field calculations
    - Financial aggregation methods
    
    Note: 
    - Equity balance calculations have been moved to FundEquityCalculator
    - IRR calculations have been moved to FundIrRCalculator and FundIrRService
    for better separation of concerns and improved performance.
    """
    
    def __init__(self):
        """Initialize the FundCalculationService."""
        pass
    
    # ============================================================================
    # IRR CALCULATIONS
    # ============================================================================
    # NOTE: IRR calculations have been moved to FundIrRCalculator and FundIrRService
    # for better separation of concerns and improved performance.
    # Use FundIrRService for all IRR calculations.
    
    # ============================================================================
    # EQUITY BALANCE CALCULATIONS
    # ============================================================================
    
    def calculate_actual_duration_months(self, fund: 'Fund', session: Optional[Session] = None) -> Optional[float]:
        """
        [EXTRACTED] Calculate the actual duration of the fund in months.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float or None: Duration in months, or None if not computable
        """
        if not fund.start_date:
            return None
        
        if fund.end_date:
            end_date = fund.end_date
        elif fund.status == FundStatus.ACTIVE:
            end_date = date.today()
        else:
            return None
        
        delta = end_date - fund.start_date
        return delta.days / 30.44  # Average days per month
    
    # ============================================================================
    # IRR CALCULATIONS
    # ============================================================================
    
    
    
    
    # ============================================================================
    # FINANCIAL AGGREGATION METHODS (MIGRATED FROM LEGACY)
    # ============================================================================
    
    def get_total_capital_calls(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total capital calls for the fund.
        
        This method was migrated from the legacy Fund model to provide
        capital call aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total capital calls amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.CAPITAL_CALL
        ).scalar()
        
        return float(total) if total else 0.0
    
    def get_total_capital_returns(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total capital returns for the fund.
        
        This method was migrated from the legacy Fund model to provide
        capital return aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total capital returns amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.RETURN_OF_CAPITAL
        ).scalar()
        
        return float(total) if total else 0.0
    
    def get_total_distributions(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total distributions for the fund.
        
        This method was migrated from the legacy Fund model to provide
        distribution aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total distributions amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.DISTRIBUTION
        ).scalar()
        
        return float(total) if total else 0.0
    
    def get_total_tax_withheld(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total tax withheld for the fund.
        
        This method was migrated from the legacy Fund model to provide
        tax withholding aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total tax withheld amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        total = session.query(func.sum(FundEvent.tax_withholding)).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.DISTRIBUTION,
            FundEvent.tax_withholding.isnot(None)
        ).scalar()
        
        return float(total) if total else 0.0
    
    def get_total_tax_payments(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total tax payments for the fund.
        
        This method was migrated from the legacy Fund model to provide
        tax payment aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total tax payments amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.TAX_PAYMENT
        ).scalar()
        
        return float(total) if total else 0.0
    
    def get_total_daily_interest_charges(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total daily interest charges for the fund.
        
        This method was migrated from the legacy Fund model to provide
        interest charge aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total daily interest charges amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        ).scalar()
        
        return float(total) if total else 0.0
    
    def get_total_unit_purchases(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total unit purchases for the fund.
        
        This method was migrated from the legacy Fund model to provide
        unit purchase aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total unit purchases amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.UNIT_PURCHASE
        ).scalar()
        
        return float(total) if total else 0.0
    
    def get_total_unit_sales(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total unit sales for the fund.
        
        This method was migrated from the legacy Fund model to provide
        unit sale aggregation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total unit sales amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType
        
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.UNIT_SALE
        ).scalar()
        
        return float(total) if total else 0.0
    
    def get_distributions_by_type(self, fund: 'Fund', session: Optional[Session] = None) -> Dict[str, float]:
        """
        [MIGRATED] Get distributions broken down by type.
        
        This method was migrated from the legacy Fund model to provide
        distribution type analysis capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            dict: Distribution amounts by type
        """
        if not session:
            return {}
        
        from src.fund.enums import EventType, DistributionType
        
        # Get all distribution events with their types
        distributions = session.query(
            FundEvent.distribution_type,
            func.sum(FundEvent.amount).label('total_amount')
        ).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.DISTRIBUTION,
            FundEvent.distribution_type.isnot(None)
        ).group_by(FundEvent.distribution_type).all()
        
        result = {}
        for dist_type, total_amount in distributions:
            type_name = dist_type.value if hasattr(dist_type, 'value') else str(dist_type)
            result[type_name] = float(total_amount) if total_amount else 0.0
        
        return result
    
    def get_taxable_distributions(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get total taxable distributions for the fund.
        
        This method was migrated from the legacy Fund model to provide
        taxable distribution calculation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Total taxable distributions amount
        """
        if not session:
            return 0.0
        
        from src.fund.enums import EventType, DistributionType
        
        # Taxable distributions are typically dividends and interest
        taxable_types = [DistributionType.DIVIDEND_FRANKED, DistributionType.DIVIDEND_UNFRANKED, DistributionType.INTEREST]
        
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.DISTRIBUTION,
            FundEvent.distribution_type.in_(taxable_types)
        ).scalar()
        
        return float(total) if total else 0.0
    
    def get_gross_distributions(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get gross distributions (before tax withholding) for the fund.
        
        This method was migrated from the legacy Fund model to provide
        gross distribution calculation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Gross distributions amount
        """
        # Gross distributions are the same as total distributions
        return self.get_total_distributions(fund, session)
    
    def get_net_distributions(self, fund: 'Fund', session: Optional[Session] = None) -> float:
        """
        [MIGRATED] Get net distributions (after tax withholding) for the fund.
        
        This method was migrated from the legacy Fund model to provide
        net distribution calculation capabilities.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float: Net distributions amount
        """
        total_distributions = self.get_total_distributions(fund, session)
        total_tax_withheld = self.get_total_tax_withheld(fund, session)
        
        return total_distributions - total_tax_withheld

    # ============================================================================
    # MIGRATED CALCULATION FUNCTIONS FROM fund/calculations.py
    # ============================================================================
    

    def _calculate_debt_cost_utility(self, events, risk_free_rates, start_date, end_date, currency):
        """
        [MIGRATED] Calculate debt cost (opportunity cost) using daily/period-by-period accuracy.
        
        This method was migrated from the old fund/calculations.py module.
        
        Args:
            events (list): List of FundEvent objects (capital movements).
            risk_free_rates (list): List of RiskFreeRate objects, sorted by date.
            start_date (date): Start date for the calculation period.
            end_date (date): End date for the calculation period.
            currency (str): Currency code for the calculation.
        
        Returns:
            dict: {
                'total_debt_cost': float,  # Total opportunity cost over the period
                'average_risk_free_rate': float,  # Weighted average risk-free rate
                'debt_cost_percentage': float,  # Debt cost as a percentage of average equity
                'investment_duration_years': float,  # Duration in years
                'average_equity': float,  # Average equity over the period
                'total_days': int  # Number of days in the period
            }
        
        Business context:
            Used for real IRR calculations in Fund models, to account for the opportunity cost of capital.
        """
        from datetime import timedelta
        from src.fund.enums import EventType, FundType
        
        # Filter events to the relevant period
        events = [e for e in events if e.event_date >= start_date and e.event_date <= end_date]
        events.sort(key=lambda e: e.event_date)
        # Build periods for each risk-free rate
        rate_periods = []
        for i, rate in enumerate(risk_free_rates):
            rate_start = rate.rate_date
            if i + 1 < len(risk_free_rates):
                rate_end = risk_free_rates[i + 1].rate_date
            else:
                rate_end = end_date + timedelta(days=1)
            rate_periods.append((rate_start, rate_end, rate.rate))
        # Build equity periods between events
        equity_periods = []
        current_equity = 0
        last_date = start_date
        for event in events:
            if event.event_date > last_date:
                equity_periods.append((last_date, event.event_date, current_equity))
            if hasattr(event, 'fund'):
                # Calculate equity change based on fund type and event type
                fund_type = event.fund.tracking_type
                if fund_type == FundType.NAV_BASED:
                    if event.event_type == EventType.UNIT_PURCHASE:
                        # Exclude brokerage: equity is units * unit_price
                        equity_change = (event.units_purchased or 0.0) * (event.unit_price or 0.0)
                    elif event.event_type == EventType.UNIT_SALE:
                        # Exclude brokerage: equity is units * unit_price
                        equity_change = -((event.units_sold or 0.0) * (event.unit_price or 0.0))
                    else:
                        equity_change = 0
                elif fund_type == FundType.COST_BASED:
                    if event.event_type == EventType.CAPITAL_CALL:
                        equity_change = event.amount or 0.0
                    elif event.event_type == EventType.RETURN_OF_CAPITAL:
                        equity_change = -(event.amount or 0.0)
                    else:
                        equity_change = 0
                else:
                    equity_change = 0
            else:
                equity_change = 0
            current_equity += equity_change
            last_date = event.event_date
        if last_date < end_date:
            equity_periods.append((last_date, end_date, current_equity))
        total_debt_cost = 0
        total_weighted_rate = 0
        total_days = 0
        total_weighted_equity = 0
        # Calculate debt cost for each equity period
        for equity_start, equity_end, equity_amount in equity_periods:
            period_days = (equity_end - equity_start).days
            if period_days <= 0:
                continue
            # Find applicable risk-free rate for this period
            applicable_rate = None
            for rate_start, rate_end, rate_value in rate_periods:
                if rate_start <= equity_start and equity_end <= rate_end:
                    applicable_rate = rate_value
                    break
            if applicable_rate is None:
                continue
            # Calculate debt cost for this period
            period_debt_cost = equity_amount * (applicable_rate / 100) * (period_days / 365.25)
            total_debt_cost += period_debt_cost
            total_weighted_rate += applicable_rate * period_days
            total_days += period_days
            total_weighted_equity += equity_amount * period_days
        # Calculate summary statistics
        # Handle single day periods - ensure at least 1 day
        if start_date == end_date:
            total_days = max(total_days, 1)
        
        average_risk_free_rate = total_weighted_rate / total_days if total_days > 0 else 0
        average_equity = total_weighted_equity / total_days if total_days > 0 else 0
        debt_cost_percentage = (total_debt_cost / average_equity * 100) if average_equity > 0 else 0
        investment_duration_years = total_days / 365.25
        return {
            'total_debt_cost': total_debt_cost,
            'average_risk_free_rate': average_risk_free_rate,
            'debt_cost_percentage': debt_cost_percentage,
            'investment_duration_years': investment_duration_years,
            'average_equity': average_equity,
            'total_days': total_days
        }

    def _calculate_nav_based_capital_gains_utility(self, events):
        """
        [MIGRATED] Calculate capital gains for NAV-based funds using FIFO method, including brokerage fees.
        - Purchase: cost base per unit = (units * unit_price + brokerage_fee) / units
        - Sale: proceeds per unit = unit_price - (brokerage_fee / units_sold)
        
        This method was migrated from the old fund/calculations.py module.
        
        Args:
            events (list): List of FundEvent objects (unit purchases/sales).
        Returns:
            float: Total capital gains.
        Business context:
            Used for tax calculations and performance reporting in NAV-based funds.
        """
        from collections import deque
        from src.fund.enums import EventType
        
        available_units = deque()  # Each entry: (units, cost_per_unit)
        total_capital_gains = 0
        for event in events:
            if event.event_type == EventType.UNIT_PURCHASE:
                units = event.units_purchased or 0
                unit_price = event.unit_price or 0
                brokerage_fee = getattr(event, 'brokerage_fee', 0.0) or 0.0
                if units > 0 and unit_price > 0:
                    # Apportion brokerage per unit and add to cost base
                    cost_per_unit = unit_price + (brokerage_fee / units)
                    available_units.append((units, cost_per_unit))
            elif event.event_type == EventType.UNIT_SALE:
                units_to_sell = event.units_sold or 0
                sale_price_per_unit = event.unit_price or 0
                sale_brokerage_fee = getattr(event, 'brokerage_fee', 0.0) or 0.0
                if units_to_sell > 0 and sale_price_per_unit > 0:
                    # Apportion sale brokerage per unit
                    proceeds_per_unit = sale_price_per_unit - (sale_brokerage_fee / units_to_sell)
                    remaining_units_to_sell = units_to_sell
                    while remaining_units_to_sell > 0 and available_units:
                        available_units_count, cost_per_unit = available_units[0]
                        units_from_this_purchase = min(remaining_units_to_sell, available_units_count)
                        # Calculate capital gain for these units
                        capital_gain = units_from_this_purchase * (proceeds_per_unit - cost_per_unit)
                        total_capital_gains += capital_gain
                        remaining_units_to_sell -= units_from_this_purchase
                        # Update or remove from available units
                        if units_from_this_purchase == available_units_count:
                            available_units.popleft()
                        else:
                            available_units[0] = (available_units_count - units_from_this_purchase, cost_per_unit)
        return total_capital_gains

    def _calculate_cost_based_capital_gains_utility(self, events):
        """
        [MIGRATED] Calculate capital gains for cost-based funds.
        
        This method was migrated from the old fund/calculations.py module.
        
        Args:
            events (list): List of FundEvent objects (capital calls/returns).
        
        Returns:
            float: Total capital gains.
        
        Business context:
            Used for tax calculations and performance reporting in cost-based funds.
        """
        from src.fund.enums import EventType, DistributionType
        
        # For cost-based funds, capital gains are typically distributions
        total_capital_gains = 0
        for event in events:
            if event.event_type == EventType.DISTRIBUTION and event.distribution_type and event.distribution_type == DistributionType.CAPITAL_GAIN:
                total_capital_gains += event.amount or 0
        return total_capital_gains
