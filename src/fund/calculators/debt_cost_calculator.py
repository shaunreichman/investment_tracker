"""
Debt Cost Calculator.

Pure mathematical calculations for debt cost and opportunity cost calculations.
Follows calculator layer rules: stateless, pure functions, no dependencies.
"""

from typing import List, Dict, Any, Optional
from datetime import date, timedelta

from src.fund.models.fund_event import FundEvent
from src.rates.models.risk_free_rate import RiskFreeRate

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
        debug: bool = False
    ) -> Dict[date, Dict[str, Any]]:
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
        # Sort events by date (don't filter here - let _build_equity_periods handle date boundaries)
        filtered_events = sorted(events, key=lambda e: e.event_date)
        
        # Build periods for each risk-free rate
        rate_periods = DailyDebtCostCalculator._build_rate_periods(risk_free_rates, start_date, end_date)
        
        # Build equity periods between events
        equity_periods = DailyDebtCostCalculator._build_equity_periods(filtered_events, start_date, end_date)
        
        # Calculate debt cost for each equity period
        return DailyDebtCostCalculator._calculate_daily_debt_costs(equity_periods, rate_periods, debug)
    
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
            rate_start_date = rate.date
            if i < len(risk_free_rates) - 1:
                next_rate = risk_free_rates[i + 1]
                rate_end_date = next_rate.date
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
            start_date: Start date for filtering periods (financial year start)
            end_date: End date for filtering periods (financial year end)
            
        Returns:
            List of tuples: (period_start_date, period_end_date, equity_amount)
        """
        equity_periods = []
        
        for i, event in enumerate(events):
            # Skip events with zero equity balance - they don't create debt cost periods
            if event.current_equity_balance == 0:
                continue
                
            equity_start_date = event.event_date
            
            # Determine the end date for this equity period
            if i < len(events) - 1:
                equity_end_date = events[i + 1].event_date
            else:
                # For the last event, use the end_date if provided (financial year end), 
                # otherwise use today. This ensures debt costs are calculated for the full financial year
                equity_end_date = end_date if end_date is not None else date.today()
            
            # If the next event has zero equity balance, stop debt costs on the day before that event
            # This prevents charging debt costs on the day when equity becomes zero
            if i < len(events) - 1 and events[i + 1].current_equity_balance == 0:
                equity_end_date = events[i + 1].event_date - timedelta(days=1)

            # Skip equity periods that are completely outside the date range
            if start_date is not None and equity_end_date <= start_date:
                continue
            if end_date is not None and equity_start_date >= end_date:
                break
            
            # Adjust period boundaries to fit within the financial year
            period_start = max(equity_start_date, start_date) if start_date else equity_start_date
            period_end = min(equity_end_date, end_date) if end_date else equity_end_date
            
            # Only include periods that have a valid date range
            if period_start < period_end:
                equity_periods.append({
                    'start_date': period_start, 
                    'end_date': period_end, 
                    'equity_amount': event.current_equity_balance
                })
        
        return equity_periods


    @staticmethod
    def _calculate_daily_debt_costs(equity_periods: List[Dict[str, Any]], rate_periods: List[Dict[str, Any]], debug: bool = False) -> Dict[date, Dict[str, Any]]:
        """
        Calculate daily debt cost for each equity period.
        
        Args:
            equity_periods: List of equity periods with start_date, end_date, equity_amount
            rate_periods: List of rate periods with start_date, end_date, rate
            debug: If True, print detailed debug information
        """
        daily_debt_costs = {}
        
        if debug:
            print(f"\n=== Daily Debt Cost Calculation Debug ===")
            print(f"Equity periods: {len(equity_periods)}")
            for i, eq in enumerate(equity_periods):
                print(f"  {i+1}. {eq['start_date']} to {eq['end_date']} - Equity: ${eq['equity_amount']:,.2f}")
            print(f"Rate periods: {len(rate_periods)}")
            for i, rp in enumerate(rate_periods):
                print(f"  {i+1}. {rp['start_date']} to {rp['end_date']} - Rate: {rp['rate']:.2f}%")
        
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
                        debt_cost = eq['equity_amount'] * (rp['rate'] / 100 / 365.25)
                        daily_debt_costs[d] = {'debt_cost':debt_cost, 'equity': eq['equity_amount'], 'rate': rp['rate']}
                        d += timedelta(days=1)
        
        if debug:
            print(f"\nTotal daily debt costs calculated: {len(daily_debt_costs)}")
            if daily_debt_costs:
                min_date = min(daily_debt_costs.keys())
                max_date = max(daily_debt_costs.keys())
                print(f"Date range: {min_date} to {max_date}")
                
                # Group by unique daily charges
                charge_groups = {}
                for date_key, data in daily_debt_costs.items():
                    charge = data['debt_cost']
                    if charge not in charge_groups:
                        charge_groups[charge] = 0
                    charge_groups[charge] += 1
                
                print(f"\nSummary of unique daily charges:")
                print(f"Daily Charge |  Days")
                print(f"----------------------")
                for charge, days in sorted(charge_groups.items()):
                    print(f"{charge:11.6f} | {days:4d}")
        
        return daily_debt_costs
