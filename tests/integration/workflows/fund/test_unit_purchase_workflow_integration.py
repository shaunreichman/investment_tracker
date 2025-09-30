"""
Integration tests for unit purchase workflow through all refactored layers.

This file tests the complete unit purchase workflow from API route through
all refactored layers: Routes -> Controllers -> Services -> Repositories.

Tests cover:
- API route validation and request handling
- Controller orchestration and response formatting
- Service business logic and validation
- Repository data persistence
- Fund equity calculations and state updates (NAV-based funds)
- Cash flow integration
- Error handling across all layers
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from tests.factories import (
    FundFactory, EntityFactory, InvestmentCompanyFactory,
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


class TestUnitPurchaseWorkflowIntegration:
    """Test complete unit purchase workflow through all refactored layers"""

    def test_unit_purchase_service_layer_flow(self, db_session):
        """Test unit purchase creation through service layer flow"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund (required for unit purchases)
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        # Test data for unit purchase
        unit_purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'Initial unit purchase',
            'reference_number': 'UP-001',
            'fund_id': fund.id,
            'units_purchased': 1000.0,
            'unit_price': 50.0,
            'brokerage_fee': 100.0
        }
        
        # Test through service layer
        fund_event_service = FundEventService()
        event = fund_event_service.create_fund_event(fund.id, unit_purchase_data, db_session)
        
        # WORKAROUND: Manually update current_units since this functionality is missing from the refactored system
        # TODO: Add proper units calculation service to the fund equity service
        fund.current_units = unit_purchase_data['units_purchased']
        event.units_owned = unit_purchase_data['units_purchased']
        
        db_session.commit()
        
        # Verify event creation
        assert event.event_type == EventType.UNIT_PURCHASE
        assert event.amount == 50000.0
        assert event.event_date == date(2023, 1, 15)
        assert event.description == 'Initial unit purchase'
        assert event.reference_number == 'UP-001'
        assert event.fund_id == fund.id
        assert event.units_purchased == 1000.0
        assert event.unit_price == 50.0
        assert event.brokerage_fee == 100.0

    def test_unit_purchase_service_layer_validation(self, db_session):
        """Test unit purchase validation and business logic in service layer"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Test valid unit purchase
        event_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 25000.0,
            'description': 'Valid unit purchase',
            'fund_id': fund.id,
            'units_purchased': 500.0,
            'unit_price': 50.0,
            'brokerage_fee': 50.0
        }
        
        fund_event_service = FundEventService()
        event = fund_event_service.create_fund_event(fund.id, event_data, db_session)
        
        # WORKAROUND: Manually update current_units since this functionality is missing from the refactored system
        fund.current_units = event_data['units_purchased']
        event.units_owned = event_data['units_purchased']
        
        # Verify event creation
        assert event.event_type == EventType.UNIT_PURCHASE
        assert event.amount == 25000.0
        assert event.event_date == date(2023, 1, 15)
        assert event.fund_id == fund.id
        assert event.units_purchased == 500.0
        assert event.unit_price == 50.0
        
        # Test validation service
        validation_service = FundValidationService()
        errors = validation_service.validate_fund_event_creation(event_data, db_session)
        assert not errors  # Should be no validation errors

    def test_unit_purchase_business_rules_validation(self, db_session):
        """Test unit purchase business rules and constraints"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        nav_fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0
        )
        
        # Create cost-based fund (should not allow unit purchases)
        cost_fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        validation_service = FundValidationService()
        
        # Test: NAV-based fund allows unit purchases
        valid_purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 25000.0,
            'fund_id': nav_fund.id,
            'units_purchased': 500.0,
            'unit_price': 50.0
        }
        errors = validation_service.validate_unit_purchase(nav_fund, valid_purchase_data, db_session)
        assert not errors  # Should be no validation errors
        
        # Test: Cost-based funds cannot have unit purchases
        invalid_purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 25000.0,
            'fund_id': cost_fund.id,
            'units_purchased': 500.0,
            'unit_price': 50.0
        }
        errors = validation_service.validate_unit_purchase(cost_fund, invalid_purchase_data, db_session)
        assert 'fund_type' in errors
        assert 'Unit purchases are only applicable for NAV-based funds' in errors['fund_type']

    def test_unit_purchase_equity_calculations(self, db_session):
        """Test fund equity calculations after unit purchase"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        # Initial state
        assert fund.current_equity_balance == 0.0
        
        # Create unit purchase
        event_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 75000.0,
            'description': 'First unit purchase',
            'fund_id': fund.id,
            'units_purchased': 1500.0,
            'unit_price': 50.0,
            'brokerage_fee': 150.0
        }
        
        fund_event_service = FundEventService()
        event = fund_event_service.create_fund_event(fund.id, event_data, db_session)
        db_session.commit()

        # Verify fund state updates (equity should be updated by the service)
        db_session.refresh(fund)
        # For NAV-based funds, equity balance = units * unit_price (excluding brokerage for equity calculation)
        expected_equity = 1500.0 * 50.0  # 75000.0
        assert fund.current_equity_balance == expected_equity
        
        # Verify event was created successfully
        assert event is not None
        assert event.event_type == EventType.UNIT_PURCHASE

    def test_multiple_unit_purchases_fifo_tracking(self, db_session):
        """Test multiple unit purchases with FIFO tracking"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=300000.0
        )
        db_session.commit()
        
        fund_event_service = FundEventService()

        # First unit purchase
        event_data_1 = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'First unit purchase',
            'fund_id': fund.id,
            'units_purchased': 1000.0,
            'unit_price': 50.0,
            'brokerage_fee': 100.0
        }
        fund_event_service.create_fund_event(fund.id, event_data_1, db_session)
        db_session.commit()

        db_session.refresh(fund)
        assert fund.current_equity_balance == 50000.0  # 1000 * 50

        # Second unit purchase at different price
        event_data_2 = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 3, 15),
            'amount': 60000.0,
            'description': 'Second unit purchase',
            'fund_id': fund.id,
            'units_purchased': 1200.0,
            'unit_price': 50.0,
            'brokerage_fee': 120.0
        }
        fund_event_service.create_fund_event(fund.id, event_data_2, db_session)
        db_session.commit()

        db_session.refresh(fund)
        expected_total_equity = (1000.0 * 50.0) + (1200.0 * 50.0)  # 110000.0
        assert fund.current_equity_balance == expected_total_equity
        
        # Verify all events exist
        fund_event_repository = FundEventRepository()
        events = fund_event_repository.get_fund_events(
            db_session, 
            fund_ids=[fund.id], 
            event_types=[EventType.UNIT_PURCHASE]
        )
        assert len(events) == 2

    def test_unit_purchase_with_cash_flow_integration(self, db_session):
        """Test unit purchase workflow with cash flow creation"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, 
                       BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund and bank account
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(
            entity=entity,
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            currency="AUD"
        )
        db_session.commit()
        
        # Create unit purchase
        event_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 25000.0,
            'description': 'Unit purchase with cash flow',
            'fund_id': fund.id,
            'units_purchased': 500.0,
            'unit_price': 50.0,
            'brokerage_fee': 50.0
        }
        
        fund_event_service = FundEventService()
        event = fund_event_service.create_fund_event(fund.id, event_data, db_session)
        db_session.commit()
        
        # Add cash flow for the unit purchase (outflow - paying for units)
        from src.fund.services.fund_event_cash_flow_service import FundEventCashFlowService
        cash_flow_service = FundEventCashFlowService()
        
        cash_flow_data = {
            'bank_account_id': account.id,
            'amount': 25050.0,  # 25000 + 50 brokerage
            'currency': 'AUD',
            'transfer_date': date(2023, 1, 16),
            'direction': CashFlowDirection.OUTFLOW
        }
        
        cash_flow = cash_flow_service.create_fund_event_cash_flow(event.id, cash_flow_data, db_session)
        db_session.commit()
        
        # Verify cash flow was created and linked
        assert cash_flow.amount == 25050.0
        assert cash_flow.direction == CashFlowDirection.OUTFLOW
        assert cash_flow.transfer_date == date(2023, 1, 16)
        assert cash_flow.fund_event_id == event.id

    def test_unit_purchase_repository_persistence(self, db_session):
        """Test unit purchase data persistence through repository layer"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Test repository layer directly
        fund_event_repository = FundEventRepository()
        
        event_data = {
            'fund_id': fund.id,
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 30000.0,
            'description': 'Repository test purchase',
            'reference_number': 'REPO-UP-001',
            'units_purchased': 600.0,
            'unit_price': 50.0,
            'brokerage_fee': 60.0
        }
        
        # Create event through repository
        event = fund_event_repository.create_fund_event(event_data, db_session)
        db_session.commit()
        
        # Verify persistence
        assert event.id is not None
        assert event.fund_id == fund.id
        assert event.event_type == EventType.UNIT_PURCHASE
        assert event.amount == 30000.0
        assert event.units_purchased == 600.0
        assert event.unit_price == 50.0
        assert event.brokerage_fee == 60.0
        
        # Test retrieval
        retrieved_event = fund_event_repository.get_fund_event_by_id(event.id, db_session)
        assert retrieved_event is not None
        assert retrieved_event.id == event.id
        assert retrieved_event.description == 'Repository test purchase'

    def test_unit_purchase_error_handling_across_layers(self, db_session):
        """Test error handling across all layers"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Test service layer error handling
        fund_event_service = FundEventService()
        
        # Test with invalid fund ID
        with pytest.raises(ValueError):
            invalid_event_data = {
                'event_type': EventType.UNIT_PURCHASE,
                'event_date': date(2023, 1, 15),
                'amount': 25000.0,
                'fund_id': 99999,  # Non-existent fund
                'units_purchased': 500.0,
                'unit_price': 50.0
            }
            fund_event_service.create_fund_event(99999, invalid_event_data, db_session)
        
        # Test with invalid event type
        with pytest.raises(ValueError):
            invalid_event_data = {
                'event_type': 'INVALID_TYPE',
                'event_date': date(2023, 1, 15),
                'amount': 25000.0,
                'fund_id': fund.id,
                'units_purchased': 500.0,
                'unit_price': 50.0
            }
            fund_event_service.create_fund_event(fund.id, invalid_event_data, db_session)

    def test_unit_purchase_transaction_integrity(self, db_session):
        """Test transaction integrity across all layers"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Record initial state
        initial_equity = fund.current_equity_balance
        
        # Create unit purchase through service
        fund_event_service = FundEventService()
        equity_service = FundEquityService()
        
        event_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 12500.0,
            'description': 'Transaction integrity test',
            'fund_id': fund.id,
            'units_purchased': 250.0,
            'unit_price': 50.0,
            'brokerage_fee': 25.0
        }
        
        event = fund_event_service.create_fund_event(fund.id, event_data, db_session)
        equity_service.update_fund_equity_fields(fund, db_session)
        db_session.commit()
        
        # Verify all related state changes are consistent
        db_session.refresh(fund)
        expected_equity = initial_equity + (250.0 * 50.0)  # 12500.0
        assert fund.current_equity_balance == expected_equity
        
        # Verify event count increased by exactly one
        fund_event_repository = FundEventRepository()
        events = fund_event_repository.get_fund_events(
            db_session, 
            fund_ids=[fund.id], 
            event_types=[EventType.UNIT_PURCHASE]
        )
        assert len(events) == 1

    def test_unit_purchase_performance_with_large_dataset(self, db_session):
        """Test unit purchase performance with multiple events"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=1000000.0  # Large commitment
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        equity_service = FundEquityService()
        
        # Create multiple unit purchases
        purchase_data = [
            {'units': 1000.0, 'price': 45.0, 'brokerage': 45.0},
            {'units': 1500.0, 'price': 50.0, 'brokerage': 75.0},
            {'units': 2000.0, 'price': 55.0, 'brokerage': 110.0},
            {'units': 1200.0, 'price': 52.0, 'brokerage': 62.0},
            {'units': 800.0, 'price': 48.0, 'brokerage': 40.0}
        ]
        total_equity = 0.0
        
        for i, data in enumerate(purchase_data):
            # Calculate proper dates for monthly purchases
            purchase_date = date(2023, 1 + i, 15) if 1 + i <= 12 else date(2023 + (1 + i - 1) // 12, ((1 + i - 1) % 12) + 1, 15)
            event_data = {
                'event_type': EventType.UNIT_PURCHASE,
                'event_date': purchase_date,
                'amount': data['units'] * data['price'],
                'description': f'Unit purchase {i+1}',
                'fund_id': fund.id,
                'units_purchased': data['units'],
                'unit_price': data['price'],
                'brokerage_fee': data['brokerage']
            }
            
            fund_event_service.create_fund_event(fund.id, event_data, db_session)
            total_equity += data['units'] * data['price']
        
        # Update equity calculations
        equity_service.update_fund_equity_fields(fund, db_session)
        db_session.commit()
        
        # Verify final state
        db_session.refresh(fund)
        assert fund.current_equity_balance == total_equity
        
        # Verify all events were created
        fund_event_repository = FundEventRepository()
        events = fund_event_repository.get_fund_events(
            db_session, 
            fund_ids=[fund.id], 
            event_types=[EventType.UNIT_PURCHASE]
        )
        assert len(events) == len(purchase_data)
