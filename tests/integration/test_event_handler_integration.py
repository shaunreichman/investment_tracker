"""
Integration Test for Event Handler Architecture.

This module tests the complete event handler architecture to ensure
it works correctly end-to-end with real database operations.
"""

import pytest
from datetime import date
from decimal import Decimal

from src.fund.events import FundUpdateOrchestrator
from src.fund.models import FundType, EventType, DistributionType
from src.fund.models import Fund, FundEvent
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from tests.conftest import db_session


class TestEventHandlerIntegration:
    """Test the event handler architecture end-to-end."""
    
    def test_capital_call_event_flow(self, db_session):
        """Test complete capital call event flow."""
        # Create test data
        company = InvestmentCompany(
            name="Test Company",
            description="Test investment company"
        )
        db_session.add(company)
        db_session.flush()
        
        entity = Entity(
            name="Test Entity",
            description="Test entity"
        )
        db_session.add(entity)
        db_session.flush()
        
        fund = Fund.create(
            investment_company_id=company.id,
            entity_id=entity.id,
            name="Test Fund",
            fund_type="Private Equity",
            tracking_type=FundType.COST_BASED,
            description="Test fund for integration testing",
            session=db_session
        )
        
        # Test the event handler architecture
        orchestrator = FundUpdateOrchestrator()
        
        # Process a capital call event
        event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': 100000.0,
            'event_date': '2024-01-15',
            'description': 'Initial capital call',
            'reference_number': 'CC001'
        }
        
        # Validate event data
        assert orchestrator.validate_event_data(event_data) is True
        
        # Process the event
        event = orchestrator.process_fund_event(event_data, db_session, fund)
        
        # Verify the event was created correctly
        assert event is not None
        assert event.event_type == EventType.CAPITAL_CALL
        assert event.amount == 100000.0
        assert event.event_date == date(2024, 1, 15)
        assert event.description == 'Initial capital call'
        assert event.reference_number == 'CC001'
        
        # Verify the event is persisted
        db_session.refresh(event)
        assert event.id is not None
        
        # Verify fund state was updated
        db_session.refresh(fund)
        assert fund.current_equity_balance == 100000.0
    
    def test_nav_update_event_flow(self, db_session):
        """Test complete NAV update event flow."""
        # Create test data
        company = InvestmentCompany(
            name="Test NAV Company",
            description="Test NAV investment company"
        )
        db_session.add(company)
        db_session.flush()
        
        entity = Entity(
            name="Test NAV Entity",
            description="Test NAV entity"
        )
        db_session.add(entity)
        db_session.flush()
        
        fund = Fund.create(
            investment_company_id=company.id,
            entity_id=entity.id,
            name="Test NAV Fund",
            fund_type="Private Equity",
            tracking_type=FundType.NAV_BASED,
            description="Test NAV fund for integration testing",
            session=db_session
        )
        
        # Test the event handler architecture
        orchestrator = FundUpdateOrchestrator()
        
        # Process a NAV update event
        event_data = {
            'event_type': EventType.NAV_UPDATE,
            'nav_per_share': 10.50,
            'event_date': '2024-01-15',
            'description': 'Initial NAV update',
            'reference_number': 'NAV001'
        }
        
        # Validate event data
        assert orchestrator.validate_event_data(event_data) is True
        
        # Process the event
        event = orchestrator.process_fund_event(event_data, db_session, fund)
        
        # Verify the event was created correctly
        assert event is not None
        assert event.event_type == EventType.NAV_UPDATE
        assert event.nav_per_share == 10.50
        assert event.event_date == date(2024, 1, 15)
        assert event.description == 'Initial NAV update'
        assert event.reference_number == 'NAV001'
        
        # Verify the event is persisted
        db_session.refresh(event)
        assert event.id is not None
        
        # Verify fund state was updated
        db_session.refresh(fund)
        assert fund.current_unit_price == 10.50
    
    # NOTE: Distribution workflow testing moved to focused test_distribution_workflow.py
    # This eliminates duplication and follows enterprise testing principles
    # The test_distribution_workflow.py file provides comprehensive distribution testing
    
    def test_bulk_events_processing(self, db_session):
        """Test processing multiple events in a single transaction."""
        # Create test data
        company = InvestmentCompany(
            name="Test Bulk Company",
            description="Test bulk investment company"
        )
        db_session.add(company)
        db_session.flush()
        
        entity = Entity(
            name="Test Bulk Entity",
            description="Test bulk entity"
        )
        db_session.add(entity)
        db_session.flush()
        
        fund = Fund.create(
            investment_company_id=company.id,
            entity_id=entity.id,
            name="Test Bulk Fund",
            fund_type="Private Equity",
            tracking_type=FundType.COST_BASED,
            description="Test bulk fund for integration testing",
            session=db_session
        )
        
        # Test the event handler architecture
        orchestrator = FundUpdateOrchestrator()
        
        # Process multiple events
        events_data = [
            {
                'event_type': EventType.CAPITAL_CALL,
                'amount': 50000.0,
                'event_date': '2024-01-15',
                'description': 'First capital call',
                'reference_number': 'CC001'
            },
            {
                'event_type': EventType.CAPITAL_CALL,
                'amount': 50000.0,
                'event_date': '2024-02-15',
                'description': 'Second capital call',
                'reference_number': 'CC002'
            }
        ]
        
        # Process all events
        events = orchestrator.process_bulk_events(events_data, db_session, fund)
        
        # Verify all events were created
        assert len(events) == 2
        assert events[0].event_type == EventType.CAPITAL_CALL
        assert events[0].amount == 50000.0
        assert events[1].event_type == EventType.CAPITAL_CALL
        assert events[1].amount == 50000.0
        
        # Verify fund state was updated correctly
        db_session.refresh(fund)
        assert fund.current_equity_balance == 100000.0
    
    def test_registry_status(self, db_session):
        """Test that the orchestrator provides correct registry status."""
        orchestrator = FundUpdateOrchestrator()
        status = orchestrator.get_registry_status()
        
        # Verify registry status
        assert status['registry_initialized'] is True
        assert status['total_handlers'] == 6
        
        # Verify all expected event types are registered
        expected_types = [
            EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.DISTRIBUTION,
            EventType.NAV_UPDATE, EventType.UNIT_PURCHASE, EventType.UNIT_SALE
        ]
        for event_type in expected_types:
            assert event_type in status['registered_event_types']
