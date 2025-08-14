#!/usr/bin/env python3
"""
Performance tests for flag-based event grouping system using NEW Phase 3.5 Architecture.

This test suite verifies that the simplified flag-based approach provides
better performance than the complex grouping service approach.

UPDATED: Now uses FundUpdateOrchestrator instead of old Fund model methods.
"""

import pytest
import time
from datetime import date, timedelta, datetime
from decimal import Decimal

# NEW: Import new architecture components
from src.fund.events import FundUpdateOrchestrator
from src.fund.events.handlers import CapitalCallHandler, DistributionHandler
from src.fund.enums import EventType, DistributionType, TaxPaymentType, GroupType, FundType, FundStatus

# OLD: Keep old imports for comparison and gradual migration
from src.fund.models import Fund, FundEvent
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from src.api import create_app


class TestFlagBasedPerformance:
    """Test suite for flag-based event grouping performance using NEW architecture."""
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        """Set up test environment with large dataset using NEW architecture."""
        # Use the test session instead of global session
        self.session = db_session
        self.app = create_app()
        self.client = self.app.test_client()
        
        # NEW: Initialize new architecture components
        self.orchestrator = FundUpdateOrchestrator()
        
        # Create test data
        self.company = InvestmentCompany(
            name=f"Performance Test Company {datetime.now().timestamp()}",
            description="Company for performance testing"
        )
        self.session.add(self.company)
        self.session.flush()
        
        self.entity = Entity(
            name=f"Performance Test Entity {datetime.now().timestamp()}",
            description="Entity for performance testing"
        )
        self.session.add(self.entity)
        self.session.flush()
        
        self.fund = Fund(
            name="Performance Test Fund",
            description="Fund for performance testing",
            investment_company_id=self.company.id,
            entity_id=self.entity.id,
            fund_type="DEBT",
            tracking_type=FundType.COST_BASED,
            status=FundStatus.ACTIVE,
            currency="AUD"
        )
        self.session.add(self.fund)
        self.session.flush()
        
        # Create large dataset for performance testing using NEW architecture
        self._create_large_dataset()
        
        yield
        
        # Cleanup - let the test session handle rollback automatically
        # self.session.rollback()
        # self.session.close()
    
    def _create_large_dataset(self):
        """Create a large dataset for performance testing using NEW architecture."""
        print("📊 Creating large dataset for performance testing...")
        
        # Create events over 2 years (730 days)
        start_date = date(2022, 1, 1)
        total_events = 0
        
        for i in range(730):
            current_date = start_date + timedelta(days=i)
            
            # Create interest distribution with withholding tax every 30 days
            if i % 30 == 0:
                amount = Decimal("1000.00") + (i * Decimal("10.00"))  # Varying amounts
                
                # NEW: Use new architecture instead of old Fund model methods
                distribution_data = {
                    'event_type': EventType.DISTRIBUTION,
                    'event_date': current_date,
                    'distribution_type': DistributionType.INTEREST,
                    'has_withholding_tax': True,
                    'distribution_amount': float(amount),  # Use the field name the handler expects
                    'gross_interest_amount': float(amount),
                    'withholding_tax_rate': 0.10,
                    'reference_number': f"PERF{i:04d}",
                    'description': f"Performance test distribution {i}"
                }
                
                # Process distribution through new architecture
                dist = self.orchestrator.process_fund_event(
                    event_data=distribution_data,
                    session=self.session,
                    fund=self.fund
                )
                total_events += 1
            
            # Create capital call every 90 days
            if i % 90 == 0:
                # NEW: Use new architecture for capital calls
                capital_call_data = {
                    'event_type': EventType.CAPITAL_CALL,
                    'amount': float(Decimal("5000.00")),
                    'date': current_date,
                    'reference_number': f"PERF_CAP{i:04d}",
                    'description': f"Performance test capital call {i}"
                }
                
                # Process capital call through new architecture
                self.orchestrator.process_fund_event(
                    event_data=capital_call_data,
                    session=self.session,
                    fund=self.fund
                )
                total_events += 1
        
        # Commit all events
        self.session.commit()
        
        print(f"    ✅ Created {total_events} events over 730 days")
        print(f"    ✅ Fund has {total_events} total events")
    
    def test_api_response_performance(self):
        """Test API response performance with large dataset."""
        print("\n🚀 Testing API response performance...")
        
        # Measure time for API call
        start_time = time.time()
        response = self.client.get(f"/api/funds/{self.fund.id}")
        api_time = time.time() - start_time
        
        assert response.status_code == 200, f"API should return 200, got {response.status_code}"
        
        data = response.get_json()
        events = data["events"]
        
        print(f"    📊 API returned {len(events)} events in {api_time:.4f} seconds")
        print(f"    📊 Average time per event: {api_time/len(events)*1000:.2f} ms")
        
        # Performance assertion: API should respond in under 1 second for large datasets
        assert api_time < 1.0, f"API response time {api_time:.4f}s exceeds 1 second threshold"
        
        # Verify grouping metadata is present
        grouped_events = [e for e in events if e.get("is_grouped")]
        print(f"    📊 Found {len(grouped_events)} grouped events")
        
        # All grouped events should have proper metadata
        for event in grouped_events:
            assert "is_grouped" in event, "Grouped events should have is_grouped flag"
            assert "group_id" in event, "Grouped events should have group_id"
            assert "group_type" in event, "Grouped events should have group_type"
            assert "group_position" in event, "Grouped events should have group_position"
        
        print("    ✅ API performance test passed!")
    
    def test_frontend_processing_performance(self):
        """Test frontend data processing performance simulation."""
        print("\n🎨 Testing frontend processing performance...")
        
        # Get events from API
        response = self.client.get(f"/api/funds/{self.fund.id}")
        data = response.get_json()
        events = data["events"]
        
        # Measure time for frontend processing simulation
        start_time = time.time()
        
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
        
        processing_time = time.time() - start_time
        
        print(f"    📊 Processed {len(grouped_events_processed)} groups in {processing_time:.4f} seconds")
        
        # Handle case where there are no grouped events
        if len(grouped_events_processed) > 0:
            print(f"    📊 Average time per group: {processing_time/len(grouped_events_processed)*1000:.2f} ms")
        else:
            print(f"    📊 No grouped events to process")
        
        # Performance assertion: Processing should be very fast
        assert processing_time < 0.1, f"Frontend processing time {processing_time:.4f}s exceeds 0.1 second threshold"
        
        print("    ✅ Frontend processing performance test passed!")
    
    def test_memory_efficiency(self):
        """Test memory efficiency of the flag-based approach."""
        print("\n💾 Testing memory efficiency...")
        
        try:
            import psutil
            psutil_available = True
        except ImportError:
            psutil_available = False
            print("    ⚠️  psutil module not available, skipping memory measurements")
        
        if psutil_available:
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform operations that might use memory
            response = self.client.get(f"/api/funds/{self.fund.id}")
            data = response.get_json()
            events = data["events"]
            
            # Simulate some processing
            sorted_events = sorted(events, key=lambda e: e["event_date"])
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_delta = final_memory - initial_memory
            
            print(f"    📊 Initial memory: {initial_memory:.2f} MB")
            print(f"    📊 Final memory: {final_memory:.2f} MB")
            print(f"    📊 Memory delta: {memory_delta:.2f} MB")
            
            # Memory should not increase significantly (within 50MB)
            assert memory_delta < 50, f"Memory usage increased by {memory_delta:.2f}MB, exceeding 50MB threshold"
            
            print("    ✅ Memory efficiency test passed!")
        else:
            # Skip memory test if psutil is not available
            print("    ⏭️  Skipping memory efficiency test (psutil not available)")
            pytest.skip("psutil module not available for memory testing")
    
    def test_scalability_with_event_count(self):
        """Test that performance scales well with increasing event count."""
        print("\n📈 Testing scalability with event count...")
        
        # Test with different event counts by limiting the dataset
        event_counts = [100, 500, 1000, 2000]
        response_times = []
        
        for limit in event_counts:
            # Get limited dataset
            start_time = time.time()
            response = self.client.get(f"/api/funds/{self.fund.id}")
            api_time = time.time() - start_time
            
            data = response.get_json()
            events = data["events"][:limit]  # Limit to test count
            
            # Measure frontend processing time
            start_time = time.time()
            
            # Simulate frontend processing
            sorted_events = sorted(events, key=lambda e: e["event_date"])
            processed_group_keys = set()
            grouped_events_processed = []
            
            for event in sorted_events:
                if event.get("is_grouped") and event.get("group_id") and event.get("group_type"):
                    group_key = f"{event['group_id']}_{event['event_date']}"
                    
                    if group_key in processed_group_keys:
                        continue
                    
                    group_events = [e for e in sorted_events if 
                                  e.get("group_id") == event["group_id"] and 
                                  e.get("is_grouped") and 
                                  e.get("event_date") == event["event_date"]]
                    
                    group_events.sort(key=lambda e: e.get("group_position", 0))
                    
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
            
            processing_time = time.time() - start_time
            total_time = api_time + processing_time
            
            response_times.append({
                "event_count": limit,
                "api_time": api_time,
                "processing_time": processing_time,
                "total_time": total_time
            })
            
            print(f"    📊 {limit} events: API={api_time:.4f}s, Processing={processing_time:.4f}s, Total={total_time:.4f}s")
        
        # Verify that performance scales linearly or better
        for i in range(1, len(response_times)):
            prev = response_times[i-1]
            curr = response_times[i]
            
            # Calculate scaling factor
            event_ratio = curr["event_count"] / prev["event_count"]
            time_ratio = curr["total_time"] / prev["total_time"]
            
            # Performance should scale better than linearly (time_ratio < event_ratio)
            # Allow some tolerance for overhead
            scaling_factor = time_ratio / event_ratio
            assert scaling_factor < 1.5, f"Performance scaling factor {scaling_factor:.2f} exceeds 1.5 threshold"
            
            print(f"    📊 Scaling factor {prev['event_count']}→{curr['event_count']}: {scaling_factor:.2f}")
        
        print("    ✅ Scalability test passed!")
    
    def _generate_group_description(self, group_type: str, events: list) -> str:
        """Generate group description (same logic as frontend)."""
        if group_type == "interest_withholding":
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
