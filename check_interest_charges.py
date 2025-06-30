#!/usr/bin/env python3
"""
Check daily interest charge events to verify they're using the correct risk-free rates.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import FundEvent, EventType, RiskFreeRate

def check_interest_charges():
    """Check daily interest charge events."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("CHECKING DAILY INTEREST CHARGE EVENTS")
    print("=" * 50)
    
    # Get all daily interest charge events
    events = session.query(FundEvent).filter(
        FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
    ).order_by(FundEvent.event_date).all()
    
    print(f"Found {len(events)} daily interest charge events")
    
    # Show first 10 events
    print("\nFirst 10 events:")
    for i, event in enumerate(events[:10]):
        print(f"  {event.event_date}: ${event.amount:.4f} - {event.description}")
    
    # Show last 10 events
    print("\nLast 10 events:")
    for i, event in enumerate(events[-10:]):
        print(f"  {event.event_date}: ${event.amount:.4f} - {event.description}")
    
    # Check if rates match
    print("\nVerifying rates match database:")
    sample_events = events[::len(events)//10]  # Sample every 10th event
    for event in sample_events[:5]:
        # Get the rate for this date from the database
        rate = session.query(RiskFreeRate).filter(
            RiskFreeRate.currency == 'AUD',
            RiskFreeRate.rate_date <= event.event_date
        ).order_by(RiskFreeRate.rate_date.desc()).first()
        
        if rate:
            print(f"  {event.event_date}: Event uses {event.description.split('(')[1].split('%')[0]}%, DB has {rate.rate}%")
        else:
            print(f"  {event.event_date}: No rate found in DB")
    
    session.close()

if __name__ == "__main__":
    check_interest_charges() 