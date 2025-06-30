#!/usr/bin/env python3
"""
Check events for Senior Debt Fund No.24
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType

def check_events():
    """Check all events for Senior Debt Fund No.24."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get the fund
    fund = session.query(Fund).filter(Fund.name=='Senior Debt Fund No.24').first()
    if not fund:
        print("Fund not found!")
        return
    
    print(f"EVENTS FOR: {fund.name}")
    print("=" * 80)
    print("ID | Date       | Event Type        | Amount    | Tax Rate | Tax Amount | Description")
    print("-" * 80)
    
    # Get all events ordered by date
    events = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id
    ).order_by(FundEvent.event_date, FundEvent.id).all()
    
    for event in events:
        print(f"{event.id:>2} | {event.event_date} | {event.event_type:<16} | ${event.amount:>8,.2f} | {event.tax_withholding_rate:>8.1f}% | ${event.tax_withheld:>9,.2f} | {event.description}")
    
    print("-" * 80)
    print(f"Total events: {len(events)}")
    
    # Check for duplicates
    print("\nDUPLICATE CHECK:")
    print("-" * 80)
    
    # Group events by date and type
    event_groups = {}
    for event in events:
        key = (event.event_date, event.event_type)
        if key not in event_groups:
            event_groups[key] = []
        event_groups[key].append(event)
    
    duplicates_found = False
    for key, group in event_groups.items():
        if len(group) > 1:
            duplicates_found = True
            print(f"DUPLICATES on {key[0]} - {key[1]}:")
            for event in group:
                print(f"  ID {event.id}: ${event.amount:,.2f} (Tax: {event.tax_withholding_rate}%, ${event.tax_withheld:,.2f})")
    
    if not duplicates_found:
        print("No exact duplicates found.")
    
    session.close()

if __name__ == "__main__":
    check_events() 