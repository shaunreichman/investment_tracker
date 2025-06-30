#!/usr/bin/env python3
"""
Clean up duplicate tax payment events.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import FundEvent, EventType

def cleanup_duplicates():
    """Clean up duplicate tax payment events."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("CLEANING UP DUPLICATE TAX PAYMENT EVENTS")
    print("=" * 60)
    
    # Find all tax payment events
    tax_events = session.query(FundEvent).filter(
        FundEvent.event_type == EventType.TAX_PAYMENT
    ).order_by(FundEvent.fund_id, FundEvent.event_date, FundEvent.amount).all()
    
    print(f"Found {len(tax_events)} tax payment events")
    
    # Group by fund_id, event_date, and amount
    duplicates = []
    seen = set()
    
    for event in tax_events:
        key = (event.fund_id, event.event_date, event.amount, event.description)
        if key in seen:
            duplicates.append(event)
        else:
            seen.add(key)
    
    print(f"Found {len(duplicates)} duplicate events")
    
    # Remove duplicates (keep the first one)
    for event in duplicates:
        print(f"Removing duplicate: {event.event_date} - ${event.amount:,.2f} - {event.description}")
        session.delete(event)
    
    session.commit()
    session.close()
    
    print(f"Cleaned up {len(duplicates)} duplicate events.")

if __name__ == "__main__":
    cleanup_duplicates() 