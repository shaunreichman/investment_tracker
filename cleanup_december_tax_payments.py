#!/usr/bin/env python3
"""
Script to delete December 2024 tax payment events from Senior Debt Fund No.24.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType

def delete_december_2024_tax_payments():
    """Delete December 2024 tax payment events from Senior Debt Fund No.24."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("DELETING DECEMBER 2024 TAX PAYMENT EVENTS")
    print("=" * 60)
    
    # Find Senior Debt Fund No.24
    fund = session.query(Fund).filter(Fund.name == "Senior Debt Fund No.24").first()
    if not fund:
        print("Senior Debt Fund No.24 not found!")
        session.close()
        return
    
    print(f"Found fund: {fund.name} (ID: {fund.id})")
    
    # Find December 2024 tax payment events
    december_events = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.event_type == EventType.TAX_PAYMENT,
        FundEvent.event_date >= date(2024, 12, 1),
        FundEvent.event_date <= date(2024, 12, 31)
    ).order_by(FundEvent.event_date).all()
    
    if not december_events:
        print("No December 2024 tax payment events found.")
        session.close()
        return
    
    print(f"\nFound {len(december_events)} December 2024 tax payment events:")
    print("-" * 50)
    
    total_amount = 0
    for event in december_events:
        print(f"  {event.event_date}: ${event.amount:,.2f} - {event.description}")
        total_amount += event.amount
    
    print(f"\nTotal amount to be deleted: ${total_amount:,.2f}")
    
    # Delete the events (no confirmation required)
    print("\nDeleting events...")
    for event in december_events:
        session.delete(event)
        print(f"Deleted: {event.event_date} - ${event.amount:,.2f}")
    
    # Commit the changes
    session.commit()
    print(f"\nSuccessfully deleted {len(december_events)} events.")
    
    # Verify deletion
    remaining_events = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.event_type == EventType.TAX_PAYMENT,
        FundEvent.event_date >= date(2024, 12, 1),
        FundEvent.event_date <= date(2024, 12, 31)
    ).count()
    
    print(f"Remaining December 2024 tax payment events: {remaining_events}")
    
    # Show updated IRR calculations
    print(f"\nUPDATED IRR CALCULATIONS:")
    print("-" * 30)
    print(f"Gross IRR:         {fund.get_irr_percentage(session)}")
    print(f"After-Tax IRR:     {fund.get_after_tax_irr_percentage(session)}")
    
    gross_irr = fund.calculate_irr(session)
    after_tax_irr = fund.calculate_after_tax_irr(session)
    
    if gross_irr is not None and after_tax_irr is not None:
        difference = gross_irr - after_tax_irr
        percentage_impact = (difference / gross_irr * 100) if gross_irr != 0 else 0
        print(f"Tax Impact:        {difference:.2f} percentage points ({percentage_impact:.1f}%)")
    
    session.close()

if __name__ == "__main__":
    delete_december_2024_tax_payments() 