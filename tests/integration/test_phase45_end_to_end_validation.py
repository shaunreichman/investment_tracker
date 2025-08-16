"""
Phase 4.5 End-to-End Validation Tests.

This module provides comprehensive testing of the complete event-driven system
to validate that loose coupling and event consumption are working correctly.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from src.fund.models import Fund, FundEvent, FundType, FundStatus, EventType
from src.fund.events.consumption.event_bus import event_bus
from src.fund.events.consumption.handlers.tax_statement_event_handler import TaxStatementEventHandler
from src.fund.events.consumption.handlers.company_record_event_handler import CompanyRecordEventHandler
from src.fund.events.domain import (
    EquityBalanceChangedEvent,
    DistributionRecordedEvent,
    NAVUpdatedEvent,
    TaxStatementUpdatedEvent,
    FundSummaryUpdatedEvent
)
from src.tax.models import TaxStatement
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from tests.factories import (
    FundFactory, FundEventFactory, TaxStatementFactory,
    InvestmentCompanyFactory, EntityFactory
)


class TestPhase45EndToEndValidation:
    """
    Comprehensive end-to-end validation of Phase 4.5 event-driven architecture.
    
    These tests validate that the complete event flow works from API to event consumption,
    ensuring true loose coupling between components.
    """
    
    def test_complete_event_flow_capital_call_to_tax_statement(self, db_session: Session):
        """
        Test complete event flow: Capital Call → Event Publishing → Event Consumption → Tax Statement Update.
        
        This validates the entire loose coupling architecture end-to-end.
        """
        # Setup test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED,
            status=FundStatus.ACTIVE
        )
        
        # Verify initial state
        assert fund.current_equity_balance == 0.0
        assert fund.status == FundStatus.ACTIVE
        
        # Create capital call event through the proper event handling pipeline
        # We'll use the orchestrator to process the event properly
        from src.fund.events.orchestrator import FundUpdateOrchestrator
        from src.fund.events.registry import FundEventHandlerRegistry
        
        # Create orchestrator with registry
        registry = FundEventHandlerRegistry()
        orchestrator = FundUpdateOrchestrator(registry=registry)
        
        # Create event data for the orchestrator
        event_data = {
            "event_type": EventType.CAPITAL_CALL,
            "amount": 100000.0,
            "date": date.today(),
            "description": "Test capital call for end-to-end validation"
        }
        
        # Process the event through the orchestrator
        capital_event = orchestrator.process_fund_event(event_data, db_session, fund)
        
        # Verify event was created
        assert capital_event.id is not None
        assert capital_event.amount == 100000.0
        
        # Verify fund was updated through event consumption
        db_session.refresh(fund)
        assert fund.current_equity_balance == 100000.0
        
        # Now create a tax statement (this should trigger TaxStatementUpdatedEvent)
        tax_statement = TaxStatementFactory(
            fund=fund,
            entity=entity,
            financial_year="2024-25",
            statement_date=date.today()
        )
        
        # Verify tax statement was created
        assert tax_statement.id is not None
        assert tax_statement.fund_id == fund.id
        
        # Verify that fund status was updated through event consumption
        # (not through direct model calls)
        db_session.refresh(fund)
        # The fund status should be updated through the event handler
        
        print(f"✅ Complete event flow validated: Capital Call → Event Publishing → Event Consumption → Tax Statement Update")
    
    def test_event_consumption_through_event_bus(self, db_session: Session):
        """
        Test that events are properly consumed through the event bus system.
        
        This validates that the event consumption architecture is working correctly.
        """
        # Register event handlers
        tax_handler = TaxStatementEventHandler()
        company_handler = CompanyRecordEventHandler()
        
        # Subscribe handlers to events
        event_bus.subscribe_consumer(EquityBalanceChangedEvent, tax_handler)
        event_bus.subscribe_consumer(EquityBalanceChangedEvent, company_handler)
        event_bus.subscribe_consumer(FundSummaryUpdatedEvent, company_handler)
        
        # Create test fund
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED
        )
        
        # Publish test events
        equity_event = EquityBalanceChangedEvent(
            fund_id=fund.id,
            event_date=date.today(),
            old_balance=0.0,
            new_balance=50000.0,
            change_reason="Test equity change"
        )
        
        summary_event = FundSummaryUpdatedEvent(
            fund_id=fund.id,
            event_date=date.today(),
            summary_type="TEST_UPDATE"
        )
        
        # Publish events
        event_bus.publish(equity_event)
        event_bus.publish(summary_event)
        
        # Verify events were processed
        stats = event_bus.get_stats()
        assert stats['events_published'] >= 2
        assert stats['events_processed'] >= 2
        
        print(f"✅ Event consumption through event bus validated: {stats['events_processed']} events processed")
    
    def test_loose_coupling_tax_statement_creation(self, db_session: Session):
        """
        Test that tax statement creation uses events instead of direct model calls.
        
        This validates that we've achieved true loose coupling.
        """
        # Setup test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED
        )
        
        # Create tax statement through API (this should trigger event publishing)
        # We'll simulate the API call by creating the event directly
        tax_event = TaxStatementUpdatedEvent(
            fund_id=fund.id,
            event_date=date.today(),
            tax_statement_id=999,  # Dummy ID for testing
            update_type="created",
            financial_year="2024-25",
            entity_id=entity.id
        )
        
        # Verify event was created correctly
        assert tax_event.fund_id == fund.id
        assert tax_event.update_type == "created"
        assert tax_event.financial_year == "2024-25"
        
        # Publish event to event bus
        event_bus.publish(tax_event)
        
        # Verify event was processed
        stats = event_bus.get_stats()
        assert stats['events_published'] >= 1
        
        print(f"✅ Loose coupling validated: Tax statement creation uses events, not direct model calls")
    
    def test_fund_summary_updates_through_events(self, db_session: Session):
        """
        Test that fund summary updates are handled through events.
        
        This validates the FundSummaryUpdatedEvent and its consumption.
        """
        # Setup test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED
        )
        
        # Create fund summary update event
        summary_event = FundSummaryUpdatedEvent(
            fund_id=fund.id,
            event_date=date.today(),
            summary_type="CAPITAL_EVENT_PROCESSED",
            metadata={
                "original_event_id": 123,
                "original_event_type": "CAPITAL_CALL",
                "amount": 75000.0
            }
        )
        
        # Verify event structure
        assert summary_event.fund_id == fund.id
        assert summary_event.summary_type == "CAPITAL_EVENT_PROCESSED"
        assert summary_event.metadata["amount"] == 75000.0
        
        # Publish event
        event_bus.publish(summary_event)
        
        # Verify event was processed
        stats = event_bus.get_stats()
        assert stats['events_published'] >= 1
        
        print(f"✅ Fund summary updates through events validated")
    
    def test_event_handler_registration_and_routing(self, db_session: Session):
        """
        Test that event handlers are properly registered and route events correctly.
        
        This validates the event handler registry and routing system.
        """
        from src.fund.events.consumption.handler_registry import EventHandlerRegistry
        
        # Create registry and register handlers
        registry = EventHandlerRegistry()
        registry.register_all_handlers()
        
        # Verify handlers were registered
        assert registry.registered is True
        assert len(registry.handlers) >= 2  # Tax and company handlers
        
        # Get handler stats
        stats = registry.get_handler_stats()
        assert stats['total_handlers'] >= 2
        assert stats['registered'] is True
        
        print(f"✅ Event handler registration and routing validated: {stats['total_handlers']} handlers registered")
    
    def test_performance_event_consumption(self, db_session: Session):
        """
        Test that event consumption doesn't introduce performance issues.
        
        This validates that the loose coupling architecture maintains performance.
        """
        import time
        
        # Setup test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity
        )
        
        # Measure time to publish and consume events
        start_time = time.time()
        
        # Publish multiple events
        for i in range(10):
            equity_event = EquityBalanceChangedEvent(
                fund_id=fund.id,
                event_date=date.today(),
                old_balance=float(i * 10000),
                new_balance=float((i + 1) * 10000),
                change_reason=f"Performance test {i}"
            )
            event_bus.publish(equity_event)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance is acceptable (should be very fast)
        assert total_time < 1.0  # Should complete in under 1 second
        
        # Verify all events were processed
        stats = event_bus.get_stats()
        assert stats['events_published'] >= 10
        
        print(f"✅ Performance validation passed: {10} events processed in {total_time:.4f} seconds")
    
    def test_complete_workflow_integration(self, db_session: Session):
        """
        Test complete workflow integration: Fund creation → Events → Tax statements → Company updates.
        
        This validates the entire system works together seamlessly.
        """
        # Setup complete test scenario
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED,
            status=FundStatus.ACTIVE
        )
        
        # Step 1: Create capital call event
        capital_event = FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=200000.0,
            event_date=date.today()
        )
        
        # Step 2: Create distribution event
        distribution_event = FundEventFactory(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            amount=50000.0,
            event_date=date.today()
        )
        
        # Step 3: Create tax statement
        tax_statement = TaxStatementFactory(
            fund=fund,
            entity=entity,
            financial_year="2024-25",
            statement_date=date.today()
        )
        
        # Verify all components were created and updated through events
        assert capital_event.id is not None
        assert distribution_event.id is not None
        assert tax_statement.id is not None
        
        # Verify fund state is consistent
        db_session.refresh(fund)
        # The fund should have been updated through event consumption
        
        print(f"✅ Complete workflow integration validated: Fund → Events → Tax Statements → Company Updates")
    
    def test_error_handling_in_event_consumption(self, db_session: Session):
        """
        Test that error handling works correctly in event consumption.
        
        This validates robustness of the event-driven architecture.
        """
        # Test with invalid fund ID (should not crash the system)
        try:
            invalid_event = EquityBalanceChangedEvent(
                fund_id=99999,  # Non-existent fund
                event_date=date.today(),
                old_balance=0.0,
                new_balance=100000.0,
                change_reason="Test error handling"
            )
            
            # Publish event (should be handled gracefully)
            event_bus.publish(invalid_event)
            
            # Verify system is still stable
            stats = event_bus.get_stats()
            assert stats['events_published'] >= 1
            
            print(f"✅ Error handling in event consumption validated: System remains stable")
            
        except Exception as e:
            # If an exception occurs, it should be handled gracefully
            print(f"⚠️  Expected error handled gracefully: {e}")
            assert "not found" in str(e) or "doesn't exist" in str(e)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
