"""
Integration tests for fund tax statement workflow through all refactored layers.

This file tests the complete fund tax statement workflow from API route through
all refactored layers: Routes -> Controllers -> Services -> Repositories.

Tests cover:
- API route validation and request handling
- Controller orchestration and response formatting
- Service business logic and validation
- Repository data persistence
- Tax calculation logic and event creation
- Financial year calculations
- Debt cost calculations
- Capital gains calculations
- Error handling across all layers
- Validation of business rules
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from tests.factories import (
    FundFactory, EntityFactory, InvestmentCompanyFactory,
    BankFactory, BankAccountFactory, RiskFreeRateFactory
)
from src.fund.models import Fund, FundTaxStatement, FundEvent
from src.fund.enums import FundTrackingType, EventType, TaxPaymentType, GroupType, DistributionType, FundTaxStatementFinancialYearType
from src.fund.services.fund_tax_statement_service import FundTaxStatementService
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.services.fund_event_service import FundEventService
from src.fund.repositories.fund_tax_statement_repository import FundTaxStatementRepository
from src.fund.repositories.fund_event_repository import FundEventRepository
from src.fund.repositories.fund_repository import FundRepository
from src.api.dto.response_codes import ApiResponseCode


class TestTaxStatementWorkflowIntegration:
    """Test complete fund tax statement workflow through all refactored layers"""

    def test_tax_statement_creation_basic_flow(self, db_session):
        """Test basic tax statement creation through service layer flow"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, RiskFreeRateFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund and entity
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            currency='AUD',
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        entity = EntityFactory.create()
        db_session.commit()
        
        # Test data for tax statement
        tax_statement_data = {
            'entity_id': entity.id,
            'financial_year': '2023',
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            
            # Interest income data
            'interest_received_in_cash': 5000.0,
            'interest_income_tax_rate': 30.0,
            'interest_non_resident_withholding_tax_from_statement': 1000.0,
            
            # Dividend income data
            'dividend_franked_income_amount': 3000.0,
            'dividend_franked_income_tax_rate': 25.0,
            'dividend_unfranked_income_amount': 2000.0,
            'dividend_unfranked_income_tax_rate': 30.0,
            
            # Capital gains data
            'capital_gain_income_amount': 10000.0,
            'capital_gain_income_tax_rate': 20.0,
            
            # Debt cost data
            'eofy_debt_interest_deduction_rate': 30.0,
            
            # Additional fields
            'accountant': 'Test Accountant',
            'notes': 'Test tax statement for FY 2023'
        }
        
        # Test through service layer
        tax_statement_service = FundTaxStatementService()
        tax_statement = tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data, db_session
        )
        
        db_session.commit()
        
        # Verify tax statement creation
        assert tax_statement.fund_id == fund.id
        assert tax_statement.entity_id == entity.id
        assert tax_statement.financial_year == '2023'
        assert tax_statement.financial_year_start_date == date(2022, 7, 1)  # July 1, 2022 (year before)
        assert tax_statement.financial_year_end_date == date(2023, 6, 30)   # June 30, 2023 (end year)
        assert tax_statement.statement_date == date(2024, 7, 15)
        assert tax_statement.tax_payment_date == date(2024, 7, 31)
        
        # Verify calculated fields
        assert tax_statement.interest_income_amount == 5000.0
        assert tax_statement.interest_income_tax_rate == 30.0
        assert tax_statement.interest_tax_amount == 500.0  # (5000 * 0.30) - 1000
        assert tax_statement.interest_non_resident_withholding_tax_from_statement == 1000.0
        
        assert tax_statement.dividend_franked_income_amount == 3000.0
        assert tax_statement.dividend_franked_income_tax_rate == 25.0
        assert tax_statement.dividend_franked_tax_amount == 750.0  # 3000 * 0.25
        
        assert tax_statement.dividend_unfranked_income_amount == 2000.0
        assert tax_statement.dividend_unfranked_income_tax_rate == 30.0
        assert tax_statement.dividend_unfranked_tax_amount == 600.0  # 2000 * 0.30
        
        assert tax_statement.capital_gain_income_amount == 10000.0
        assert tax_statement.capital_gain_income_tax_rate == 20.0
        
        assert tax_statement.eofy_debt_interest_deduction_rate == 30.0
        assert tax_statement.accountant == 'Test Accountant'
        assert tax_statement.notes == 'Test tax statement for FY 2023'

    def test_tax_statement_creation_with_auto_calculated_dividends(self, db_session):
        """Test tax statement creation with auto-calculated dividend amounts"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund and entity
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        entity = EntityFactory.create()
        db_session.commit()
        
        # Create some dividend distribution events first
        fund_event_service = FundEventService()
        
        # Create franked dividend distribution (within financial year 2023: July 1, 2022 - June 30, 2023)
        franked_dividend_data = {
            'event_type': EventType.DISTRIBUTION,
            'distribution_type': DistributionType.DIVIDEND_FRANKED,
            'event_date': date(2023, 3, 15),  # Within the financial year
            'amount': 1500.0,
            'description': 'Franked dividend distribution',
            'reference_number': 'FD-001',
            'has_withholding_tax': False
        }
        fund_event_service.create_fund_event(fund.id, franked_dividend_data, db_session)
        
        # Create unfranked dividend distribution (within financial year 2023: July 1, 2022 - June 30, 2023)
        unfranked_dividend_data = {
            'event_type': EventType.DISTRIBUTION,
            'distribution_type': DistributionType.DIVIDEND_UNFRANKED,
            'event_date': date(2023, 6, 15),  # Within the financial year
            'amount': 800.0,
            'description': 'Unfranked dividend distribution',
            'reference_number': 'UD-001',
            'has_withholding_tax': False
        }
        fund_event_service.create_fund_event(fund.id, unfranked_dividend_data, db_session)
        
        db_session.commit()
        
        # Test data for tax statement (without dividend amounts - should be auto-calculated)
        tax_statement_data = {
            'entity_id': entity.id,
            'financial_year': '2023',
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            
            # Dividend tax rates (amounts should be auto-calculated)
            'dividend_franked_income_tax_rate': 25.0,
            'dividend_unfranked_income_tax_rate': 30.0,
            
            # Other required fields
            'interest_income_amount': 0.0,
            'interest_income_tax_rate': 0.0,
            'capital_gain_income_amount': 0.0,
            'capital_gain_income_tax_rate': 0.0,
            'eofy_debt_interest_deduction_rate': 0.0
        }
        
        # Test through service layer
        tax_statement_service = FundTaxStatementService()
        tax_statement = tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data, db_session
        )
        
        db_session.commit()
        
        # Verify auto-calculated dividend amounts
        assert tax_statement.dividend_franked_income_amount == 1500.0
        assert tax_statement.dividend_franked_income_amount_from_tax_statement_flag == False
        assert tax_statement.dividend_franked_tax_amount == 375.0  # 1500 * 0.25
        
        assert tax_statement.dividend_unfranked_income_amount == 800.0
        assert tax_statement.dividend_unfranked_income_amount_from_tax_statement_flag == False
        assert tax_statement.dividend_unfranked_tax_amount == 240.0  # 800 * 0.30

    def test_tax_statement_creation_with_capital_gains_calculation(self, db_session):
        """Test tax statement creation with auto-calculated capital gains for NAV-based fund"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund and entity
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        entity = EntityFactory.create()
        db_session.commit()
        
        # Create some unit purchase and sale events to generate capital gains
        fund_event_service = FundEventService()
        
        # Create unit purchase (within financial year 2023: July 1, 2022 - June 30, 2023)
        unit_purchase_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'event_date': date(2023, 1, 1),  # Within the financial year
            'amount': 50000.0,
            'description': 'Unit purchase',
            'reference_number': 'UP-001',
            'units_purchased': 1000.0,
            'unit_price': 50.0,
            'brokerage_fee': 100.0
        }
        fund_event_service.create_fund_event(fund.id, unit_purchase_data, db_session)
        
        # Create unit sale (should generate capital gain) - within financial year 2023: July 1, 2022 - June 30, 2023
        unit_sale_data = {
            'event_type': EventType.UNIT_SALE,
            'event_date': date(2023, 5, 1),  # Within the financial year, after purchase
            'amount': 55000.0,
            'description': 'Unit sale',
            'reference_number': 'US-001',
            'units_sold': 1000.0,
            'unit_price': 55.0,
            'brokerage_fee': 150.0
        }
        fund_event_service.create_fund_event(fund.id, unit_sale_data, db_session)
        
        db_session.commit()
        
        # Test data for tax statement (without capital gains amount - should be auto-calculated)
        tax_statement_data = {
            'entity_id': entity.id,
            'financial_year': '2023',
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            
            # Capital gains tax rate (amount should be auto-calculated)
            'capital_gain_income_tax_rate': 20.0,
            
            # Other required fields
            'interest_income_amount': 0.0,
            'interest_income_tax_rate': 0.0,
            'dividend_franked_income_amount': 0.0,
            'dividend_franked_income_tax_rate': 0.0,
            'dividend_unfranked_income_amount': 0.0,
            'dividend_unfranked_income_tax_rate': 0.0,
            'eofy_debt_interest_deduction_rate': 0.0
        }
        
        # Test through service layer
        tax_statement_service = FundTaxStatementService()
        tax_statement = tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data, db_session
        )
        
        db_session.commit()
        
        # Verify auto-calculated capital gains
        # Expected: (55000 - 150) - (50000 + 100) = 4750
        assert tax_statement.capital_gain_income_amount > 0
        assert tax_statement.capital_gain_income_amount_from_tax_statement_flag == False

    def test_tax_statement_validation_entity_not_found(self, db_session):
        """Test tax statement creation validation with non-existent entity"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        db_session.commit()
        
        # Test data with non-existent entity ID
        tax_statement_data = {
            'entity_id': 99999,  # Non-existent entity
            'financial_year': '2023',
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            'interest_income_amount': 5000.0,
            'interest_income_tax_rate': 30.0,
            'dividend_franked_income_amount': 0.0,
            'dividend_franked_income_tax_rate': 0.0,
            'dividend_unfranked_income_amount': 0.0,
            'dividend_unfranked_income_tax_rate': 0.0,
            'capital_gain_income_amount': 0.0,
            'capital_gain_income_tax_rate': 0.0,
            'eofy_debt_interest_deduction_rate': 0.0
        }
        
        # Test through service layer - should raise ValueError
        tax_statement_service = FundTaxStatementService()
        
        with pytest.raises(ValueError, match="Entity not found"):
            tax_statement_service.create_fund_tax_statement(
                fund.id, tax_statement_data, db_session
            )

    def test_tax_statement_validation_invalid_financial_year(self, db_session):
        """Test tax statement creation validation with invalid financial year"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund and entity
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        entity = EntityFactory.create()
        db_session.commit()
        
        # Test data with invalid financial year format
        tax_statement_data = {
            'entity_id': entity.id,
            'financial_year': 'invalid-year',  # Invalid format
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            'interest_received_in_cash': 5000.0,
            'interest_income_tax_rate': 30.0,
            'dividend_franked_income_amount': 0.0,
            'dividend_franked_income_tax_rate': 0.0,
            'dividend_unfranked_income_amount': 0.0,
            'dividend_unfranked_income_tax_rate': 0.0,
            'capital_gain_income_amount': 0.0,
            'capital_gain_income_tax_rate': 0.0,
            'eofy_debt_interest_deduction_rate': 0.0
        }
        
        # Test through service layer - should raise ValueError from FinancialYearCalculator
        tax_statement_service = FundTaxStatementService()
        
        with pytest.raises((ValueError, Exception)):  # FinancialYearCalculator may raise different exceptions
            tax_statement_service.create_fund_tax_statement(
                fund.id, tax_statement_data, db_session
            )

    def test_tax_statement_deletion_validation(self, db_session):
        """Test tax statement deletion validation and cleanup"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund, entity, and tax statement
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        entity = EntityFactory.create()
        db_session.commit()
        
        # Create tax statement
        tax_statement_data = {
            'entity_id': entity.id,
            'financial_year': '2023',
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            'interest_received_in_cash': 5000.0,
            'interest_income_tax_rate': 30.0,
            'dividend_franked_income_amount': 0.0,
            'dividend_franked_income_tax_rate': 0.0,
            'dividend_unfranked_income_amount': 0.0,
            'dividend_unfranked_income_tax_rate': 0.0,
            'capital_gain_income_amount': 0.0,
            'capital_gain_income_tax_rate': 0.0,
            'eofy_debt_interest_deduction_rate': 0.0
        }
        
        tax_statement_service = FundTaxStatementService()
        tax_statement = tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data, db_session
        )
        db_session.commit()
        
        # Verify tax statement was created
        assert tax_statement.id is not None
        
        # Test deletion
        success = tax_statement_service.delete_fund_tax_statement(
            tax_statement.id, db_session
        )
        
        assert success == True
        
        # Verify tax statement was deleted
        deleted_tax_statement = tax_statement_service.get_fund_tax_statement_by_id(
            tax_statement.id, db_session
        )
        assert deleted_tax_statement is None

    def test_tax_statement_deletion_non_existent(self, db_session):
        """Test tax statement deletion with non-existent ID"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        db_session.commit()
        
        # Test deletion of non-existent tax statement
        tax_statement_service = FundTaxStatementService()
        
        with pytest.raises(ValueError, match="Fund tax statement not found"):
            tax_statement_service.delete_fund_tax_statement(99999, db_session)

    def test_tax_statement_retrieval_by_filters(self, db_session):
        """Test tax statement retrieval with various filters"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create multiple funds and entities
        fund1 = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        fund2 = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=200000.0,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        entity1 = EntityFactory.create()
        entity2 = EntityFactory.create()
        db_session.commit()
        
        # Create tax statements for different combinations
        tax_statement_service = FundTaxStatementService()
        
        # Tax statement 1: Fund1, Entity1, FY 2023
        tax_statement_data_1 = {
            'entity_id': entity1.id,
            'financial_year': '2023',
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            'interest_income_amount': 5000.0,
            'interest_income_tax_rate': 30.0,
            'dividend_franked_income_amount': 0.0,
            'dividend_franked_income_tax_rate': 0.0,
            'dividend_unfranked_income_amount': 0.0,
            'dividend_unfranked_income_tax_rate': 0.0,
            'capital_gain_income_amount': 0.0,
            'capital_gain_income_tax_rate': 0.0,
            'eofy_debt_interest_deduction_rate': 0.0
        }
        tax_statement1 = tax_statement_service.create_fund_tax_statement(
            fund1.id, tax_statement_data_1, db_session
        )
        
        # Tax statement 2: Fund1, Entity2, FY 2024
        tax_statement_data_2 = {
            'entity_id': entity2.id,
            'financial_year': '2024',
            'statement_date': date(2025, 7, 15),
            'tax_payment_date': date(2025, 7, 31),
            'interest_income_amount': 3000.0,
            'interest_income_tax_rate': 30.0,
            'dividend_franked_income_amount': 0.0,
            'dividend_franked_income_tax_rate': 0.0,
            'dividend_unfranked_income_amount': 0.0,
            'dividend_unfranked_income_tax_rate': 0.0,
            'capital_gain_income_amount': 0.0,
            'capital_gain_income_tax_rate': 0.0,
            'eofy_debt_interest_deduction_rate': 0.0
        }
        tax_statement2 = tax_statement_service.create_fund_tax_statement(
            fund1.id, tax_statement_data_2, db_session
        )
        
        # Tax statement 3: Fund2, Entity1, FY 2023
        tax_statement_data_3 = {
            'entity_id': entity1.id,
            'financial_year': '2023',
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            'interest_received_in_cash': 7000.0,
            'interest_income_tax_rate': 30.0,
            'dividend_franked_income_amount': 0.0,
            'dividend_franked_income_tax_rate': 0.0,
            'dividend_unfranked_income_amount': 0.0,
            'dividend_unfranked_income_tax_rate': 0.0,
            'capital_gain_income_amount': 0.0,
            'capital_gain_income_tax_rate': 0.0,
            'eofy_debt_interest_deduction_rate': 0.0
        }
        tax_statement3 = tax_statement_service.create_fund_tax_statement(
            fund2.id, tax_statement_data_3, db_session
        )
        
        db_session.commit()
        
        # Test retrieval by fund_id
        fund1_statements = tax_statement_service.get_fund_tax_statements(
            fund_id=fund1.id, session=db_session
        )
        assert len(fund1_statements) == 2
        assert all(stmt.fund_id == fund1.id for stmt in fund1_statements)
        
        # Test retrieval by entity_id
        entity1_statements = tax_statement_service.get_fund_tax_statements(
            entity_id=entity1.id, session=db_session
        )
        assert len(entity1_statements) == 2
        assert all(stmt.entity_id == entity1.id for stmt in entity1_statements)
        
        # Test retrieval by financial_year
        fy_2023_24_statements = tax_statement_service.get_fund_tax_statements(
            financial_year='2023', session=db_session
        )
        assert len(fy_2023_24_statements) == 2
        assert all(stmt.financial_year == '2023' for stmt in fy_2023_24_statements)
        
        # Test retrieval by combined filters
        combined_statements = tax_statement_service.get_fund_tax_statements(
            fund_id=fund1.id, entity_id=entity1.id, financial_year='2023', session=db_session
        )
        assert len(combined_statements) == 1
        assert combined_statements[0].id == tax_statement1.id

    def test_tax_statement_duplicate_prevention(self, db_session):
        """Test that duplicate tax statements for same fund/entity/financial year are prevented"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund and entity
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        entity = EntityFactory.create()
        db_session.commit()
        
        # Create first tax statement
        tax_statement_data = {
            'entity_id': entity.id,
            'financial_year': '2023',
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            'interest_received_in_cash': 5000.0,
            'interest_income_tax_rate': 30.0,
            'dividend_franked_income_amount': 0.0,
            'dividend_franked_income_tax_rate': 0.0,
            'dividend_unfranked_income_amount': 0.0,
            'dividend_unfranked_income_tax_rate': 0.0,
            'capital_gain_income_amount': 0.0,
            'capital_gain_income_tax_rate': 0.0,
            'eofy_debt_interest_deduction_rate': 0.0
        }
        
        tax_statement_service = FundTaxStatementService()
        tax_statement1 = tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data, db_session
        )
        db_session.commit()
        
        # Try to create duplicate tax statement - should raise IntegrityError
        from sqlalchemy.exc import IntegrityError
        
        with pytest.raises(IntegrityError):
            tax_statement_service.create_fund_tax_statement(
                fund.id, tax_statement_data, db_session
            )
            db_session.commit()

    def test_tax_statement_tax_payment_events_creation(self, db_session):
        """Test that tax payment events are created correctly for tax statement"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund and entity
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        entity = EntityFactory.create()
        db_session.commit()
        
        # Test data for tax statement with multiple income types
        tax_statement_data = {
            'entity_id': entity.id,
            'financial_year': '2023',
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            
            # Interest income data
            'interest_received_in_cash': 5000.0,
            'interest_income_tax_rate': 30.0,
            'interest_non_resident_withholding_tax_from_statement': 1000.0,
            
            # Dividend income data
            'dividend_franked_income_amount': 3000.0,
            'dividend_franked_income_tax_rate': 25.0,
            'dividend_unfranked_income_amount': 2000.0,
            'dividend_unfranked_income_tax_rate': 30.0,
            
            # Capital gains data
            'capital_gain_income_amount': 10000.0,
            'capital_gain_income_tax_rate': 20.0,
            
            # Debt cost data
            'eofy_debt_interest_deduction_rate': 30.0
        }
        
        # Test through service layer
        tax_statement_service = FundTaxStatementService()
        tax_statement = tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data, db_session
        )
        
        db_session.commit()
        
        # Verify tax payment events were created
        fund_event_repository = FundEventRepository()
        tax_payment_events = fund_event_repository.get_fund_events(
            fund_ids=[fund.id],
            event_types=[EventType.TAX_PAYMENT],
            session=db_session
        )
        
        # Should have multiple tax payment events (interest, franked dividend, unfranked dividend, capital gains)
        assert len(tax_payment_events) >= 3  # At least interest, franked, unfranked, capital gains
        
        # Verify event types and amounts
        tax_payment_types = [event.tax_payment_type for event in tax_payment_events]
        assert TaxPaymentType.EOFY_INTEREST_TAX in tax_payment_types
        assert TaxPaymentType.DIVIDENDS_FRANKED_TAX in tax_payment_types
        assert TaxPaymentType.DIVIDENDS_UNFRANKED_TAX in tax_payment_types
        assert TaxPaymentType.CAPITAL_GAINS_TAX in tax_payment_types
        
        # Verify events are grouped
        grouped_events = [event for event in tax_payment_events if event.is_grouped]
        assert len(grouped_events) > 0
        assert all(event.group_type == GroupType.TAX_STATEMENT for event in grouped_events)
        
        # Verify tax statement ID is set
        assert all(event.tax_statement_id == tax_statement.id for event in tax_payment_events)

    def test_tax_statement_with_zero_tax_rates(self, db_session):
        """Test tax statement creation with zero tax rates (should not create tax payment events)"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund and entity
        fund = FundFactory.create(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=100000.0,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.HALF_YEAR
        )
        entity = EntityFactory.create()
        db_session.commit()
        
        # Test data for tax statement with zero tax rates
        tax_statement_data = {
            'entity_id': entity.id,
            'financial_year': '2023',
            'statement_date': date(2024, 7, 15),
            'tax_payment_date': date(2024, 7, 31),
            
            # Income data with zero tax rates
            'interest_received_in_cash': 5000.0,
            'interest_income_tax_rate': 0.0,  # Zero tax rate
            
            'dividend_franked_income_amount': 3000.0,
            'dividend_franked_income_tax_rate': 0.0,  # Zero tax rate
            
            'dividend_unfranked_income_amount': 2000.0,
            'dividend_unfranked_income_tax_rate': 0.0,  # Zero tax rate
            
            'capital_gain_income_amount': 10000.0,
            'capital_gain_income_tax_rate': 0.0,  # Zero tax rate
            
            'eofy_debt_interest_deduction_rate': 0.0
        }
        
        # Test through service layer
        tax_statement_service = FundTaxStatementService()
        tax_statement = tax_statement_service.create_fund_tax_statement(
            fund.id, tax_statement_data, db_session
        )
        
        db_session.commit()
        
        # Verify tax statement was created
        assert tax_statement.id is not None
        
        # Verify no tax payment events were created (since all tax rates are zero)
        fund_event_repository = FundEventRepository()
        tax_payment_events = fund_event_repository.get_fund_events(
            fund_ids=[fund.id],
            event_types=[EventType.TAX_PAYMENT],
            session=db_session
        )
        
        assert len(tax_payment_events) == 0
        
        # Verify tax amounts are zero
        assert tax_statement.interest_tax_amount == 0.0
        assert tax_statement.dividend_franked_tax_amount == 0.0
        assert tax_statement.dividend_unfranked_tax_amount == 0.0
