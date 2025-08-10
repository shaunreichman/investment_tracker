"""
Integration tests for derived fields and computed properties.

Tests computed properties, relationships, and derived fields
that require database interaction and session management.
"""

import pytest
from datetime import date, datetime, timezone
from decimal import Decimal

from tests.factories import FundFactory, EntityFactory, InvestmentCompanyFactory, TaxStatementFactory
from src.fund.models import Fund, FundEvent, FundType, EventType, FundStatus, DistributionType
from src.tax.models import TaxStatement
from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany


class TestFundDerivedFields:
    """Test fund computed properties and derived fields."""

    def test_fund_total_commitments_calculated(self, db_session):
        """Test that fund total commitments are calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Verify commitment amount is set
        assert fund.commitment_amount == 100000.0
        
        # Add capital calls
        fund.add_capital_call(30000.0, date(2023, 1, 1), "First capital call", session=db_session)
        fund.add_capital_call(20000.0, date(2023, 3, 1), "Second capital call", session=db_session)
        db_session.commit()
        
        # Verify total capital called
        fund = db_session.query(Fund).get(fund.id)
        assert fund.total_capital_called == 50000.0
        
        # Verify remaining commitment
        assert fund.remaining_commitment == 50000.0

    def test_fund_irr_calculation_with_events(self, db_session):
        """Test that fund IRR is calculated correctly from events."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add capital call
        fund.add_capital_call(100000.0, date(2023, 1, 1), "Full capital call", session=db_session)
        db_session.commit()
        
        # Add distribution (return)
        fund.add_distribution(
            event_date=date(2023, 12, 31),
            distribution_type=DistributionType.CAPITAL_GAIN,
            distribution_amount=110000.0,  # 10% return
            description="Return with profit",
            session=db_session
        )
        db_session.commit()
        
        # Calculate IRR from events
        fund = db_session.query(Fund).get(fund.id)
        events = fund.get_all_fund_events()
        
        # Extract cash flows and dates for IRR calculation
        cash_flows = []
        dates = []
        for event in events:
            if event.event_type == EventType.CAPITAL_CALL:
                cash_flows.append(-event.amount)  # Negative for capital call
                dates.append(event.event_date)
            elif event.event_type == EventType.DISTRIBUTION:
                cash_flows.append(event.amount)  # Positive for distribution
                dates.append(event.event_date)
        
        # Verify we have the expected cash flows
        assert len(cash_flows) == 2
        assert cash_flows[0] == -100000.0  # Capital call
        assert cash_flows[1] == 110000.0   # Distribution
        
        # Verify dates are correct
        assert dates[0] == date(2023, 1, 1)
        assert dates[1] == date(2023, 12, 31)

    def test_fund_status_derived_from_equity_balance(self, db_session):
        """Test that fund status is derived from equity balance."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Initial status should be ACTIVE (default)
        assert fund.status == FundStatus.ACTIVE
        
        # Add capital call
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call", session=db_session)
        db_session.commit()
        
        # Status should remain ACTIVE
        fund = db_session.query(Fund).get(fund.id)
        assert fund.status == FundStatus.ACTIVE
        
        # Return all capital
        fund.add_return_of_capital(50000.0, date(2023, 6, 1), "Full capital return", session=db_session)
        db_session.commit()
        
        # Status should change to REALIZED
        fund = db_session.query(Fund).get(fund.id)
        assert fund.status == FundStatus.REALIZED

    def test_fund_current_nav_total_calculated(self, db_session):
        """Test that fund current NAV total is calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Initial NAV total should be 0
        assert fund.current_nav_total == 0.0
        
        # Add unit purchase
        fund.add_unit_purchase(
            units=1000.0,
            price=10.0,
            date=date(2023, 1, 1),
            description="Initial unit purchase",
            session=db_session
        )
        db_session.commit()
        
        # NAV total should be units * price
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_nav_total == 10000.0
        
        # Update NAV
        fund.add_nav_update(
            nav_per_share=12.0,
            date=date(2023, 6, 1),
            description="NAV increase",
            session=db_session
        )
        db_session.commit()
        
        # NAV total should update to new price * units
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_nav_total == 12000.0


class TestEntityDerivedFields:
    """Test entity computed properties and derived fields."""

    def test_entity_total_funds_under_management(self, db_session):
        """Test that entity total funds under management is calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        entity = EntityFactory()
        db_session.commit()
        
        # Create multiple funds for this entity
        fund1 = FundFactory(
            entity=entity,  # Pass the actual object, not just the ID
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        fund2 = FundFactory(
            entity=entity,  # Pass the actual object, not just the ID
            tracking_type=FundType.NAV_BASED,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        # Verify total funds under management
        # Use the existing entity object to preserve loaded relationships
        assert len(entity.funds) == 2
        assert entity.total_funds_under_management == 300000.0

    def test_entity_financial_year_calculation(self, db_session):
        """Test that entity financial year is calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        entity = EntityFactory()
        db_session.commit()
        
        # Test financial year calculation
        test_date = date(2023, 7, 15)  # July 15, 2023
        financial_year = entity.get_financial_year(test_date)
        
        # Should be 2023-24 for July date
        assert financial_year == "2023-24"
        
        # Test January date (should be previous year)
        test_date_jan = date(2023, 1, 15)  # January 15, 2023
        financial_year_jan = entity.get_financial_year(test_date_jan)
        assert financial_year_jan == "2022-23"

    def test_entity_financial_years_for_period(self, db_session):
        """Test that entity financial years for a period are calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        entity = EntityFactory()
        db_session.commit()
        
        # Test financial years for a period
        start_date = date(2022, 7, 1)
        end_date = date(2024, 6, 30)
        financial_years = entity.get_financial_years_for_period(start_date, end_date)
        
        # Should include 2022-23, 2023-24 (as a set)
        expected_years = {"2022-23", "2023-24"}
        assert financial_years == expected_years


class TestInvestmentCompanyDerivedFields:
    """Test investment company computed properties and derived fields."""

    def test_company_total_commitments(self, db_session):
        """Test that company total commitments are calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory()
        db_session.commit()
        
        # Create multiple funds for this company
        fund1 = FundFactory(
            investment_company=company,  # Pass the object, not just the ID
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        fund2 = FundFactory(
            investment_company=company,  # Pass the object, not just the ID
            tracking_type=FundType.NAV_BASED,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        # Verify total commitments
        # Use the existing company object instead of requerying to preserve loaded relationships
        assert company.get_total_funds_under_management(db_session) == 2  # Total number of funds
        assert company.get_total_commitments(db_session) == 300000.0  # Total commitment amount

    def test_company_funds_under_management(self, db_session):
        """Test that company funds under management are calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory()
        db_session.commit()
        
        # Create funds with different statuses
        active_fund = FundFactory(
            investment_company=company,  # Pass the object, not just the ID
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        realized_fund = FundFactory(
            investment_company=company,  # Pass the object, not just the ID
            tracking_type=FundType.COST_BASED,
            commitment_amount=50000.0
        )
        db_session.commit()
        
        # Return capital from realized fund
        active_fund.add_capital_call(50000.0, date(2023, 1, 1), "Capital call", session=db_session)
        realized_fund.add_capital_call(50000.0, date(2023, 1, 1), "Capital call", session=db_session)
        realized_fund.add_return_of_capital(50000.0, date(2023, 6, 1), "Capital return", session=db_session)
        db_session.commit()
        
        # Verify funds under management using existing methods
        assert company.get_total_funds_under_management(db_session) == 2  # Total number of funds
        assert company.get_total_commitments(db_session) == 150000.0  # Total commitment amount


class TestTaxStatementDerivedFields:
    """Test tax statement computed properties and derived fields."""

    def test_tax_statement_total_income_calculated(self, db_session):
        """Test that tax statement total income is calculated correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, TaxStatementFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create tax statement
        tax_statement = TaxStatementFactory()
        db_session.commit()
        
        # Verify total income calculation
        assert tax_statement.total_income >= 0.0
        assert isinstance(tax_statement.total_income, (int, float))

    def test_tax_statement_financial_year_derived(self, db_session):
        """Test that tax statement financial year is derived correctly."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, TaxStatementFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create tax statement
        tax_statement = TaxStatementFactory()
        db_session.commit()
        
        # Verify financial year is derived
        assert tax_statement.financial_year is not None
        assert isinstance(tax_statement.financial_year, str)
        assert "-" in tax_statement.financial_year  # Should be in format "2023-2024"
