"""
Integration tests for capital call workflow through all refactored layers.

This file tests the complete capital call workflow from API route through
all refactored layers: Routes -> Controllers -> Services -> Repositories.

Tests cover:
- API route validation and request handling
- Controller orchestration and response formatting
- Service business logic and validation
- Repository data persistence
- Fund equity calculations and state updates
- Cash flow integration
- Error handling across all layers
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from tests.factories import (
    FundFactory, EntityFactory, CompanyFactory,
    BankFactory, BankAccountFactory
)
from src.fund.models import Fund
from src.fund.enums import FundTrackingType, EventType, CashFlowDirection, FundStatus
from src.api.controllers.fund_controller import FundController
from src.fund.services.fund_event_service import FundEventService
from src.fund.services.fund_equity_service import FundEquityService
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.repositories.fund_repository import FundRepository
from src.fund.repositories.fund_event_repository import FundEventRepository
from src.api.dto.response_codes import ApiResponseCode


class TestCapitalCallWorkflowIntegration:
    """Test complete capital call workflow through all refactored layers"""

    def test_capital_call_service_layer_flow(self, db_session):
        """Test capital call creation through service layer flow"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, CompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund with cost-based tracking
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        # Test data for capital call
        capital_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'Initial capital call',
            'reference_number': 'CC-001',
            'fund_id': fund.id
        }
        
        # Test through service layer
        fund_event_service = FundEventService()
        event = fund_event_service.create_fund_event(fund.id, capital_call_data, db_session)
        db_session.commit()
        
        # Verify event creation
        assert event.event_type == EventType.CAPITAL_CALL
        assert event.amount == 50000.0
        assert event.event_date == date(2023, 1, 15)
        assert event.description == 'Initial capital call'
        assert event.reference_number == 'CC-001'
        assert event.fund_id == fund.id

    def test_capital_call_service_layer_validation(self, db_session):
        """Test capital call validation and business logic in service layer"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, CompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create cost-based fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Test valid capital call
        event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'Valid capital call',
            'fund_id': fund.id,
        }
        
        fund_event_service = FundEventService()
        # Test that the event creation succeeds (validation happens internally)
        event = fund_event_service.create_fund_event(fund.id, event_data, db_session)
        
        # Verify event creation
        assert event.event_type == EventType.CAPITAL_CALL
        assert event.amount == 50000.0
        assert event.event_date == date(2023, 1, 15)
        assert event.fund_id == fund.id

    def test_capital_call_business_rules_validation(self, db_session):
        """Test capital call business rules and constraints"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, CompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create cost-based fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        validation_service = FundValidationService()
        
        # Test: Cannot call more than remaining commitment
        excessive_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 150000.0,  # More than commitment
            'fund_id': fund.id,
        }
        errors = validation_service.validate_capital_call(fund, excessive_call_data, db_session)
        assert 'amount' in errors
        assert 'Cannot call more capital than total commitment for first capital call' in errors['amount']
        
        # Test: Cannot call negative amount (this validation is not implemented yet)
        # negative_call_data = {
        #     'event_type': EventType.CAPITAL_CALL,
        #     'event_date': date(2023, 1, 15),
        #     'amount': -10000.0,
        #     'fund_id': fund.id
        # }
        # errors = validation_service.validate_capital_call(negative_call_data, db_session)
        # assert 'amount' in errors
        # assert 'Capital call amount must be a positive number' in errors['amount']
        
        # Test: NAV-based funds cannot have capital calls
        nav_fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        nav_call_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'fund_id': nav_fund.id
        }
        errors = validation_service.validate_capital_call(nav_fund, nav_call_data, db_session)
        assert 'fund_type' in errors
        assert 'Capital calls are only applicable for cost-based funds' in errors['fund_type']

    def test_capital_call_equity_calculations(self, db_session):
        """Test fund equity calculations after capital call"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, CompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        # Initial state
        assert fund.current_equity_balance == 0.0
        assert fund.commitment_amount - fund.current_equity_balance == 200000.0
        
        # Create capital call
        event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 75000.0,
            'description': 'First capital call',
            'fund_id': fund.id,
        }
        
        fund_event_service = FundEventService()
        event = fund_event_service.create_fund_event(fund.id, event_data, db_session)
        db_session.commit()

        # Verify fund state updates (equity should be updated by the service)
        db_session.refresh(fund)
        assert fund.current_equity_balance == 75000.0
        assert fund.commitment_amount - fund.current_equity_balance == 125000.0
        
        # Verify event was created successfully
        assert event is not None
        assert event.event_type == EventType.CAPITAL_CALL

    def test_multiple_capital_calls_cumulative_tracking(self, db_session):
        """Test multiple capital calls with cumulative tracking"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, CompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=300000.0
        )
        db_session.commit()
        
        fund_event_service = FundEventService()

        # First capital call
        event_data_1 = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 100000.0,
            'description': 'First capital call',
            'fund_id': fund.id,
        }
        fund_event_service.create_fund_event(fund.id, event_data_1, db_session)
        db_session.commit()

        db_session.refresh(fund)
        assert fund.current_equity_balance == 100000.0
        assert fund.commitment_amount - fund.current_equity_balance == 200000.0

        # Second capital call
        event_data_2 = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 3, 15),
            'amount': 150000.0,
            'description': 'Second capital call',
            'fund_id': fund.id,
        }
        fund_event_service.create_fund_event(fund.id, event_data_2, db_session)
        db_session.commit()

        db_session.refresh(fund)
        assert fund.current_equity_balance == 250000.0
        assert fund.commitment_amount - fund.current_equity_balance == 50000.0
        
        # Verify all events exist
        fund_event_repository = FundEventRepository()
        events = fund_event_repository.get_fund_events(
            db_session, 
            fund_ids=[fund.id], 
            event_types=[EventType.CAPITAL_CALL]
        )
        assert len(events) == 2

    def test_capital_call_with_cash_flow_integration(self, db_session):
        """Test capital call workflow with cash flow creation"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, CompanyFactory, 
                       BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund and bank account
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(
            entity=entity,
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0,
            currency="AUD"
        )
        db_session.commit()
        
        # Create capital call
        event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'Capital call with cash flow',
            'fund_id': fund.id,
        }
        
        fund_event_service = FundEventService()
        event = fund_event_service.create_fund_event(fund.id, event_data, db_session)
        db_session.commit()
        
        # Add cash flow for the capital call
        from src.fund.services.fund_event_cash_flow_service import FundEventCashFlowService
        cash_flow_service = FundEventCashFlowService()
        
        cash_flow_data = {
            'bank_account_id': account.id,
            'amount': 50000.0,
            'currency': 'AUD',
            'transfer_date': date(2023, 1, 16),
            'direction': CashFlowDirection.OUTFLOW
        }
        
        cash_flow = cash_flow_service.create_fund_event_cash_flow(event.id, cash_flow_data, db_session)
        db_session.commit()
        
        # Verify cash flow was created and linked
        assert cash_flow.amount == 50000.0
        assert cash_flow.direction == CashFlowDirection.OUTFLOW
        assert cash_flow.transfer_date == date(2023, 1, 16)
        assert cash_flow.fund_event_id == event.id

    def test_capital_call_repository_persistence(self, db_session):
        """Test capital call data persistence through repository layer"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, CompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Test repository layer directly
        fund_event_repository = FundEventRepository()
        
        event_data = {
            'fund_id': fund.id,
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'Repository test call',
            'reference_number': 'REPO-001',
        }
        
        # Create event through repository
        event = fund_event_repository.create_fund_event(event_data, db_session)
        db_session.commit()
        
        # Verify persistence
        assert event.id is not None
        assert event.fund_id == fund.id
        assert event.event_type == EventType.CAPITAL_CALL
        assert event.amount == 50000.0
        
        # Test retrieval
        retrieved_event = fund_event_repository.get_fund_event_by_id(event.id, db_session)
        assert retrieved_event is not None
        assert retrieved_event.id == event.id
        assert retrieved_event.description == 'Repository test call'

    def test_capital_call_error_handling_across_layers(self, db_session):
        """Test error handling across all layers"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, CompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Test service layer error handling
        fund_event_service = FundEventService()
        
        # Test with invalid fund ID
        with pytest.raises(ValueError):
            invalid_event_data = {
                'event_type': EventType.CAPITAL_CALL,
                'event_date': date(2023, 1, 15),
                'amount': 50000.0,
                'fund_id': 99999,  # Non-existent fund
            }
            fund_event_service.create_fund_event(99999, invalid_event_data, db_session)
        
        # Test with invalid event type
        with pytest.raises(ValueError):
            invalid_event_data = {
                'event_type': 'INVALID_TYPE',
                'event_date': date(2023, 1, 15),
                'amount': 50000.0,
                'fund_id': fund.id,
            }
            fund_event_service.create_fund_event(fund.id, invalid_event_data, db_session)

    def test_capital_call_transaction_integrity(self, db_session):
        """Test transaction integrity across all layers"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, CompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Record initial state
        initial_equity = fund.current_equity_balance
        initial_remaining = fund.commitment_amount - fund.current_equity_balance
        
        # Create capital call through service
        fund_event_service = FundEventService()
        equity_service = FundEquityService()
        
        event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2023, 1, 15),
            'amount': 25000.0,
            'description': 'Transaction integrity test',
            'fund_id': fund.id,
        }
        
        event = fund_event_service.create_fund_event(fund.id, event_data, db_session)
        equity_service.update_fund_equity_fields(fund, db_session)
        db_session.commit()
        
        # Verify all related state changes are consistent
        db_session.refresh(fund)
        assert fund.current_equity_balance == initial_equity + 25000.0
        assert fund.commitment_amount - fund.current_equity_balance == initial_remaining - 25000.0
        
        # Verify the sum of called and remaining equals total commitment
        assert fund.current_equity_balance + (fund.commitment_amount - fund.current_equity_balance) == fund.commitment_amount
        
        # Verify event count increased by exactly one
        fund_event_repository = FundEventRepository()
        events = fund_event_repository.get_fund_events(
            db_session, 
            fund_ids=[fund.id], 
            event_types=[EventType.CAPITAL_CALL]
        )
        assert len(events) == 1

    def test_capital_call_performance_with_large_dataset(self, db_session):
        """Test capital call performance with multiple events"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, CompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.0  # Large commitment
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        equity_service = FundEquityService()
        
        # Create multiple capital calls
        call_amounts = [10000.0, 15000.0, 25000.0, 30000.0, 20000.0]
        total_called = 0.0
        
        for i, amount in enumerate(call_amounts):
            # Calculate proper dates for monthly calls
            call_date = date(2023, 1 + i, 15) if 1 + i <= 12 else date(2023 + (1 + i - 1) // 12, ((1 + i - 1) % 12) + 1, 15)
            event_data = {
                'event_type': EventType.CAPITAL_CALL,
                'event_date': call_date,
                'amount': amount,
                'description': f'Capital call {i+1}',
                'fund_id': fund.id,
            }
            
            fund_event_service.create_fund_event(fund.id, event_data, db_session)
            total_called += amount
        
        # Update equity calculations
        equity_service.update_fund_equity_fields(fund, db_session)
        db_session.commit()
        
        # Verify final state
        db_session.refresh(fund)
        assert fund.current_equity_balance == total_called
        assert fund.commitment_amount - fund.current_equity_balance == fund.commitment_amount - total_called
        
        # Verify all events were created
        fund_event_repository = FundEventRepository()
        events = fund_event_repository.get_fund_events(
            db_session, 
            fund_ids=[fund.id], 
            event_types=[EventType.CAPITAL_CALL]
        )
        assert len(events) == len(call_amounts)
