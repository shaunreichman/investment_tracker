#!/usr/bin/env python3
"""
Debug script to test the calculate_average_equity_balance method directly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from src.database import get_database_session
from src.fund.models import Fund, FundEvent, EventType, FundType, DistributionType

def debug_average_calculation():
    """Debug the calculate_average_equity_balance method directly."""
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Get the first fund
        fund = session.query(Fund).first()
        if not fund:
            print("No funds found")
            return
            
        print(f"=== DEBUGGING AVERAGE EQUITY CALCULATION FOR {fund.name} ===")
        
        # Get capital events
        capital_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL])
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        print(f"\n=== CAPITAL EVENTS ===")
        for i, event in enumerate(capital_events):
            equity_str = f"${event.current_equity_balance:10,.2f}" if event.current_equity_balance is not None else "None"
            print(f"{i+1:2d}. {event.event_date} - {event.event_type.value:20s} - Amount: ${event.amount:10,.2f} - Current Equity: {equity_str:>15}")
        
        # Test the calculation method
        print(f"\n=== CALCULATION TEST ===")
        calculated_avg = fund.calculate_average_equity_balance(session=session)
        stored_avg = fund.average_equity_balance
        print(f"Calculated average: ${calculated_avg:,.2f}")
        print(f"Stored average: ${stored_avg:,.2f}")
        print(f"Difference: ${calculated_avg - stored_avg:,.2f}")
        
        # Manual calculation for verification
        print(f"\n=== MANUAL CALCULATION ===")
        if len(capital_events) >= 2:
            total_weighted_equity = 0.0
            total_days = 0
            
            for i in range(len(capital_events) - 1):
                e = capital_events[i]
                next_e = capital_events[i + 1]
                days = (next_e.event_date - e.event_date).days
                equity = e.current_equity_balance if e.current_equity_balance is not None else 0.0
                weighted_equity = equity * days
                total_weighted_equity += weighted_equity
                total_days += days
                print(f"Period {i+1}: ${equity:,.2f} × {days} days = ${weighted_equity:,.2f}")
            
            # Last period
            last_event = capital_events[-1]
            if fund.end_date:
                days = (fund.end_date - last_event.event_date).days
                equity = last_event.current_equity_balance if last_event.current_equity_balance is not None else 0.0
                weighted_equity = equity * days
                total_weighted_equity += weighted_equity
                total_days += days
                print(f"Last period: ${equity:,.2f} × {days} days = ${weighted_equity:,.2f}")
            
            manual_avg = total_weighted_equity / total_days if total_days > 0 else 0.0
            print(f"Manual average: ${manual_avg:,.2f}")
            print(f"Total weighted equity: ${total_weighted_equity:,.2f}")
            print(f"Total days: {total_days}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    debug_average_calculation() 