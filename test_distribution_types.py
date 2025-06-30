#!/usr/bin/env python3
"""
Test script to demonstrate distribution types with the helper functions.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fund, FundEvent, EventType, DistributionType

def test_distribution_types():
    """Test distribution types with the helper functions."""
    
    # Create database connection
    engine = create_engine('sqlite:///data/investment_tracker.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("TESTING DISTRIBUTION TYPES")
    print("=" * 60)
    
    # Get the first fund for testing
    fund = session.query(Fund).first()
    if not fund:
        print("No funds found for testing.")
        return
    
    print(f"Testing with fund: {fund.name}")
    
    # Test different distribution types
    test_cases = [
        {
            'type': DistributionType.INTEREST,
            'amount': 1000.0,
            'tax': 100.0,
            'description': 'Interest distribution'
        },
        {
            'type': DistributionType.DIVIDEND,
            'amount': 1500.0,
            'tax': 150.0,
            'description': 'Dividend distribution'
        },
        {
            'type': DistributionType.CAPITAL_GAIN,
            'amount': 2000.0,
            'tax': 200.0,
            'description': 'Capital gain distribution'
        },
        {
            'type': DistributionType.RENT,
            'amount': 800.0,
            'tax': 80.0,
            'description': 'Rental income distribution'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['type'].value.upper()} Distribution")
        print("-" * 40)
        
        distribution_event, tax_event = fund.add_distribution_with_tax(
            event_date=date(2024, 12, 10 + i),
            gross_amount=test_case['amount'],
            tax_withheld=test_case['tax'],
            distribution_type=test_case['type'],
            description=test_case['description']
        )
        
        session.commit()
        
        print(f"Created {test_case['type'].value} distribution: ${distribution_event.amount:,.2f}")
        print(f"Distribution type: {distribution_event.distribution_type.value}")
        print(f"Created tax payment: ${tax_event.amount:,.2f}")
        print(f"Net received: ${distribution_event.amount - tax_event.amount:,.2f}")
    
    # Show all distribution events with their types
    print(f"\nAll Distribution Events by Type:")
    print("-" * 60)
    
    distribution_events = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.event_type == EventType.DISTRIBUTION
    ).order_by(FundEvent.event_date).all()
    
    for event in distribution_events:
        dist_type = event.distribution_type.value if event.distribution_type else "UNSPECIFIED"
        print(f"{event.event_date}: ${event.amount:,.2f} - {dist_type.upper()} - {event.description}")
    
    # Show summary by distribution type
    print(f"\nSummary by Distribution Type:")
    print("-" * 40)
    
    from sqlalchemy import func
    summary = session.query(
        FundEvent.distribution_type,
        func.sum(FundEvent.amount).label('total_amount'),
        func.count(FundEvent.id).label('count')
    ).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.event_type == EventType.DISTRIBUTION
    ).group_by(FundEvent.distribution_type).all()
    
    for row in summary:
        dist_type = row.distribution_type.value if row.distribution_type else "UNSPECIFIED"
        print(f"{dist_type.upper()}: ${row.total_amount:,.2f} ({row.count} events)")
    
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
        FundEvent.description.like('Interest distribution') |
        FundEvent.description.like('Dividend distribution') |
        FundEvent.description.like('Capital gain distribution') |
        FundEvent.description.like('Rental income distribution')
    ).all()
    
    for event in test_events:
        session.delete(event)
        print(f"Deleted: {event.event_type} - {event.event_date} - ${event.amount:,.2f} - {event.distribution_type.value if event.distribution_type else 'UNSPECIFIED'}")
    
    session.commit()
    session.close()
    
    print(f"Cleaned up {len(test_events)} test events.")

if __name__ == "__main__":
    test_distribution_types()
    
    # Ask if user wants to clean up
    response = input("\nDo you want to clean up the test events? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        cleanup_test_events() 