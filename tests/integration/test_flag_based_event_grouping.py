#!/usr/bin/env python3
"""
Integration tests for flag-based event grouping system.

This test suite verifies the complete workflow from backend event creation
through API responses to frontend data processing.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from src.fund.models import Fund, FundEvent, EventType, DistributionType, TaxPaymentType, GroupType
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from src.api import create_app
from src.tax.models import TaxStatement
from src.tax.events import TaxEventManager


class TestFlagBasedEventGrouping:
    """Test suite for flag-based event grouping integration."""
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        """Set up test environment using conftest.py fixtures."""
        self.session = db_session
        
        # Configure the app to use our test session
        self.app = create_app()
        self.app.config['TEST_DB_SESSION'] = self.session
        self.client = self.app.test_client()
        
        # Create test data with unique names
        self.company = InvestmentCompany(
            name=f"Test Company {id(self)}",
            description="Test company for grouping integration test"
        )
        self.session.add(self.company)
        self.session.commit()
        
        self.entity = Entity(
            name=f"Test Entity {id(self)}",
            description="Test entity for grouping integration test"
        )
        self.session.add(self.entity)
        self.session.commit()
        
        self.fund = Fund(
            name=f"Test Fund {id(self)}",
            description="Test fund for grouping integration test",
            investment_company_id=self.company.id,
            entity_id=self.entity.id,
            fund_type="COST_BASED",
            tracking_type="COST_BASED",
            status="ACTIVE",
            currency="AUD"
        )
        self.session.add(self.fund)
        self.session.commit()
        
        yield
        
        # Cleanup is handled by conftest.py db_session fixture

    def test_tax_statement_event_grouping_workflow(self):
        """Test complete workflow for tax statement event grouping."""
        print("\n🧪 Testing tax statement event grouping workflow...")
        
        # Step 1: Create a tax statement with multiple tax events
        print("  📝 Creating tax statement with multiple tax events...")
        
        # Create tax statement
        tax_statement = TaxStatement(
            fund_id=self.fund.id,
            entity_id=self.entity.id,
            financial_year=2024,
            interest_income_amount=Decimal("1000.00"),
            interest_income_tax_rate=Decimal("32.5"),
            dividend_franked_income_amount=Decimal("500.00"),
            dividend_franked_income_tax_rate=Decimal("32.5"),
            dividend_unfranked_income_amount=Decimal("300.00"),
            dividend_unfranked_income_tax_rate=Decimal("32.5"),
            capital_gain_income_amount=Decimal("200.00"),
            capital_gain_income_tax_rate=Decimal("32.5"),
            eofy_debt_interest_deduction_rate=Decimal("32.5")
        )
        self.session.add(tax_statement)
        self.session.commit()
        
        # Step 2: Create tax events using TaxEventManager (this should trigger grouping)
        print("  🔄 Creating tax events with automatic grouping...")
        created_events = TaxEventManager.create_or_update_tax_events(tax_statement, self.session)
        
        # Step 3: Verify backend grouping logic
        print("  🔍 Verifying backend grouping logic...")
        
        # Get all events for this tax statement
        tax_events = self.session.query(FundEvent).filter(
            FundEvent.tax_statement_id == tax_statement.id
        ).all()
        
        print(f"    📊 Created {len(tax_events)} tax events")
        
        # Check if events are grouped
        grouped_events = [e for e in tax_events if e.is_grouped]
        ungrouped_events = [e for e in tax_events if not e.is_grouped]
        
        if len(tax_events) > 1:
            # Should have grouped events if multiple events exist
            assert len(grouped_events) > 0, "Should have grouped events when multiple events exist"
            
            # All grouped events should have the same group_id and group_type
            group_ids = set(e.group_id for e in grouped_events)
            group_types = set(e.group_type for e in grouped_events)
            
            assert len(group_ids) == 1, "All grouped events should have the same group_id"
            assert len(group_types) == 1, "All grouped events should have the same group_type"
            assert GroupType.TAX_STATEMENT in group_types, "Group type should be TAX_STATEMENT"
            
            # Verify group positions are set correctly
            for event in grouped_events:
                assert event.group_position is not None, "Group position should be set"
                assert event.group_position >= 0, "Group position should be non-negative"
            
            print(f"    ✅ Group ID: {list(group_ids)[0]}")
            print(f"    ✅ Group Type: {list(group_types)[0]}")
            print(f"    ✅ Grouped Events: {len(grouped_events)}")
            print(f"    ✅ Group Positions: {[e.group_position for e in grouped_events]}")
            
            # Verify events are ordered by group position
            sorted_events = sorted(grouped_events, key=lambda e: e.group_position or 0)
            print(f"    ✅ Event Order: {[e.event_type.value for e in sorted_events]}")
            
        else:
            # Single event shouldn't be grouped
            print("    ℹ️  Single event - no grouping applied")
            assert len(grouped_events) == 0, "Single event should not be grouped"
        
        print("    ✅ Tax statement event grouping test passed!")

    def test_interest_withholding_tax_grouping_workflow(self):
        """Test complete workflow for interest + withholding tax grouping."""
        print("\n🧪 Testing interest + withholding tax grouping workflow...")
        
        # Step 1: Create interest distribution with withholding tax
        print("  📝 Creating interest distribution with withholding tax...")
        distribution_event, tax_event = self.fund.add_distribution(
            event_date=date(2024, 1, 15),
            distribution_type=DistributionType.INTEREST,
            gross_interest_amount=Decimal("1000.00"),
            withholding_tax_amount=Decimal("200.00"),
            has_withholding_tax=True,
            reference_number="TEST001",
            session=self.session
        )
        
        # Commit the events so the API can see them
        self.session.commit()
        
        # Step 2: Verify backend grouping logic
        print("  🔍 Verifying backend grouping logic...")
        assert distribution_event.is_grouped, "Distribution event should be grouped"
        assert tax_event.is_grouped, "Tax event should be grouped"
        assert distribution_event.group_id == tax_event.group_id, "Both events should have same group_id"
        assert distribution_event.group_type == GroupType.INTEREST_WITHHOLDING, "Group type should be INTEREST_WITHHOLDING"
        assert tax_event.group_type == GroupType.INTEREST_WITHHOLDING, "Tax event group type should be INTEREST_WITHHOLDING"
        assert distribution_event.group_position == 0, "Distribution should be position 0"
        assert tax_event.group_position == 1, "Tax event should be position 1"
        assert distribution_event.event_date == tax_event.event_date, "Both events should have same date"
        
        print(f"    ✅ Group ID: {distribution_event.group_id}")
        print(f"    ✅ Group Type: {distribution_event.group_type}")
        print(f"    ✅ Distribution Position: {distribution_event.group_position}")
        print(f"    ✅ Tax Event Position: {tax_event.group_position}")
        
        # Step 3: Test API response structure
        print("  🌐 Testing API response structure...")
        response = self.client.get(f"/api/funds/{self.fund.id}")
        assert response.status_code == 200, f"API should return 200, got {response.status_code}"
        
        data = response.get_json()
        assert "events" in data, "API response should include events"
        
        events = data["events"]
        assert len(events) >= 2, f"Should have at least 2 events, got {len(events)}"
        
        # Find our grouped events
        grouped_events = [e for e in events if e.get("is_grouped")]
        assert len(grouped_events) == 2, f"Should have 2 grouped events, got {len(grouped_events)}"
        
        # Verify grouping metadata in API response
        for event in grouped_events:
            assert "is_grouped" in event, "Grouped events should have is_grouped flag"
            assert "group_id" in event, "Grouped events should have group_id"
            assert "group_type" in event, "Grouped events should have group_type"
            assert "group_position" in event, "Grouped events should have group_position"
            assert event["is_grouped"] is True, "is_grouped should be True"
            assert event["group_id"] == distribution_event.group_id, "Group ID should match"
            assert event["group_type"] == "interest_withholding", "Group type should be interest_withholding"
        
        print(f"    ✅ API returned {len(grouped_events)} grouped events")
        print(f"    ✅ All grouped events have proper metadata")
        
        # Step 4: Test frontend data processing simulation
        print("  🎨 Testing frontend data processing simulation...")
        
        # Simulate the useEventGrouping hook logic
        sorted_events = sorted(events, key=lambda e: e["event_date"])
        processed_group_keys = set()
        grouped_events_processed = []
        
        for event in sorted_events:
            if event.get("is_grouped") and event.get("group_id") and event.get("group_type"):
                # Create unique group key (same logic as frontend)
                group_key = f"{event['group_id']}_{event['event_date']}"
                
                if group_key in processed_group_keys:
                    continue
                
                # Find all events in this group
                group_events = [e for e in sorted_events if 
                              e.get("group_id") == event["group_id"] and 
                              e.get("is_grouped") and 
                              e.get("event_date") == event["event_date"]]
                
                # Sort by position
                group_events.sort(key=lambda e: e.get("group_position", 0))
                
                # Create grouped event (simulating frontend logic)
                grouped_event = {
                    "events": group_events,
                    "isGrouped": True,
                    "groupType": event["group_type"],
                    "groupId": event["group_id"],
                    "displayDate": group_events[0]["event_date"],
                    "displayAmount": sum(float(e.get("amount", 0)) for e in group_events),
                    "displayDescription": self._generate_group_description(event["group_type"], group_events)
                }
                
                grouped_events_processed.append(grouped_event)
                processed_group_keys.add(group_key)
        
        # Verify frontend processing worked correctly
        assert len(grouped_events_processed) == 1, f"Should have 1 processed group, got {len(grouped_events_processed)}"
        
        group = grouped_events_processed[0]
        assert group["isGrouped"] is True, "Processed group should be marked as grouped"
        assert group["groupType"] == "interest_withholding", "Group type should be correct"
        assert len(group["events"]) == 2, "Group should have 2 events"
        assert group["displayDate"] == "2024-01-15", "Display date should be correct"
        
        # Verify description formatting
        description = group["displayDescription"]
        assert "Interest Distribution + Withholding Tax" in description, "Description should mention both types"
        assert "1000.00" in description, "Description should include interest amount"
        assert "200.00" in description, "Description should include tax amount"
        
        print(f"    ✅ Frontend processing created {len(grouped_events_processed)} grouped events")
        print(f"    ✅ Group description: {description}")
        
        print("  🎉 All integration tests passed!")
    
    def test_multiple_interest_groups_same_fund(self):
        """Test that multiple interest groups on different dates work correctly."""
        print("\n🧪 Testing multiple interest groups on different dates...")
        
        # Create first group
        dist1, tax1 = self.fund.add_distribution(
            event_date=date(2024, 1, 15),
            distribution_type=DistributionType.INTEREST,
            gross_interest_amount=Decimal("1000.00"),
            withholding_tax_amount=Decimal("200.00"),
            has_withholding_tax=True,
            reference_number="TEST001",
            session=self.session
        )
        
        # Create second group on different date
        dist2, tax2 = self.fund.add_distribution(
            event_date=date(2024, 2, 15),
            distribution_type=DistributionType.INTEREST,
            gross_interest_amount=Decimal("1500.00"),
            withholding_tax_amount=Decimal("300.00"),
            has_withholding_tax=True,
            reference_number="TEST002",
            session=self.session
        )
        
        # Commit the events so the API can see them
        self.session.commit()
        
        # Verify different group IDs
        assert dist1.group_id != dist2.group_id, "Different dates should have different group IDs"
        assert dist1.group_id == tax1.group_id, "Same date events should have same group ID"
        assert dist2.group_id == tax2.group_id, "Same date events should have same group ID"
        
        # Test API response
        response = self.client.get(f"/api/funds/{self.fund.id}")
        assert response.status_code == 200
        
        data = response.get_json()
        events = data["events"]
        
        # Should have 4 grouped events (2 interest + 2 tax)
        grouped_events = [e for e in events if e.get("is_grouped")]
        assert len(grouped_events) == 4, f"Should have 4 grouped events, got {len(grouped_events)}"
        
        # Should have 2 unique group IDs
        unique_group_ids = set(e["group_id"] for e in grouped_events)
        assert len(unique_group_ids) == 2, f"Should have 2 unique groups, got {len(unique_group_ids)}"
        
        print(f"    ✅ Created {len(grouped_events)} grouped events")
        print(f"    ✅ Formed {len(unique_group_ids)} unique groups")
        print("  🎉 Multiple groups test passed!")
    
    def test_non_grouped_events_work_correctly(self):
        """Test that non-grouped events still work correctly."""
        print("\n🧪 Testing non-grouped events...")
        
        # Create a simple capital call (not grouped)
        capital_call = self.fund.add_capital_call(
            amount=Decimal("5000.00"),
            date=date(2024, 1, 20),
            reference_number="TEST003",
            session=self.session
        )
        
        # Commit the event so the API can see it
        self.session.commit()
        
        # Verify it's not grouped
        assert not capital_call.is_grouped, "Capital call should not be grouped"
        assert capital_call.group_id is None, "Non-grouped event should have no group_id"
        assert capital_call.group_type is None, "Non-grouped event should have no group_type"
        assert capital_call.group_position is None, "Non-grouped event should have no group_position"
        
        # Test API response
        response = self.client.get(f"/api/funds/{self.fund.id}")
        assert response.status_code == 200
        
        data = response.get_json()
        events = data["events"]
        
        # Find the capital call
        capital_call_event = next((e for e in events if e["reference_number"] == "TEST003"), None)
        assert capital_call_event is not None, "Capital call should be in API response"
        assert capital_call_event["is_grouped"] is False, "Capital call should not be grouped in API"
        
        print("    ✅ Non-grouped events work correctly")
        print("  🎉 Non-grouped events test passed!")
    
    def _generate_group_description(self, group_type: str, events: list) -> str:
        """Generate group description (same logic as frontend)."""
        if group_type == "interest_withholding":
            # Find events by position
            first_event = next((e for e in events if e.get("group_position") == 0), None)
            second_event = next((e for e in events if e.get("group_position") == 1), None)
            
            if first_event and second_event:
                first_amount = float(first_event.get("amount", 0))
                second_amount = float(second_event.get("amount", 0))
                first_formatted = f"{first_amount:.2f}"
                second_formatted = f"{abs(second_amount):.2f}"
                second_sign = "-" if second_amount < 0 else "+"
                
                return f"Interest Distribution + Withholding Tax ({first_formatted} {second_sign} {second_formatted})"
        
        return "Grouped Events"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
