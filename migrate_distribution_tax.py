#!/usr/bin/env python3
"""
Migration script to separate tax withholding from distribution events.
Converts distribution events with tax withholding into separate distribution + tax payment events.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import FundEvent, EventType

def migrate_distribution_tax():
    """Migrate distribution events to separate tax withholding."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("MIGRATING DISTRIBUTION TAX WITHHOLDING")
    print("=" * 60)
    
    # Find all distribution events with tax withholding
    distribution_events = session.query(FundEvent).filter(
        FundEvent.event_type == EventType.DISTRIBUTION,
        FundEvent.tax_withheld > 0
    ).all()
    
    print(f"Found {len(distribution_events)} distribution events with tax withholding")
    
    for event in distribution_events:
        print(f"\nProcessing: {event.event_date} - ${event.amount:,.2f} (tax: ${event.tax_withheld:,.2f})")
        
        # Store the tax amount before clearing it
        tax_amount = event.tax_withheld
        
        # Create tax payment event
        tax_event = FundEvent(
            fund_id=event.fund_id,
            event_type=EventType.TAX_PAYMENT,
            event_date=event.event_date,
            amount=tax_amount,
            description=f"Tax withheld on distribution",
            reference_number=f"TAX-WITHHELD-{event.id}"
        )
        
        # Add the tax event
        session.add(tax_event)
        
        # Clear tax withholding from the distribution event
        event.tax_withheld = 0.0
        event.tax_withholding_rate = 0.0
        
        print(f"  Created tax payment event: ${tax_amount:,.2f}")
        print(f"  Cleared tax withholding from distribution")
    
    # Commit all changes
    session.commit()
    
    print(f"\nMigration completed! Processed {len(distribution_events)} events.")
    
    # Verify the migration
    remaining_tax_withheld = session.query(FundEvent).filter(
        FundEvent.event_type == EventType.DISTRIBUTION,
        FundEvent.tax_withheld > 0
    ).count()
    
    print(f"Remaining distribution events with tax withholding: {remaining_tax_withheld}")
    
    # Count new tax payment events
    tax_payment_events = session.query(FundEvent).filter(
        FundEvent.event_type == EventType.TAX_PAYMENT
    ).count()
    
    print(f"Total tax payment events: {tax_payment_events}")
    
    session.close()

if __name__ == "__main__":
    migrate_distribution_tax() 