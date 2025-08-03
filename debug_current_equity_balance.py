#!/usr/bin/env python3
"""
Debug script to check current_equity_balance values on events.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from src.database import get_database_session
from src.fund.models import Fund, FundEvent, EventType, FundType, DistributionType

def debug_current_equity_balance():
    """Debug current_equity_balance values on events."""
    
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Get the first fund
        fund = session.query(Fund).first()
        if not fund:
            print("No funds found")
            return
            
        print(f"=== DEBUGGING CURRENT EQUITY BALANCE FOR {fund.name} ===")
        print(f"Fund type: {fund.tracking_type.value}")
        print(f"Current average equity balance: ${fund.average_equity_balance:,.2f}")
        
        # Get all events ordered by date
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        print(f"\n=== ALL EVENTS ===")
        for i, event in enumerate(events):
            equity_str = f"${event.current_equity_balance:10,.2f}" if event.current_equity_balance is not None else "None"
            print(f"{i+1:2d}. {event.event_date} - {event.event_type.value:20s} - Amount: ${event.amount:10,.2f} - Current Equity: {equity_str:>15}")
        
        # Get only capital events
        if fund.tracking_type == FundType.COST_BASED:
            capital_events = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id,
                FundEvent.event_type.in_([EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL])
            ).order_by(FundEvent.event_date, FundEvent.id).all()
        else:
            capital_events = session.query(FundEvent).filter(
                FundEvent.fund_id == fund.id,
                FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
            ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        print(f"\n=== CAPITAL EVENTS ONLY ===")
        for i, event in enumerate(capital_events):
            equity_str = f"${event.current_equity_balance:10,.2f}" if event.current_equity_balance is not None else "None"
            print(f"{i+1:2d}. {event.event_date} - {event.event_type.value:20s} - Amount: ${event.amount:10,.2f} - Current Equity: {equity_str:>15}")
        
        # Calculate what the average should be
        print(f"\n=== AVERAGE EQUITY CALCULATION ===")
        calculated_average = fund.calculate_average_equity_balance(session=session)
        print(f"Calculated average: ${calculated_average:,.2f}")
        print(f"Stored average: ${fund.average_equity_balance:,.2f}")
        print(f"Difference: ${calculated_average - fund.average_equity_balance:,.2f}")
        
    finally:
        session.close()

if __name__ == "__main__":
    debug_current_equity_balance() 