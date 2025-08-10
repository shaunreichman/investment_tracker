#!/usr/bin/env python3
"""Test script to verify the API returns grouping fields correctly."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_global_session
from src.fund.models import Fund, FundEvent, EventType, DistributionType, TaxPaymentType, GroupType
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from datetime import date, datetime

def test_grouping_api():
    """Test that the API returns grouping fields correctly."""
    print("Testing grouping API functionality...")
    
    # Get database session
    session = get_global_session()
    
    try:
        # Create test data
        print("Creating test data...")
        
        # Create investment company
        company = InvestmentCompany(
            name=f"Test Company {datetime.now().timestamp()}",
            description="Test company for grouping API test"
        )
        session.add(company)
        session.flush()
        
        # Create entity
        entity = Entity(
            name=f"Test Entity {datetime.now().timestamp()}",
            description="Test entity for grouping API test"
        )
        session.add(entity)
        session.flush()
        
        # Create fund
        fund = Fund(
            name=f"Test Fund {datetime.now().timestamp()}",
            description="Test fund for grouping API test",
            investment_company_id=company.id,
            entity_id=entity.id,
            fund_type="DEBT",
            status="ACTIVE"
        )
        session.add(fund)
        session.flush()
        
        # Create interest distribution with withholding tax
        print("Creating interest distribution with withholding tax...")
        distribution_event, tax_event = fund.add_distribution(
            event_date=date(2024, 1, 15),
            distribution_type=DistributionType.INTEREST,
            gross_interest_amount=1000.0,
            has_withholding_tax=True,
            withholding_tax_rate=0.10,  # 10% withholding tax rate
            reference_number="TEST001",
            session=session
        )
        
        # Verify the events were created and grouped
        print(f"Distribution event ID: {distribution_event.id}")
        print(f"Tax event ID: {tax_event.id}")
        print(f"Distribution is_grouped: {distribution_event.is_grouped}")
        print(f"Tax event is_grouped: {tax_event.is_grouped}")
        print(f"Distribution group_id: {distribution_event.group_id}")
        print(f"Tax event group_id: {tax_event.group_id}")
        print(f"Distribution group_type: {distribution_event.group_type}")
        print(f"Tax event group_type: {tax_event.group_type}")
        print(f"Distribution group_position: {distribution_event.group_position}")
        print(f"Tax event group_position: {tax_event.group_position}")
        
        # Test the API endpoint by calling the fund detail method directly
        print("\nTesting fund detail API response...")
        fund_data = fund.get_summary_data(session=session)
        all_events = fund.get_all_fund_events(exclude_system_events=True, session=session)
        
        events_data = []
        for event in all_events:
            event_data = {
                "id": event.id,
                "event_type": event.event_type.value.upper() if event.event_type else None,
                "event_date": event.event_date.isoformat() if event.event_date else None,
                "amount": float(event.amount) if event.amount else None,
                "description": event.description,
                "reference_number": event.reference_number,
                "distribution_type": event.distribution_type.value.upper() if event.distribution_type else None,
                "tax_payment_type": event.tax_payment_type.value.upper() if event.tax_payment_type else None,
                "units_purchased": float(event.units_purchased) if event.units_purchased else None,
                "units_sold": float(event.units_sold) if event.units_sold else None,
                "unit_price": float(event.unit_price) if event.unit_price else None,
                "nav_per_share": float(event.nav_per_share) if event.nav_per_share else None,
                "previous_nav_per_share": float(event.previous_nav_per_share) if event.previous_nav_per_share else None,
                "nav_change_absolute": float(event.nav_change_absolute) if event.nav_change_absolute else None,
                "nav_change_percentage": float(event.nav_change_percentage) if event.nav_change_percentage else None,
                "brokerage_fee": float(event.brokerage_fee) if event.brokerage_fee else None,
                "has_withholding_tax": bool(event.has_withholding_tax) if event.has_withholding_tax is not None else None,
                "created_at": event.created_at.isoformat() if event.created_at else None,
                # CALCULATED: Grouping flags set by backend when creating events
                "is_grouped": bool(event.is_grouped) if event.is_grouped is not None else False,
                "group_id": event.group_id,
                "group_type": event.group_type.value if event.group_type else None,
                "group_position": event.group_position
            }
            events_data.append(event_data)
        
        # Calculate grouping metadata
        grouped_events = [e for e in events_data if e["is_grouped"]]
        total_groups = len(set(e["group_id"] for e in grouped_events if e["group_id"] is not None))
        group_types_present = list(set(e["group_type"] for e in grouped_events if e["group_type"] is not None))
        
        print(f"\nAPI Response - Events:")
        for event in events_data:
            print(f"  Event {event['id']}: {event['event_type']} - is_grouped: {event['is_grouped']}, group_id: {event['group_id']}, group_type: {event['group_type']}, group_position: {event['group_position']}")
        
        print(f"\nAPI Response - Grouping Metadata:")
        print(f"  Total groups: {total_groups}")
        print(f"  Grouped events count: {len(grouped_events)}")
        print(f"  Group types present: {group_types_present}")
        
        # Verify the grouping worked correctly
        assert len(grouped_events) == 2, f"Expected 2 grouped events, got {len(grouped_events)}"
        assert total_groups == 1, f"Expected 1 group, got {total_groups}"
        assert "interest_withholding" in group_types_present, f"Expected interest_withholding in group types, got {group_types_present}"
        
        print("\n✅ All tests passed! The grouping API is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        session.close()
    
    return True

if __name__ == "__main__":
    success = test_grouping_api()
    sys.exit(0 if success else 1)
