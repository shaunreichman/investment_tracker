#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType, FundType

def debug_average_calculation(fund_name="3PG Finance"):
    """Debug the average equity balance calculation to show the difference."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get the fund
    fund = session.query(Fund).filter(Fund.name == fund_name).first()
    if not fund:
        print(f"Fund '{fund_name}' not found!")
        return
    
    print(f"DEBUGGING AVERAGE EQUITY CALCULATION FOR: {fund.name}")
    print("=" * 80)
    
    # Get system's calculated average
    system_average = fund.calculate_average_equity_balance(session)
    stored_average = fund.average_equity_balance
    
    print(f"System Average: ${system_average:,.0f}")
    print(f"Stored Average: ${stored_average:,.0f}")
    print()
    
    # Get all equity-changing events
    if fund.tracking_type == FundType.COST_BASED:
        equity_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL])
        ).order_by(FundEvent.event_date).all()
    else:
        equity_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date).all()
    
    print("SYSTEM METHOD CALCULATION (from _calculate_cost_based_average_equity):")
    print("-" * 80)
    print("Period | Equity Balance | Start Date  | End Date    | Days | Weighted Equity")
    print("-" * 80)
    
    # Simulate the system method exactly
    total_weighted_equity = 0
    total_days = 0
    current_equity = 0
    current_date = None
    
    for i, event in enumerate(equity_events):
        # For the first event, start from the event date
        if i == 0:
            current_date = event.event_date
            current_equity += fund._get_equity_change_for_event(event)
            print(f"  {i+1:2d}   | ${current_equity:>8,.0f} | {current_date} | {current_date} | {'':>4} | {'':>12}")
            continue
        
        # Calculate duration of the previous period
        duration_days = (event.event_date - current_date).days
        weighted_equity = current_equity * duration_days
        
        total_weighted_equity += weighted_equity
        total_days += duration_days
        
        print(f"  {i+1:2d}   | ${current_equity:>8,.0f} | {current_date} | {event.event_date} | {duration_days:4d} | ${weighted_equity:>12,.0f}")
        
        # Update equity for next period
        current_equity += fund._get_equity_change_for_event(event)
        current_date = event.event_date
    
    print("-" * 80)
    print(f"TOTAL: | {'':>8} | {'':>10} | {'':>10} | {total_days:4d} | ${total_weighted_equity:>12,.0f}")
    
    system_calculated = total_weighted_equity / total_days if total_days > 0 else 0
    print(f"System Calculated Average: ${system_calculated:,.0f}")
    print()
    
    print("OUR BREAKDOWN SCRIPT METHOD:")
    print("-" * 80)
    print("Period | Equity Balance | Start Date  | End Date    | Days | Weighted Equity")
    print("-" * 80)
    
    # Simulate our breakdown script method
    periods = []
    current_equity = 0
    current_date = fund.start_date
    
    for i, event in enumerate(equity_events):
        # Calculate duration of current period
        if i > 0:
            duration_days = (event.event_date - current_date).days
            periods.append({
                'start_date': current_date,
                'end_date': event.event_date,
                'equity': current_equity,
                'duration_days': duration_days
            })
        
        # Update equity for next period
        equity_change = fund._get_equity_change_for_event(event)
        current_equity += equity_change
        current_date = event.event_date
    
    # Add final period if fund has exited (OUR METHOD INCLUDES THIS)
    if not fund.should_be_active and current_date <= fund.end_date:
        duration_days = (fund.end_date - current_date).days + 1  # Include final day
        periods.append({
            'start_date': current_date,
            'end_date': fund.end_date,
            'equity': current_equity,
            'duration_days': duration_days
        })
    
    # Display periods
    total_weighted_equity_our = 0
    total_days_our = 0
    
    for i, period in enumerate(periods):
        weighted_equity = period['equity'] * period['duration_days']
        total_weighted_equity_our += weighted_equity
        total_days_our += period['duration_days']
        
        print(f"  {i+1:2d}   | ${period['equity']:>8,.0f} | {period['start_date']} | {period['end_date']} | {period['duration_days']:4d} | ${weighted_equity:>12,.0f}")
    
    print("-" * 80)
    print(f"TOTAL: | {'':>8} | {'':>10} | {'':>10} | {total_days_our:4d} | ${total_weighted_equity_our:>12,.0f}")
    
    our_calculated = total_weighted_equity_our / total_days_our if total_days_our > 0 else 0
    print(f"Our Calculated Average: ${our_calculated:,.0f}")
    print()
    
    print("COMPARISON:")
    print("-" * 80)
    print(f"System Method: ${system_calculated:,.0f} ({total_days} days)")
    print(f"Our Method:    ${our_calculated:,.0f} ({total_days_our} days)")
    print(f"Difference:    ${abs(system_calculated - our_calculated):,.2f} ({total_days_our - total_days} extra days)")
    print()
    
    if total_days_our > total_days:
        print("EXPLANATION:")
        print("-" * 80)
        print("The difference is because:")
        print("1. System method: Stops at the last event date")
        print("2. Our method: Includes the final day (2024-04-19) with $0 equity")
        print(f"3. Extra days: {total_days_our - total_days} day(s) with $0 equity")
        print()
        print("The system method is more accurate because:")
        print("- It doesn't include the final day when equity is $0")
        print("- The fund effectively 'exits' on the last event date")
        print("- Including $0 equity days artificially lowers the average")
    
    session.close()

if __name__ == "__main__":
    fund_name = sys.argv[1] if len(sys.argv) > 1 else "3PG Finance"
    debug_average_calculation(fund_name) 