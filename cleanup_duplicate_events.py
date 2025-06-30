#!/usr/bin/env python3
"""
Clean up duplicate events by removing the ones without tax withholding
and keeping the ones with tax withholding.
Also handles exact duplicates (same amount, date, type).
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType

def cleanup_duplicate_events():
    """Clean up duplicate events for Senior Debt Fund No.24."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get the fund
    fund = session.query(Fund).filter(Fund.name=='Senior Debt Fund No.24').first()
    if not fund:
        print("Fund not found!")
        return
    
    print(f"CLEANING DUPLICATE EVENTS FOR: {fund.name}")
    print("=" * 80)
    
    # Get all distribution events
    distribution_events = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.event_type == EventType.DISTRIBUTION
    ).order_by(FundEvent.event_date, FundEvent.id).all()
    
    print("Current distribution events:")
    print("-" * 80)
    for event in distribution_events:
        print(f"ID {event.id}: {event.event_date} - ${event.amount:,.2f} (Tax: {event.tax_withholding_rate}%, ${event.tax_withheld:,.2f})")
    
    # Group events by date
    event_groups = {}
    for event in distribution_events:
        if event.event_date not in event_groups:
            event_groups[event.event_date] = []
        event_groups[event.event_date].append(event)
    
    # Remove duplicates
    events_to_delete = []
    for date, events in event_groups.items():
        if len(events) > 1:
            print(f"\nFound duplicates on {date}:")
            for event in events:
                print(f"  ID {event.id}: ${event.amount:,.2f} (Tax: {event.tax_withholding_rate}%, ${event.tax_withheld:,.2f})")
            
            # If there are events with and without tax, keep the ones with tax
            events_with_tax = [e for e in events if e.tax_withholding_rate > 0]
            events_without_tax = [e for e in events if e.tax_withholding_rate == 0]
            
            if events_with_tax and events_without_tax:
                print(f"  Keeping ID {events_with_tax[0].id} (with tax), deleting ID {events_without_tax[0].id} (without tax)")
                events_to_delete.append(events_without_tax[0])
            else:
                # All events have the same tax status, keep the first one, delete the rest
                print(f"  All events have same tax status, keeping ID {events[0].id}, deleting the rest")
                events_to_delete.extend(events[1:])
    
    # Delete the duplicate events
    if events_to_delete:
        print(f"\nDeleting {len(events_to_delete)} duplicate events...")
        for event in events_to_delete:
            session.delete(event)
            print(f"  Deleted ID {event.id}")
        
        session.commit()
        print("Cleanup completed!")
    else:
        print("\nNo duplicates to clean up.")
    
    # Show final state
    print("\nFinal distribution events:")
    print("-" * 80)
    final_events = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.event_type == EventType.DISTRIBUTION
    ).order_by(FundEvent.event_date, FundEvent.id).all()
    
    for event in final_events:
        print(f"ID {event.id}: {event.event_date} - ${event.amount:,.2f} (Tax: {event.tax_withholding_rate}%, ${event.tax_withheld:,.2f})")
    
    session.close()

if __name__ == "__main__":
    cleanup_duplicate_events() 