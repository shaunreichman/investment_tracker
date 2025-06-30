#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, RiskFreeRate, EventType

def debug_debt_cost_calculation(fund_name="Senior Debt Fund No.24"):
    """Debug the debt cost calculation with detailed breakdown."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Find the fund
    fund = session.query(Fund).filter(Fund.name == fund_name).first()
    if not fund:
        print(f"Fund '{fund_name}' not found!")
        return
    
    print(f"DEBUGGING DEBT COST CALCULATION FOR: {fund.name}")
    print("=" * 60)
    
    # Get fund dates
    start_date = fund.start_date
    end_date = fund.end_date
    print(f"Investment Period: {start_date} to {end_date}")
    print(f"Total Days: {(end_date - start_date).days}")
    print()
    
    # Get all equity change events, sorted by date
    events = [e for e in fund.fund_events if e.event_date >= start_date and e.event_date <= end_date]
    events.sort(key=lambda e: e.event_date)
    
    print("EQUITY CHANGE EVENTS:")
    print("-" * 40)
    current_equity = 0
    for event in events:
        equity_change = fund._get_equity_change_for_event(event)
        current_equity += equity_change
        print(f"{event.event_date}: {event.event_type} (${event.amount:,.0f}) -> Equity Change: ${equity_change:+,.0f} -> New Balance: ${current_equity:,.0f}")
    print()
    
    # Build equity periods
    print("EQUITY PERIODS:")
    print("-" * 40)
    equity_periods = []
    current_equity = 0
    last_date = start_date
    
    for event in events:
        if event.event_date > last_date:
            equity_periods.append((last_date, event.event_date, current_equity))
            print(f"Period: {last_date} to {event.event_date} ({event.event_date - last_date} days) - Equity: ${current_equity:,.0f}")
        
        equity_change = fund._get_equity_change_for_event(event)
        current_equity += equity_change
        last_date = event.event_date
    
    # Add final period if needed
    if last_date < end_date:
        equity_periods.append((last_date, end_date, current_equity))
        print(f"Period: {last_date} to {end_date} ({end_date - last_date} days) - Equity: ${current_equity:,.0f}")
    print()
    
    # Get risk-free rates
    risk_free_rates = session.query(RiskFreeRate).filter(
        RiskFreeRate.currency == fund.currency,
        RiskFreeRate.rate_date <= end_date
    ).order_by(RiskFreeRate.rate_date).all()
    
    print("RISK-FREE RATES:")
    print("-" * 40)
    for rate in risk_free_rates:
        print(f"{rate.rate_date}: {rate.rate}%")
    print()
    
    # Build rate periods
    print("RISK-FREE RATE PERIODS:")
    print("-" * 40)
    rate_periods = []
    for i, rate in enumerate(risk_free_rates):
        rate_start = rate.rate_date
        if i + 1 < len(risk_free_rates):
            rate_end = risk_free_rates[i + 1].rate_date
        else:
            rate_end = end_date + timedelta(days=1)
        rate_periods.append((rate_start, rate_end, rate.rate))
        print(f"Rate Period: {rate_start} to {rate_end} - Rate: {rate.rate}%")
    print()
    
    # Calculate debt cost with detailed breakdown
    print("DEBT COST CALCULATION BREAKDOWN:")
    print("-" * 40)
    total_debt_cost = 0
    total_days = 0
    weighted_rfr_sum = 0
    weighted_equity_days = 0  # Track equity-weighted days for rate calculation
    
    # Group by unique equity + rate combinations
    equity_rate_combinations = {}
    
    for eq_start, eq_end, equity in equity_periods:
        period_start = eq_start
        while period_start < eq_end:
            # Find the risk-free rate for this day
            rate = None
            sub_period_end = eq_end
            
            for r_start, r_end, r_value in rate_periods:
                if r_start <= period_start < r_end:
                    rate = r_value
                    sub_period_end = min(eq_end, r_end)
                    break
            
            if rate is None:
                # Use the most recent available rate
                rate = rate_periods[-1][2]
                sub_period_end = eq_end
            
            days = (sub_period_end - period_start).days
            if days > 0 and equity != 0:
                cost = equity * (rate / 100) * (days / 365.25)
                total_debt_cost += cost
                weighted_rfr_sum += rate * days * equity  # Equity-weighted rate calculation
                weighted_equity_days += days * equity  # Equity-weighted days
                total_days += days
                
                # Group by equity + rate combination
                key = (equity, rate)
                if key not in equity_rate_combinations:
                    equity_rate_combinations[key] = {'days': 0, 'cost': 0, 'periods': []}
                
                equity_rate_combinations[key]['days'] += days
                equity_rate_combinations[key]['cost'] += cost
                equity_rate_combinations[key]['periods'].append((period_start, sub_period_end, days))
            
            period_start = sub_period_end
    
    # Display grouped results
    print("GROUPED BY EQUITY BALANCE + RISK-FREE RATE:")
    print("-" * 60)
    print(f"{'Equity':>12} {'Rate':>6} {'Days':>6} {'Cost':>12} {'Periods'}")
    print("-" * 60)
    
    for (equity, rate), data in sorted(equity_rate_combinations.items()):
        print(f"${equity:>10,.0f} {rate:>5.2f}% {data['days']:>5} ${data['cost']:>10,.2f} ", end="")
        
        # Show the periods for this combination
        period_strs = []
        for start, end, days in data['periods']:
            period_strs.append(f"{start} to {end} ({days}d)")
        print(" | ".join(period_strs))
    
    print("-" * 60)
    print(f"{'TOTAL':>12} {'':>6} {total_days:>6} ${total_debt_cost:>10,.2f}")
    print()
    
    print(f"SUMMARY:")
    print("-" * 40)
    print(f"Total Days: {total_days}")
    print(f"Total Debt Cost: ${total_debt_cost:,.2f}")
    print(f"Weighted RFR Sum: {weighted_rfr_sum:,.2f}")
    print(f"Average Risk-Free Rate: {weighted_rfr_sum / weighted_equity_days:.2f}%" if weighted_equity_days > 0 else "No days calculated")
    
    # Calculate sum of all equity balances
    total_equity_days = 0
    for (equity, rate), data in equity_rate_combinations.items():
        total_equity_days += equity * data['days']
    
    print(f"Sum of Equity × Days: {total_equity_days:,.0f}")
    print(f"Average Equity Balance: {total_equity_days / total_days:,.0f}" if total_days > 0 else "No days calculated")
    
    # Compare with fund's calculation
    debt_cost_data = fund.calculate_debt_cost(session)
    if debt_cost_data:
        print(f"\nFUND CALCULATION RESULT:")
        print(f"Average Risk-Free Rate: {debt_cost_data['average_risk_free_rate']:.2f}%")
        print(f"Total Debt Cost: ${debt_cost_data['total_debt_cost']:,.2f}")
        print(f"Total Days: {debt_cost_data['total_days']}")
    
    # Compare with 365 days calculation
    print(f"\nCOMPARISON WITH 365 DAYS:")
    print("-" * 40)
    total_debt_cost_365 = 0
    weighted_rfr_sum_365 = 0
    weighted_equity_days_365 = 0
    
    for (equity, rate), data in equity_rate_combinations.items():
        # Recalculate cost using 365 days instead of 365.25
        cost_365 = equity * (rate / 100) * (data['days'] / 365)
        total_debt_cost_365 += cost_365
        weighted_rfr_sum_365 += rate * data['days'] * equity
        weighted_equity_days_365 += data['days'] * equity
    
    avg_rate_365 = weighted_rfr_sum_365 / weighted_equity_days_365 if weighted_equity_days_365 > 0 else 0
    print(f"Using 365 days:")
    print(f"  Total Debt Cost: ${total_debt_cost_365:,.2f}")
    print(f"  Average Risk-Free Rate: {avg_rate_365:.2f}%")
    print(f"  Difference in Rate: {avg_rate_365 - (weighted_rfr_sum / weighted_equity_days):.2f} percentage points")
    print(f"  Difference in Cost: ${total_debt_cost_365 - total_debt_cost:,.2f}")
    
    session.close()

if __name__ == "__main__":
    debug_debt_cost_calculation() 