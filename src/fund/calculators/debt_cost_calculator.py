"""
Debt Cost Calculator.

Pure mathematical calculations for debt cost and opportunity cost calculations.
Follows calculator layer rules: stateless, pure functions, no dependencies.

This calculator extracts the debt cost calculation logic from FundCalculationService
to provide clean separation of concerns and improved testability.
"""

from typing import List, Dict, Any, Tuple
from datetime import date, timedelta
from dataclasses import dataclass

from src.fund.enums import EventType, FundType


@dataclass
class DebtCostResult:
    """
    Result of debt cost calculation.
    
    Contains all the calculated values from the debt cost calculation
    to provide comprehensive information about the opportunity cost.
    """
    total_debt_cost: float
    average_risk_free_rate: float
    debt_cost_percentage: float
    investment_duration_years: float
    average_equity: float
    total_days: int


class DebtCostCalculator:
    """
    Pure calculator for debt cost and opportunity cost calculations.
    
    This calculator provides stateless, pure mathematical operations
    for debt cost calculations without any dependencies. It extracts
    the complex calculation logic from FundCalculationService to follow
    the calculator layer rules.
    
    Business context:
        Used for real IRR calculations in Fund models, to account for 
        the opportunity cost of capital.
    """
    
    @staticmethod
    def calculate_debt_cost(
        events: List[Any], 
        risk_free_rates: List[Any], 
        start_date: date, 
        end_date: date, 
        currency: str
    ) -> DebtCostResult:
        """
        Calculate debt cost (opportunity cost) using daily/period-by-period accuracy.
        
        This method provides the exact same functionality as the original
        _calculate_debt_cost_utility method, but as a pure calculator function.
        
        Args:
            events: List of FundEvent objects (capital movements)
            risk_free_rates: List of RiskFreeRate objects, sorted by date
            start_date: Start date for the calculation period
            end_date: End date for the calculation period
            currency: Currency code for the calculation
        
        Returns:
            DebtCostResult: Comprehensive debt cost calculation results
        """
        # Filter events to the relevant period
        filtered_events = [e for e in events if e.event_date >= start_date and e.event_date <= end_date]
        filtered_events.sort(key=lambda e: e.event_date)
        
        # Build periods for each risk-free rate
        rate_periods = DebtCostCalculator._build_rate_periods(risk_free_rates, end_date)
        
        # Build equity periods between events
        equity_periods = DebtCostCalculator._build_equity_periods(filtered_events, start_date, end_date)
        
        # Calculate debt cost for each equity period
        return DebtCostCalculator._calculate_period_debt_costs(equity_periods, rate_periods, start_date, end_date)
    
    @staticmethod
    def _build_rate_periods(risk_free_rates: List[Any], end_date: date) -> List[Tuple[date, date, float]]:
        """
        Build periods for each risk-free rate.
        
        Args:
            risk_free_rates: List of RiskFreeRate objects, sorted by date
            end_date: End date for the calculation period
            
        Returns:
            List of tuples: (rate_start, rate_end, rate_value)
        """
        rate_periods = []
        for i, rate in enumerate(risk_free_rates):
            rate_start = rate.rate_date
            if i + 1 < len(risk_free_rates):
                rate_end = risk_free_rates[i + 1].rate_date
            else:
                rate_end = end_date + timedelta(days=1)
            rate_periods.append((rate_start, rate_end, rate.rate))
        return rate_periods
    
    @staticmethod
    def _build_equity_periods(events: List[Any], start_date: date, end_date: date) -> List[Tuple[date, date, float]]:
        """
        Build equity periods between events.
        
        Args:
            events: List of FundEvent objects, sorted by date
            start_date: Start date for the calculation period
            end_date: End date for the calculation period
            
        Returns:
            List of tuples: (period_start, period_end, equity_amount)
        """
        equity_periods = []
        current_equity = 0
        last_date = start_date
        
        for event in events:
            if event.event_date > last_date:
                equity_periods.append((last_date, event.event_date, current_equity))
            
            # Calculate equity change based on fund type and event type
            equity_change = DebtCostCalculator._calculate_equity_change(event)
            current_equity += equity_change
            last_date = event.event_date
        
        # Add final period if needed
        if last_date < end_date:
            equity_periods.append((last_date, end_date, current_equity))
        
        return equity_periods
    
    @staticmethod
    def _calculate_equity_change(event: Any) -> float:
        """
        Calculate equity change for a single event.
        
        Args:
            event: FundEvent object
            
        Returns:
            float: Equity change amount
        """
        if not hasattr(event, 'fund'):
            return 0
        
        # Calculate equity change based on fund type and event type
        fund_type = event.fund.tracking_type
        
        if fund_type == FundType.NAV_BASED:
            if event.event_type == EventType.UNIT_PURCHASE:
                # Exclude brokerage: equity is units * unit_price
                return (event.units_purchased or 0.0) * (event.unit_price or 0.0)
            elif event.event_type == EventType.UNIT_SALE:
                # Exclude brokerage: equity is units * unit_price
                return -((event.units_sold or 0.0) * (event.unit_price or 0.0))
            else:
                return 0
        elif fund_type == FundType.COST_BASED:
            if event.event_type == EventType.CAPITAL_CALL:
                return event.amount or 0.0
            elif event.event_type == EventType.RETURN_OF_CAPITAL:
                return -(event.amount or 0.0)
            else:
                return 0
        else:
            return 0
    
    @staticmethod
    def _calculate_period_debt_costs(
        equity_periods: List[Tuple[date, date, float]], 
        rate_periods: List[Tuple[date, date, float]], 
        start_date: date, 
        end_date: date
    ) -> DebtCostResult:
        """
        Calculate debt cost for each equity period.
        
        Args:
            equity_periods: List of equity periods (start, end, amount)
            rate_periods: List of rate periods (start, end, rate)
            start_date: Start date for the calculation period
            end_date: End date for the calculation period
            
        Returns:
            DebtCostResult: Comprehensive debt cost calculation results
        """
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
            applicable_rate = DebtCostCalculator._find_applicable_rate(
                equity_start, equity_end, rate_periods
            )
            
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
        
        return DebtCostResult(
            total_debt_cost=total_debt_cost,
            average_risk_free_rate=average_risk_free_rate,
            debt_cost_percentage=debt_cost_percentage,
            investment_duration_years=investment_duration_years,
            average_equity=average_equity,
            total_days=total_days
        )
    
    @staticmethod
    def _find_applicable_rate(equity_start: date, equity_end: date, rate_periods: List[Tuple[date, date, float]]) -> float:
        """
        Find the applicable risk-free rate for a given equity period.
        
        Args:
            equity_start: Start date of the equity period
            equity_end: End date of the equity period
            rate_periods: List of rate periods (start, end, rate)
            
        Returns:
            float or None: Applicable rate, or None if not found
        """
        for rate_start, rate_end, rate_value in rate_periods:
            if rate_start <= equity_start and equity_end <= rate_end:
                return rate_value
        return None
