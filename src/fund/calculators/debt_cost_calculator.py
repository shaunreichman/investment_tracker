"""
Debt Cost Calculator.

Pure mathematical calculations for debt cost and opportunity cost calculations.
Follows calculator layer rules: stateless, pure functions, no dependencies.
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import date, timedelta
from dataclasses import dataclass

from src.fund.models.fund_event import FundEvent
from src.rates.models.risk_free_rate import RiskFreeRate


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

@dataclass
class DailyDebtCost:
    """
    Daily debt cost calculation result.
    """
    date: date
    debt_cost: float
    equity: float
    rate: float


class DailyDebtCostCalculator:
    """
    Pure calculator for debt cost and opportunity cost calculations.
    
    Business context:
        Used for real IRR calculations in Fund models, to account for 
        the opportunity cost of capital.
    """
    
    @staticmethod
    def calculate_debt_cost(
        events: List[FundEvent], 
        risk_free_rates: List[RiskFreeRate], 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None, 
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
        
        Returns:
            DebtCostResult: Comprehensive debt cost calculation results
        """
        # Filter events to the relevant period
        if start_date is not None:
            filtered_events = [e for e in events if e.event_date >= start_date]
        if end_date is not None:
            filtered_events = [e for e in filtered_events if e.event_date <= end_date]
        filtered_events.sort(key=lambda e: e.event_date)
        
        # Build periods for each risk-free rate
        rate_periods = DailyDebtCostCalculator._build_rate_periods(risk_free_rates, start_date, end_date)
        
        # Build equity periods between events
        equity_periods = DailyDebtCostCalculator._build_equity_periods(filtered_events)
        
        # Calculate debt cost for each equity period
        return DailyDebtCostCalculator._calculate_period_debt_costs(equity_periods, rate_periods, start_date, end_date)
    
    @staticmethod
    def _build_rate_periods(risk_free_rates: List[RiskFreeRate], start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Build periods for each risk-free rate.
        
        Args:
            risk_free_rates: List of RiskFreeRate objects, sorted by date
            
        Returns:
            List of tuples: (rate_start_date, rate_end_date, rate_value)
        """
        rate_periods = []
        for i, rate in enumerate(risk_free_rates):
            rate_start_date = rate.rate_date
            if i <= len(risk_free_rates) - 1:
                rate_end_date = risk_free_rates[i + 1].rate_date
            else:
                rate_end_date = date.today()
            
            # Skip rate periods that are before the start date or after the end date
            if start_date is not None and rate_end_date < start_date:
                continue
            if end_date is not None and rate_start_date > end_date:
                break
            
            rate_periods.append({'start_date': rate_start_date, 'end_date': rate_end_date, 'rate': rate.rate})
        return rate_periods
    
    @staticmethod
    def _build_equity_periods(events: List[FundEvent], start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Build equity periods between events.
        
        Args:
            events: List of FundEvent objects, sorted by date
            
        Returns:
            List of tuples: (period_start_date, period_end_date, equity_amount)
        """
        equity_periods = []
        
        for i, event in enumerate(events):
            if event.current_equity_balance == 0:
                continue
            equity_start_date = event.event_date
            if i <= len(events) - 1:
                equity_end_date = events[i + 1].event_date
            else:
                equity_end_date = date.today()

            # Skip equity periods that are before the start date or after the end date
            if start_date is not None and equity_end_date < start_date:
                continue
            if end_date is not None and equity_start_date > end_date:
                break
            
            equity_periods.append({'start_date': equity_start_date, 'end_date': equity_end_date, 'equity_amount': event.current_equity_balance})
        
        return equity_periods



    @staticmethod
    def _calculate_daily_debt_costs(equity_periods: List[Dict[str, Any]], rate_periods: List[Dict[str, Any]]) -> Dict[date, Dict[str, Any]]:
        """
        Calculate daily debt cost for each equity period.
        """
        daily_debt_costs = Dict[date, Dict[str, Any]]
        for eq in equity_periods:
            for rp in rate_periods:
                if rp['start_date'] > eq['end_date']:
                    # Rate period starts after equity period ends - already passed it
                    break

                # Find overlap between equity and rate periods
                overlap_start = max(eq['start_date'], rp['start_date'])
                overlap_end = min(eq['end_date'], rp['end_date'])
                if overlap_start <= overlap_end:
                    # Loop over each day in the overlap
                    d = overlap_start
                    while d <= overlap_end:
                        debt_cost = eq['equity_amount'] * (rp['rate'] / 365.25)
                        daily_debt_costs[d] = {'debt_cost':debt_cost, 'equity': eq['equity_amount'], 'rate': rp['rate']}
                        d += timedelta(days=1)
        return daily_debt_costs



    
    # @staticmethod
    # def _calculate_period_debt_costs(
    #     equity_periods: List[Tuple[date, date, float]], 
    #     rate_periods: List[Tuple[date, date, float]], 
    #     start_date: date, 
    #     end_date: date
    # ) -> DebtCostResult:
    #     """
    #     Calculate debt cost for each equity period.
        
    #     Args:
    #         equity_periods: List of equity periods (start_date, end_date, amount)
    #         rate_periods: List of rate periods (start_date, end_date, rate)
    #         start_date: Start date for the calculation period
    #         end_date: End date for the calculation period
            
    #     Returns:
    #         DebtCostResult: Comprehensive debt cost calculation results
    #     """
    #     total_debt_cost = 0
    #     total_weighted_rate = 0
    #     total_days = 0
    #     total_weighted_equity = 0
        
    #     # Calculate debt cost for each equity period
    #     for equity_start_date, equity_end_date, equity_amount in equity_periods:
    #         period_days = (equity_end_date - equity_start_date).days
    #         if period_days <= 0:
    #             continue
            
    #         # Find applicable risk-free rate for this period
    #         applicable_rate = DebtCostCalculator._find_applicable_rate(
    #             equity_start_date, equity_end_date, rate_periods
    #         )
            
    #         if applicable_rate is None:
    #             continue
            
    #         # Calculate debt cost for this period
    #         period_debt_cost = equity_amount * (applicable_rate / 100) * (period_days / 365.25)
    #         total_debt_cost += period_debt_cost
    #         total_weighted_rate += applicable_rate * period_days
    #         total_days += period_days
    #         total_weighted_equity += equity_amount * period_days
        
    #     # Calculate summary statistics
    #     # Handle single day periods - ensure at least 1 day
    #     if start_date == end_date:
    #         total_days = max(total_days, 1)
        
    #     average_risk_free_rate = total_weighted_rate / total_days if total_days > 0 else 0
    #     average_equity = total_weighted_equity / total_days if total_days > 0 else 0
    #     debt_cost_percentage = (total_debt_cost / average_equity * 100) if average_equity > 0 else 0
    #     investment_duration_years = total_days / 365.25
        
    #     return DebtCostResult(
    #         total_debt_cost=total_debt_cost,
    #         average_risk_free_rate=average_risk_free_rate,
    #         debt_cost_percentage=debt_cost_percentage,
    #         investment_duration_years=investment_duration_years,
    #         average_equity=average_equity,
    #         total_days=total_days
    #     )
    
    # @staticmethod
    # def _find_applicable_rate(equity_start_date: date, equity_end_date: date, rate_periods: List[Tuple[date, date, float]]) -> float:
    #     """
    #     Find the applicable risk-free rate for a given equity period.
        
    #     Args:
    #         equity_start_date: Start date of the equity period
    #         equity_end_date: End date of the equity period
    #         rate_periods: List of rate periods (start, end, rate)
            
    #     Returns:
    #         float or None: Applicable rate, or None if not found
    #     """
    #     for rate_start, rate_end, rate_value in rate_periods:
    #         if rate_start <= equity_start_date and equity_end_date <= rate_end:
    #             return rate_value
    #     return None
