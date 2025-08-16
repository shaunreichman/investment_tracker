"""
Phase 4.5 Performance Validation Tests.

This module provides comprehensive performance testing of the event-driven system
to ensure that loose coupling and event consumption don't introduce performance issues.
"""

import pytest
import time
from datetime import date, datetime
from sqlalchemy.orm import Session

from src.fund.models import Fund, FundEvent, FundType, FundStatus, EventType
from src.fund.events.consumption.event_bus import event_bus
from src.fund.events.orchestrator import FundUpdateOrchestrator
from src.fund.events.registry import FundEventHandlerRegistry
from src.fund.events.domain import (
    EquityBalanceChangedEvent,
    DistributionRecordedEvent,
    NAVUpdatedEvent,
    TaxStatementUpdatedEvent,
    FundSummaryUpdatedEvent
)
from tests.factories import (
    FundFactory, FundEventFactory, TaxStatementFactory,
    InvestmentCompanyFactory, EntityFactory
)


class TestPhase45PerformanceValidation:
    """
    Performance validation tests for Phase 4.5 event-driven architecture.
    
    These tests ensure that the loose coupling architecture maintains
    performance characteristics and doesn't introduce bottlenecks.
    """
    
    def test_event_publishing_performance(self, db_session: Session):
        """
        Test performance of event publishing system.
        
        This validates that publishing events doesn't introduce
        performance bottlenecks.
        """
        import time
        
        # Setup test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED
        )
        
        # Measure time to publish multiple events
        start_time = time.time()
        
        # Publish 100 events
        for i in range(100):
            equity_event = EquityBalanceChangedEvent(
                fund_id=fund.id,
                event_date=date.today(),
                old_balance=float(i * 1000),
                new_balance=float((i + 1) * 1000),
                change_reason=f"Performance test {i}"
            )
            event_bus.publish(equity_event)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance is acceptable
        # 100 events should complete in under 0.1 seconds
        assert total_time < 0.1, f"Event publishing too slow: {total_time:.4f}s for 100 events"
        
        # Verify all events were published
        stats = event_bus.get_stats()
        assert stats['events_published'] >= 100
        
        print(f"✅ Event publishing performance: {100} events in {total_time:.4f}s ({100/total_time:.0f} events/sec)")
    
    def test_event_consumption_performance(self, db_session: Session):
        """
        Test performance of event consumption system.
        
        This validates that consuming events doesn't introduce
        performance bottlenecks.
        """
        import time
        
        # Setup test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED
        )
        
        # Register handlers for performance testing
        from src.fund.events.consumption.handlers.tax_statement_event_handler import TaxStatementEventHandler
        from src.fund.events.consumption.handlers.company_record_event_handler import CompanyRecordEventHandler
        
        tax_handler = TaxStatementEventHandler()
        company_handler = CompanyRecordEventHandler()
        
        event_bus.subscribe_consumer(EquityBalanceChangedEvent, tax_handler)
        event_bus.subscribe_consumer(EquityBalanceChangedEvent, company_handler)
        event_bus.subscribe_consumer(FundSummaryUpdatedEvent, company_handler)
        
        # Measure time to publish and consume events
        start_time = time.time()
        
        # Publish and consume 50 events
        for i in range(50):
            equity_event = EquityBalanceChangedEvent(
                fund_id=fund.id,
                event_date=date.today(),
                old_balance=float(i * 1000),
                new_balance=float((i + 1) * 1000),
                change_reason=f"Performance test {i}"
            )
            event_bus.publish(equity_event)
            
            summary_event = FundSummaryUpdatedEvent(
                fund_id=fund.id,
                event_date=date.today(),
                summary_type="PERFORMANCE_TEST"
            )
            event_bus.publish(summary_event)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance is acceptable
        # 100 total events (50 equity + 50 summary) should complete in under 0.2 seconds
        assert total_time < 0.2, f"Event consumption too slow: {total_time:.4f}s for 100 events"
        
        # Verify all events were processed
        stats = event_bus.get_stats()
        assert stats['events_published'] >= 100
        assert stats['events_processed'] >= 100
        
        print(f"✅ Event consumption performance: {100} events in {total_time:.4f}s ({100/total_time:.0f} events/sec)")
    
    def test_orchestrator_performance(self, db_session: Session):
        """
        Test performance of the orchestrator system.
        
        This validates that the complete event processing pipeline
        maintains performance characteristics.
        """
        import time
        
        # Setup test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED
        )
        
        # Create orchestrator
        registry = FundEventHandlerRegistry()
        orchestrator = FundUpdateOrchestrator(registry=registry)
        
        # Measure time to process multiple events through orchestrator
        start_time = time.time()
        
        # Process 20 events through orchestrator
        for i in range(20):
            event_data = {
                "event_type": EventType.CAPITAL_CALL,
                "amount": 10000.0 + (i * 1000),
                "date": date.today(),
                "description": f"Performance test capital call {i}"
            }
            
            event = orchestrator.process_fund_event(event_data, db_session, fund)
            assert event.id is not None
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance is acceptable
        # 20 orchestrator events should complete in under 2 seconds
        assert total_time < 2.0, f"Orchestrator too slow: {total_time:.4f}s for 20 events"
        
        print(f"✅ Orchestrator performance: {20} events in {total_time:.4f}s ({20/total_time:.1f} events/sec)")
    
    def test_memory_usage_performance(self, db_session: Session):
        """
        Test memory usage of the event-driven system.
        
        This validates that the event system doesn't introduce
        memory leaks or excessive memory usage.
        """
        import psutil
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Setup test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED
        )
        
        # Perform intensive event operations
        for i in range(100):
            equity_event = EquityBalanceChangedEvent(
                fund_id=fund.id,
                event_date=date.today(),
                old_balance=float(i * 100),
                new_balance=float((i + 1) * 100),
                change_reason=f"Memory test {i}"
            )
            event_bus.publish(equity_event)
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Check final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verify memory increase is reasonable
        # Should not increase by more than 50MB for 100 events
        assert memory_increase < 50.0, f"Memory usage too high: {memory_increase:.1f}MB increase"
        
        print(f"✅ Memory usage performance: {memory_increase:.1f}MB increase for 100 events")
    
    def test_concurrent_event_processing(self, db_session: Session):
        """
        Test performance under concurrent event processing.
        
        This validates that the system can handle multiple
        events concurrently without performance degradation.
        """
        import time
        import threading
        
        # Setup test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED
        )
        
        # Function to publish events in a thread
        def publish_events(thread_id, count):
            for i in range(count):
                equity_event = EquityBalanceChangedEvent(
                    fund_id=fund.id,
                    event_date=date.today(),
                    old_balance=float(i * 100),
                    new_balance=float((i + 1) * 100),
                    change_reason=f"Thread {thread_id} event {i}"
                )
                event_bus.publish(equity_event)
        
        # Measure time with concurrent processing
        start_time = time.time()
        
        # Create 5 threads, each publishing 20 events
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=publish_events, args=(thread_id, 20))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance is acceptable
        # 100 concurrent events should complete in under 0.5 seconds
        assert total_time < 0.5, f"Concurrent processing too slow: {total_time:.4f}s for 100 events"
        
        # Verify all events were published
        stats = event_bus.get_stats()
        assert stats['events_published'] >= 100
        
        print(f"✅ Concurrent processing performance: {100} events in {total_time:.4f}s ({100/total_time:.0f} events/sec)")
    
    def test_large_scale_event_processing(self, db_session: Session):
        """
        Test performance with large-scale event processing.
        
        This validates that the system can handle realistic
        production loads without performance degradation.
        """
        import time
        
        # Setup test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED
        )
        
        # Measure time for large-scale processing
        start_time = time.time()
        
        # Process 1000 events (realistic production load)
        for i in range(1000):
            equity_event = EquityBalanceChangedEvent(
                fund_id=fund.id,
                event_date=date.today(),
                old_balance=float(i * 10),
                new_balance=float((i + 1) * 10),
                change_reason=f"Large scale test {i}"
            )
            event_bus.publish(equity_event)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance is acceptable
        # 1000 events should complete in under 5 seconds
        assert total_time < 5.0, f"Large scale processing too slow: {total_time:.4f}s for 1000 events"
        
        # Verify all events were published
        stats = event_bus.get_stats()
        assert stats['events_published'] >= 1000
        
        events_per_second = 1000 / total_time
        print(f"✅ Large scale performance: {1000} events in {total_time:.4f}s ({events_per_second:.0f} events/sec)")
        
        # Verify we can handle production-scale loads
        assert events_per_second >= 100, f"Production scale performance insufficient: {events_per_second:.0f} events/sec"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
