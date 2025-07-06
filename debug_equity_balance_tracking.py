#!/usr/bin/env python3
"""
Debug script to track equity balance changes over the entire fund duration.
This will help identify where the equity balance calculation differs between old and new versions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Fund, EventType, FundType, RiskFreeRate
from src.shared.calculations import get_equity_change_for_event, get_risk_free_rate_for_date
from datetime import date, timedelta

def debug_equity_balance_tracking():
    """Track equity balance changes for Senior Debt Fund No.24 over its entire duration."""
    
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get the fund
        fund = session.query(Fund).filter(Fund.name == "Senior Debt Fund No.24").first()
        if not fund:
            print("Fund not found!")
            return
        
        print(f"=== Equity Balance Tracking for {fund.name} ===")
        print(f"Fund Type: {fund.tracking_type}")
        print(f"Start Date: {fund.start_date}")
        print(f"End Date: {fund.end_date}")
        print()
        
        # Get all events sorted by date
        events = fund.get_events()
        events.sort(key=lambda e: e.event_date)
        
        # Get risk-free rates
        risk_free_rates = session.query(RiskFreeRate).filter(
            RiskFreeRate.currency == fund.currency,
            RiskFreeRate.rate_date <= fund.end_date
        ).order_by(RiskFreeRate.rate_date).all()
        
        print("=== Event-by-Event Equity Balance Tracking ===")
        current_equity = 0.0
        current_date = fund.start_date
        
        for i, event in enumerate(events):
            print(f"\n--- Event {i+1}: {event.event_type} on {event.event_date} ---")
            print(f"  Amount: ${event.amount:,.2f}" if event.amount else "  Amount: None")
            if hasattr(event, 'units') and event.units:
                print(f"  Units: {event.units:,.6f}")
            
            # Calculate equity change for this event
            equity_change = get_equity_change_for_event(event, fund.tracking_type)
            print(f"  Equity Change: ${equity_change:,.2f}")
            
            # Update current equity
            current_equity += equity_change
            print(f"  New Equity Balance: ${current_equity:,.2f}")
            
            # Show daily risk-free charges until next event
            if i < len(events) - 1:
                next_event_date = events[i + 1].event_date
                daily_charges = []
                
                current_check_date = current_date + timedelta(days=1)
                while current_check_date < next_event_date:
                    rate = get_risk_free_rate_for_date(current_check_date, risk_free_rates)
                    if rate is not None and current_equity > 0:
                        daily_interest = current_equity * (rate / 100) / 365.25
                        daily_charges.append((current_check_date, daily_interest))
                    current_check_date += timedelta(days=1)
                
                if daily_charges:
                    print(f"  Daily Risk-Free Charges ({len(daily_charges)} days):")
                    for charge_date, charge_amount in daily_charges[:5]:  # Show first 5
                        print(f"    {charge_date}: ${charge_amount:,.2f}")
                    if len(daily_charges) > 5:
                        print(f"    ... and {len(daily_charges) - 5} more days")
            
            current_date = event.event_date
        
        print(f"\n=== Final Equity Balance: ${current_equity:,.2f} ===")
        
        # Also show the fund's calculated current_equity_balance
        print(f"=== Fund's Calculated current_equity_balance: ${fund.current_equity_balance:,.2f} ===")
        
        if abs(current_equity - fund.current_equity_balance) > 0.01:
            print(f"WARNING: Manual calculation ({current_equity:,.2f}) differs from fund property ({fund.current_equity_balance:,.2f})")
    
    finally:
        session.close()

if __name__ == "__main__":
    debug_equity_balance_tracking() 