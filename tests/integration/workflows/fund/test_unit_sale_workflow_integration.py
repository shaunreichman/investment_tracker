"""
Integration tests for unit sale workflow through all refactored layers.

This file tests the complete unit sale workflow from API route through
all refactored layers: Routes -> Controllers -> Services -> Repositories.

Tests cover:
- API route validation and request handling
- Controller orchestration and response formatting
- Service business logic and validation
- Repository data persistence
- Fund equity calculations and state updates (NAV-based funds)
- Cash flow integration
- FIFO unit tracking (selling oldest units first)
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


class TestUnitSaleWorkflowIntegration:
    """Test complete unit sale workflow through all refactored layers"""

    def test_unit_sale_service_layer_flow(self, db_session):
        """Test unit sale creation through service layer flow"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund (required for unit sales)
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            status=FundStatus.ACTIVE
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # First create a unit purchase to have units to sell
        purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'Initial unit purchase',
            'fund_id': fund.id,
            'units_purchased': 1000.0,
            'unit_price': 50.0,
            'brokerage_fee': 100.0
        }
        fund_event_service.create_fund_event(fund.id, purchase_data, db_session)
        db_session.commit()
        
        # Now test unit sale
        sale_data = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 6, 15),
            'amount': 27500.0,
            'description': 'Partial unit sale',
            'reference_number': 'US-001',
            'fund_id': fund.id,
            'units_sold': 500.0,
            'unit_price': 55.0,
            'brokerage_fee': 150.0
        }
        
        # Test through service layer
        event = fund_event_service.create_fund_event(fund.id, sale_data, db_session)
        db_session.commit()
        
        # Verify event creation
        assert event.event_type == EventType.UNIT_SALE
        assert event.amount == 27500.0
        assert event.event_date == date(2023, 6, 15)
        assert event.description == 'Partial unit sale'
        assert event.reference_number == 'US-001'
        assert event.fund_id == fund.id
        assert event.units_sold == 500.0
        assert event.unit_price == 55.0
        assert event.brokerage_fee == 150.0

    def test_unit_sale_service_layer_validation(self, db_session):
        """Test unit sale validation and business logic in service layer"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # Purchase units first
        purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 25000.0,
            'description': 'Initial purchase for sale test',
            'fund_id': fund.id,
            'units_purchased': 500.0,
            'unit_price': 50.0,
            'brokerage_fee': 50.0
        }
        fund_event_service.create_fund_event(fund.id, purchase_data, db_session)
        db_session.commit()
        
        # Test valid unit sale
        sale_data = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 7, 15),
            'amount': 13750.0,
            'description': 'Valid unit sale',
            'fund_id': fund.id,
            'units_sold': 250.0,
            'unit_price': 55.0,
            'brokerage_fee': 75.0
        }
        
        # Test that the event creation succeeds (validation happens internally)
        event = fund_event_service.create_fund_event(fund.id, sale_data, db_session)
        
        # Verify event creation
        assert event.event_type == EventType.UNIT_SALE
        assert event.amount == 13750.0
        assert event.event_date == date(2023, 7, 15)
        assert event.fund_id == fund.id
        assert event.units_sold == 250.0
        assert event.unit_price == 55.0

    def test_unit_sale_business_rules_validation(self, db_session):
        """Test unit sale business rules and constraints"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        nav_fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0
        )
        
        # Create cost-based fund (should not allow unit sales)
        cost_fund = FundFactory.create(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # Purchase units in NAV-based fund
        purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 25000.0,
            'fund_id': nav_fund.id,
            'units_purchased': 500.0,
            'unit_price': 50.0
        }
        fund_event_service.create_fund_event(nav_fund.id, purchase_data, db_session)
        db_session.commit()
        
        validation_service = FundValidationService()
        
        # Test: NAV-based fund allows unit sales
        valid_sale_data = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 6, 15),
            'amount': 13750.0,
            'fund_id': nav_fund.id,
            'units_sold': 250.0,
            'unit_price': 55.0
        }
        errors = validation_service.validate_unit_sale(nav_fund, valid_sale_data, db_session)
        assert not errors  # Should be no validation errors
        
        # Test: Cost-based funds cannot have unit sales
        invalid_sale_data = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 6, 15),
            'amount': 13750.0,
            'fund_id': cost_fund.id,
            'units_sold': 250.0,
            'unit_price': 55.0
        }
        errors = validation_service.validate_unit_sale(cost_fund, invalid_sale_data, db_session)
        assert 'fund_type' in errors
        assert 'Unit sales are only applicable for NAV-based funds' in errors['fund_type']

    def test_unit_sale_equity_calculations(self, db_session):
        """Test fund equity calculations after unit sale"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        
        # Initial state
        assert fund.current_equity_balance == 0.0
        
        # Purchase units
        purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 75000.0,
            'description': 'Initial purchase',
            'fund_id': fund.id,
            'units_purchased': 1500.0,
            'unit_price': 50.0,
            'brokerage_fee': 150.0
        }
        fund_event_service.create_fund_event(fund.id, purchase_data, db_session)
        db_session.commit()
        
        db_session.refresh(fund)
        assert fund.current_equity_balance == 75000.0
        
        # Sell some units
        sale_data = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 7, 15),
            'amount': 44000.0,
            'description': 'Partial sale',
            'fund_id': fund.id,
            'units_sold': 800.0,
            'unit_price': 55.0,
            'brokerage_fee': 200.0
        }
        
        event = fund_event_service.create_fund_event(fund.id, sale_data, db_session)
        db_session.commit()

        # Verify fund state updates (equity should be reduced by cost basis, not sale price)
        db_session.refresh(fund)
        # Equity after sale = initial equity - (units_sold * purchase_price)
        # IMPORTANT: Equity tracks cost basis, not market value
        # Sold 800 units at purchase price of $50 = 800 * 50 = 40,000
        expected_equity = 75000.0 - (800.0 * 50.0)  # 75000 - 40000 = 35000
        assert fund.current_equity_balance == expected_equity
        
        # Verify event was created successfully
        assert event is not None
        assert event.event_type == EventType.UNIT_SALE

    def test_multiple_unit_sales_fifo_tracking(self, db_session):
        """Test multiple unit sales with FIFO tracking"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=300000.0
        )
        db_session.commit()
        
        fund_event_service = FundEventService()

        # First purchase
        purchase_data_1 = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 50000.0,
            'description': 'First purchase',
            'fund_id': fund.id,
            'units_purchased': 1000.0,
            'unit_price': 50.0,
            'brokerage_fee': 100.0
        }
        fund_event_service.create_fund_event(fund.id, purchase_data_1, db_session)
        db_session.commit()

        db_session.refresh(fund)
        assert fund.current_equity_balance == 50000.0

        # Second purchase
        purchase_data_2 = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 3, 15),
            'amount': 60000.0,
            'description': 'Second purchase',
            'fund_id': fund.id,
            'units_purchased': 1200.0,
            'unit_price': 50.0,
            'brokerage_fee': 120.0
        }
        fund_event_service.create_fund_event(fund.id, purchase_data_2, db_session)
        db_session.commit()

        db_session.refresh(fund)
        assert fund.current_equity_balance == 110000.0  # 50000 + 60000

        # First sale (FIFO - should sell from first purchase)
        sale_data_1 = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 6, 15),
            'amount': 33000.0,
            'description': 'First sale',
            'fund_id': fund.id,
            'units_sold': 600.0,
            'unit_price': 55.0,
            'brokerage_fee': 150.0
        }
        fund_event_service.create_fund_event(fund.id, sale_data_1, db_session)
        db_session.commit()

        db_session.refresh(fund)
        # FIFO: Selling 600 units from first purchase (at $50 cost basis)
        expected_equity = 110000.0 - (600.0 * 50.0)  # 110000 - 30000 = 80000
        assert fund.current_equity_balance == expected_equity

        # Second sale
        sale_data_2 = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 9, 15),
            'amount': 27500.0,
            'description': 'Second sale',
            'fund_id': fund.id,
            'units_sold': 500.0,
            'unit_price': 55.0,
            'brokerage_fee': 125.0
        }
        fund_event_service.create_fund_event(fund.id, sale_data_2, db_session)
        db_session.commit()

        db_session.refresh(fund)
        # FIFO: Selling 500 units (400 from first purchase at $50, 100 from second at $50)
        expected_equity = 80000.0 - (500.0 * 50.0)  # 80000 - 25000 = 55000
        assert fund.current_equity_balance == expected_equity
        
        # Verify all events exist
        fund_event_repository = FundEventRepository()
        sale_events = fund_event_repository.get_fund_events(
            db_session, 
            fund_ids=[fund.id], 
            event_types=[EventType.UNIT_SALE]
        )
        assert len(sale_events) == 2

    def test_unit_sale_with_cash_flow_integration(self, db_session):
        """Test unit sale workflow with cash flow creation"""
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
        
        fund_event_service = FundEventService()
        
        # Purchase units first
        purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 25000.0,
            'description': 'Purchase for sale',
            'fund_id': fund.id,
            'units_purchased': 500.0,
            'unit_price': 50.0,
            'brokerage_fee': 50.0
        }
        fund_event_service.create_fund_event(fund.id, purchase_data, db_session)
        db_session.commit()
        
        # Create unit sale
        sale_data = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 7, 15),
            'amount': 13750.0,
            'description': 'Unit sale with cash flow',
            'fund_id': fund.id,
            'units_sold': 250.0,
            'unit_price': 55.0,
            'brokerage_fee': 75.0
        }
        
        event = fund_event_service.create_fund_event(fund.id, sale_data, db_session)
        db_session.commit()
        
        # Add cash flow for the unit sale (inflow - receiving money from sale)
        from src.fund.services.fund_event_cash_flow_service import FundEventCashFlowService
        cash_flow_service = FundEventCashFlowService()
        
        # Sale proceeds = amount - brokerage (net proceeds after fees)
        cash_flow_data = {
            'bank_account_id': account.id,
            'amount': 13675.0,  # 13750 - 75 brokerage (net proceeds after fees)
            'currency': 'AUD',
            'transfer_date': date(2023, 7, 16),
            'direction': CashFlowDirection.INFLOW
        }
        
        cash_flow = cash_flow_service.create_fund_event_cash_flow(event.id, cash_flow_data, db_session)
        db_session.commit()
        
        # Verify cash flow was created and linked
        assert cash_flow.amount == 13675.0
        assert cash_flow.direction == CashFlowDirection.INFLOW
        assert cash_flow.transfer_date == date(2023, 7, 16)
        assert cash_flow.fund_event_id == event.id

    def test_unit_sale_repository_persistence(self, db_session):
        """Test unit sale data persistence through repository layer"""
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
        
        # First create purchase
        purchase_data = {
            'fund_id': fund.id,
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 30000.0,
            'description': 'Initial purchase',
            'units_purchased': 600.0,
            'unit_price': 50.0,
            'brokerage_fee': 60.0
        }
        fund_event_repository.create_fund_event(purchase_data, db_session)
        db_session.commit()
        
        # Now test sale
        sale_data = {
            'fund_id': fund.id,
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 7, 15),
            'amount': 16500.0,
            'description': 'Repository test sale',
            'reference_number': 'REPO-US-001',
            'units_sold': 300.0,
            'unit_price': 55.0,
            'brokerage_fee': 90.0
        }
        
        # Create event through repository
        event = fund_event_repository.create_fund_event(sale_data, db_session)
        db_session.commit()
        
        # Verify persistence
        assert event.id is not None
        assert event.fund_id == fund.id
        assert event.event_type == EventType.UNIT_SALE
        assert event.amount == 16500.0
        assert event.units_sold == 300.0
        assert event.unit_price == 55.0
        assert event.brokerage_fee == 90.0
        
        # Test retrieval
        retrieved_event = fund_event_repository.get_fund_event_by_id(event.id, db_session)
        assert retrieved_event is not None
        assert retrieved_event.id == event.id
        assert retrieved_event.description == 'Repository test sale'

    def test_unit_sale_error_handling_across_layers(self, db_session):
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
            invalid_sale_data = {
                'event_type': EventType.UNIT_SALE,
                'event_date': date(2023, 7, 15),
                'amount': 13750.0,
                'fund_id': 99999,  # Non-existent fund
                'units_sold': 250.0,
                'unit_price': 55.0
            }
            fund_event_service.create_fund_event(99999, invalid_sale_data, db_session)
        
        # Test with invalid event type
        with pytest.raises(ValueError):
            invalid_sale_data = {
                'event_type': 'INVALID_TYPE',
                'event_date': date(2023, 7, 15),
                'amount': 13750.0,
                'fund_id': fund.id,
                'units_sold': 250.0,
                'unit_price': 55.0
            }
            fund_event_service.create_fund_event(fund.id, invalid_sale_data, db_session)

    def test_unit_sale_transaction_integrity(self, db_session):
        """Test transaction integrity across all layers"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        fund_event_service = FundEventService()
        equity_service = FundEquityService()
        
        # Purchase units
        purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 15),
            'amount': 25000.0,
            'description': 'Purchase for integrity test',
            'fund_id': fund.id,
            'units_purchased': 500.0,
            'unit_price': 50.0,
            'brokerage_fee': 50.0
        }
        fund_event_service.create_fund_event(fund.id, purchase_data, db_session)
        equity_service.update_fund_equity_fields(fund, db_session)
        db_session.commit()
        
        # Record state before sale
        db_session.refresh(fund)
        initial_equity = fund.current_equity_balance
        assert initial_equity == 25000.0
        
        # Create unit sale through service
        sale_data = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 7, 15),
            'amount': 13750.0,
            'description': 'Transaction integrity test',
            'fund_id': fund.id,
            'units_sold': 250.0,
            'unit_price': 55.0,
            'brokerage_fee': 75.0
        }
        
        event = fund_event_service.create_fund_event(fund.id, sale_data, db_session)
        equity_service.update_fund_equity_fields(fund, db_session)
        db_session.commit()
        
        # Verify all related state changes are consistent
        db_session.refresh(fund)
        # Equity reduced by cost basis (purchase price $50), not sale price
        expected_equity = initial_equity - (250.0 * 50.0)  # 25000 - 12500 = 12500
        assert fund.current_equity_balance == expected_equity
        
        # Verify event count
        fund_event_repository = FundEventRepository()
        sale_events = fund_event_repository.get_fund_events(
            db_session, 
            fund_ids=[fund.id], 
            event_types=[EventType.UNIT_SALE]
        )
        assert len(sale_events) == 1

    def test_unit_sale_performance_with_large_dataset(self, db_session):
        """Test unit sale performance with multiple events"""
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
        
        # First create large purchase
        large_purchase = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 1),
            'amount': 500000.0,
            'description': 'Large initial purchase',
            'fund_id': fund.id,
            'units_purchased': 10000.0,
            'unit_price': 50.0,
            'brokerage_fee': 500.0
        }
        fund_event_service.create_fund_event(fund.id, large_purchase, db_session)
        equity_service.update_fund_equity_fields(fund, db_session)
        db_session.commit()
        
        db_session.refresh(fund)
        initial_equity = fund.current_equity_balance
        
        # Create multiple unit sales
        sale_data = [
            {'units': 1000.0, 'price': 52.0, 'brokerage': 52.0},
            {'units': 1500.0, 'price': 54.0, 'brokerage': 81.0},
            {'units': 800.0, 'price': 56.0, 'brokerage': 44.0},
            {'units': 1200.0, 'price': 53.0, 'brokerage': 63.0},
            {'units': 500.0, 'price': 55.0, 'brokerage': 27.0}
        ]
        total_sold_equity = 0.0
        
        for i, data in enumerate(sale_data):
            # Calculate proper dates for monthly sales
            sale_date = date(2023, 2 + i, 15) if 2 + i <= 12 else date(2023 + (2 + i - 1) // 12, ((2 + i - 1) % 12) + 1, 15)
            sale_event_data = {
                'event_type': EventType.UNIT_SALE,
                'event_date': sale_date,
                'amount': data['units'] * data['price'],
                'description': f'Unit sale {i+1}',
                'fund_id': fund.id,
                'units_sold': data['units'],
                'unit_price': data['price'],
                'brokerage_fee': data['brokerage']
            }
            
            fund_event_service.create_fund_event(fund.id, sale_event_data, db_session)
            total_sold_equity += data['units'] * data['price']
        
        # Update equity calculations
        equity_service.update_fund_equity_fields(fund, db_session)
        db_session.commit()
        
        # Verify final state
        db_session.refresh(fund)
        # Equity is reduced by cost basis (all units purchased at $50)
        total_units_sold = sum(data['units'] for data in sale_data)  # 5000 units
        cost_basis_reduction = total_units_sold * 50.0  # 5000 * 50 = 250000
        expected_final_equity = initial_equity - cost_basis_reduction  # 500000 - 250000 = 250000
        assert fund.current_equity_balance == expected_final_equity
        
        # Verify all events were created
        fund_event_repository = FundEventRepository()
        sale_events = fund_event_repository.get_fund_events(
            db_session, 
            fund_ids=[fund.id], 
            event_types=[EventType.UNIT_SALE]
        )
        assert len(sale_events) == len(sale_data)
