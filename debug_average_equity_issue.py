#!/usr/bin/env python3
"""
Debug script to investigate average equity balance calculation issues.
Focuses on end_date calculation and time period determination.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_database_session
from src.fund.models import Fund, FundEvent, EventType, FundStatus
from datetime import date

def debug_fund_average_equity(fund_id, session):
    """Debug average equity balance calculation for a specific fund."""
    fund = session.query(Fund).filter(Fund.id == fund_id).first()
    if not fund:
        print(f"Fund {fund_id} not found")
        return
    
    print(f"\n=== DEBUGGING FUND: {fund.name} ===")
    print(f"Fund ID: {fund.id}")
    print(f"Status: {fund.status}")
    print(f"End Date: {fund.end_date}")
    print(f"Current Equity Balance: ${fund.current_equity_balance:,.2f}")
    print(f"Average Equity Balance: ${fund.average_equity_balance:,.2f}")
    
    # Get capital events
    if fund.tracking_type.value == 'nav_based':
        event_types = [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]
    else:
        event_types = [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]
    
    events = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.event_type.in_(event_types)
    ).order_by(FundEvent.event_date, FundEvent.id).all()
    
    print(f"\nCapital Events ({len(events)} total):")
    for i, event in enumerate(events):
        print(f"  {i+1}. {event.event_date}: {event.event_type.value} - ${event.amount:,.2f} (equity: ${event.current_equity_balance:,.2f})")
    
    if not events:
        print("  No capital events found")
        return
    
    # Debug the average calculation logic
    print(f"\n=== AVERAGE EQUITY CALCULATION DEBUG ===")
    
    # Check end_date logic
    print(f"hasattr(self, 'end_date'): {hasattr(fund, 'end_date')}")
    print(f"fund.end_date is not None: {fund.end_date is not None}")
    print(f"fund.status == FundStatus.ACTIVE: {fund.status == FundStatus.ACTIVE}")
    
    # Determine period end
    last_event = events[-1]
    period_end = None
    
    if fund.end_date is not None:
        period_end = fund.end_date
        print(f"Using fund end_date: {period_end}")
    elif fund.status == FundStatus.ACTIVE:
        period_end = date.today()
        print(f"Using today's date: {period_end}")
    else:
        print(f"No end_date and not active, using last event date: {last_event.event_date}")
        period_end = last_event.event_date
    
    # Calculate time-weighted average manually
    print(f"\n=== MANUAL CALCULATION ===")
    total_weighted_equity = 0.0
    total_days = 0
    
    for i in range(len(events) - 1):
        e = events[i]
        next_e = events[i + 1]
        days = (next_e.event_date - e.event_date).days
        equity = e.current_equity_balance if e.current_equity_balance is not None else 0.0
        total_weighted_equity += equity * days
        total_days += days
        print(f"  Period {i+1}: {e.event_date} to {next_e.event_date} ({days} days) - Equity: ${equity:,.2f} - Weighted: ${equity * days:,.2f}")
    
    # Include the last period
    if period_end:
        days = (period_end - last_event.event_date).days
        if days >= 0:
            equity = last_event.current_equity_balance if last_event.current_equity_balance is not None else 0.0
            total_weighted_equity += equity * days
            total_days += days
            print(f"  Final Period: {last_event.event_date} to {period_end} ({days} days) - Equity: ${equity:,.2f} - Weighted: ${equity * days:,.2f}")
    
    calculated_average = total_weighted_equity / total_days if total_days > 0 else 0.0
    print(f"\nTotal Weighted Equity: ${total_weighted_equity:,.2f}")
    print(f"Total Days: {total_days}")
    print(f"Calculated Average: ${calculated_average:,.2f}")
    print(f"Stored Average: ${fund.average_equity_balance:,.2f}")
    print(f"Difference: ${calculated_average - fund.average_equity_balance:,.2f}")

def main():
    """Main debug function."""
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Debug each fund
        funds = session.query(Fund).all()
        for fund in funds:
            debug_fund_average_equity(fund.id, session)
            
    finally:
        session.close()

if __name__ == "__main__":
    main() 