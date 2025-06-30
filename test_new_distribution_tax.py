#!/usr/bin/env python3
"""
Test script to demonstrate the new distribution with tax functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType

def test_new_distribution_tax():
    """Test the new distribution with tax functionality."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("TESTING NEW DISTRIBUTION WITH TAX FUNCTIONALITY")
    print("=" * 60)
    
    # Get the first fund for testing
    fund = session.query(Fund).first()
    if not fund:
        print("No funds found for testing.")
        return
    
    print(f"Testing with fund: {fund.name}")
    
    # Test 1: Add distribution with tax withheld
    print(f"\nTest 1: Add distribution with tax withheld")
    print("-" * 40)
    
    distribution_event, tax_event = fund.add_distribution_with_tax(
        event_date=date(2024, 12, 15),
        gross_amount=5000.0,
        tax_withheld=500.0,
        description="Test distribution with tax withheld"
    )
    
    session.commit()
    
    print(f"Created distribution: ${distribution_event.amount:,.2f}")
    print(f"Created tax payment: ${tax_event.amount:,.2f}")
    print(f"Net received: ${distribution_event.amount - tax_event.amount:,.2f}")
    
    # Test 2: Add distribution with tax rate
    print(f"\nTest 2: Add distribution with tax rate")
    print("-" * 40)
    
    distribution_event2, tax_event2 = fund.add_distribution_with_tax_rate(
        event_date=date(2024, 12, 20),
        gross_amount=3000.0,
        tax_rate=10.0,  # 10% tax rate
        description="Test distribution with 10% tax rate"
    )
    
    session.commit()
    
    print(f"Created distribution: ${distribution_event2.amount:,.2f}")
    print(f"Created tax payment: ${tax_event2.amount:,.2f}")
    print(f"Tax rate applied: 10.0%")
    print(f"Net received: ${distribution_event2.amount - tax_event2.amount:,.2f}")
    
    # Test 3: Add distribution without tax
    print(f"\nTest 3: Add distribution without tax")
    print("-" * 40)
    
    distribution_event3, tax_event3 = fund.add_distribution_with_tax(
        event_date=date(2024, 12, 25),
        gross_amount=2000.0,
        tax_withheld=0.0,
        description="Test distribution without tax"
    )
    
    session.commit()
    
    print(f"Created distribution: ${distribution_event3.amount:,.2f}")
    print(f"Tax payment created: {tax_event3 is not None}")
    
    # Show all events for this fund
    print(f"\nAll events for {fund.name}:")
    print("-" * 40)
    
    events = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id
    ).order_by(FundEvent.event_date).all()
    
    for event in events:
        if event.event_type == EventType.DISTRIBUTION:
            print(f"Distribution: {event.event_date} - ${event.amount:,.2f} - {event.description}")
        elif event.event_type == EventType.TAX_PAYMENT:
            print(f"Tax Payment:  {event.event_date} - ${event.amount:,.2f} - {event.description}")
        else:
            print(f"{event.event_type}: {event.event_date} - ${event.amount:,.2f} - {event.description}")
    
    # Calculate IRRs
    print(f"\nIRR Calculations:")
    print("-" * 40)
    print(f"Gross IRR: {fund.get_irr_percentage(session)}")
    print(f"After-Tax IRR: {fund.get_after_tax_irr_percentage(session)}")
    
    session.close()

def cleanup_test_events():
    """Clean up the test events we created."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"\nCleaning up test events...")
    
    # Remove test events
    test_events = session.query(FundEvent).filter(
        FundEvent.description.like("Test%")
    ).all()
    
    for event in test_events:
        session.delete(event)
        print(f"Deleted: {event.event_type} - {event.event_date} - ${event.amount:,.2f}")
    
    session.commit()
    session.close()
    
    print(f"Cleaned up {len(test_events)} test events.")

if __name__ == "__main__":
    test_new_distribution_tax()
    
    # Ask if user wants to clean up
    response = input("\nDo you want to clean up the test events? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        cleanup_test_events() 