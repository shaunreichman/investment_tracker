"""
Company Portfolio Workflow Integration Tests.

This module tests the complete company portfolio workflow from API to database,
ensuring all layers (API, Services, Repositories, Models) work together correctly.

Key testing areas:
- Complete portfolio management workflow
- Fund creation and coordination workflow
- Portfolio operations (add/remove/update funds)
- Cross-domain coordination between company and fund domains
- Event system integration for portfolio updates
- Portfolio summary calculations and updates
- Data consistency validation across domains
"""

import pytest
from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from typing import Dict, Any
from decimal import Decimal

from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.services import CompanyService
from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.services.fund_coordination_service import FundCoordinationService
from src.investment_company.services.company_calculation_service import CompanyCalculationService
from src.investment_company.enums import CompanyType, CompanyStatus
from src.fund.models import Fund, FundEvent
from src.fund.enums import FundStatus, FundType, EventType
from src.entity.models import Entity
from tests.factories import InvestmentCompanyFactory, ContactFactory, FundFactory, EntityFactory, FundEventFactory


class TestCompanyPortfolioWorkflow:
    """Test complete company portfolio workflow from API to database."""
    
    def test_complete_portfolio_creation_workflow(self, db_session: Session):
        """Test the complete portfolio creation workflow through all layers."""
        # Arrange: Prepare company, entity, and fund data
        company_data = {
            'name': 'Portfolio Test Company',
            'description': 'Company for portfolio workflow testing',
            'company_type': CompanyType.PRIVATE_EQUITY,
            'status': CompanyStatus.ACTIVE
        }
        
        entity_data = {
            'name': 'Portfolio Test Entity',
            'description': 'Entity for portfolio testing',
            'tax_jurisdiction': 'AU'
        }
        
        fund_data = {
            'name': 'Portfolio Test Fund',
            'fund_type': FundType.NAV_BASED.value,
            'tracking_type': FundType.NAV_BASED.value,
            'currency': 'AUD',
            'description': 'Fund for portfolio testing',
            'commitment_amount': 2500000.0,
            'expected_irr': 15.0,
            'expected_duration_months': 84
        }
        
        # Act: Create company through service layer
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            status=company_data['status'],
            session=db_session
        )
        
        # Create entity
        entity = Entity(
            name=entity_data['name'],
            description=entity_data['description'],
            tax_jurisdiction=entity_data['tax_jurisdiction']
        )
        db_session.add(entity)
        db_session.flush()
        
        # Create fund through portfolio service
        portfolio_service = CompanyPortfolioService()
        fund = portfolio_service.create_fund(
            company=company,
            entity=entity,
            name=fund_data['name'],
            fund_type=fund_data['fund_type'],
            tracking_type=fund_data['tracking_type'],
            currency=fund_data['currency'],
            description=fund_data['description'],
            commitment_amount=fund_data['commitment_amount'],
            expected_irr=fund_data['expected_irr'],
            expected_duration_months=fund_data['expected_duration_months'],
            session=db_session
        )
        
        # Assert: Verify complete portfolio setup
        assert company is not None
        assert company.id is not None
        assert entity is not None
        assert entity.id is not None
        assert fund is not None
        assert fund.id is not None
        
        # Verify fund relationships
        assert fund.investment_company_id == company.id
        assert fund.entity_id == entity.id
        assert fund.status == FundStatus.ACTIVE
        
        # Verify company portfolio
        assert len(company.funds) == 1
        assert company.funds[0].id == fund.id
        
        # Verify portfolio calculations
        total_funds = portfolio_service.get_total_funds_under_management(company, db_session)
        total_commitments = portfolio_service.get_total_commitments(company, db_session)
        
        assert total_funds == 1
        assert total_commitments == fund_data['commitment_amount']
        
        # Cleanup
        db_session.rollback()
    
    def test_portfolio_summary_calculation_workflow(self, db_session: Session):
        """Test portfolio summary calculation workflow."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, FundFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company with multiple funds
        company = InvestmentCompanyFactory(
            name='Summary Test Company',
            company_type=CompanyType.ASSET_MANAGEMENT,
            status=CompanyStatus.ACTIVE
        )
        
        entity1 = EntityFactory()
        entity2 = EntityFactory()
        
        # Create funds with different statuses and amounts
        fund1 = FundFactory(
            investment_company=company,
            entity=entity1,
            status=FundStatus.ACTIVE,
            commitment_amount=1000000.0,
            current_equity_balance=950000.0
        )
        
        fund2 = FundFactory(
            investment_company=company,
            entity=entity2,
            status=FundStatus.ACTIVE,
            commitment_amount=2000000.0,
            current_equity_balance=2100000.0
        )
        
        fund3 = FundFactory(
            investment_company=company,
            entity=entity1,
            status=FundStatus.COMPLETED,
            commitment_amount=500000.0,
            current_equity_balance=600000.0
        )
        
        db_session.commit()
        
        # Act: Get portfolio summary
        portfolio_service = CompanyPortfolioService()
        summary = portfolio_service.get_portfolio_summary(company, db_session)
        
        # Assert: Verify portfolio summary calculations
        assert summary is not None
        assert summary['total_committed_capital'] == 3500000.0  # 1M + 2M + 500K
        assert summary['total_current_value'] == 3650000.0      # 950K + 2.1M + 600K
        assert summary['total_invested_capital'] == 3650000.0   # Same as current value
        assert summary['active_funds_count'] == 2
        assert summary['completed_funds_count'] == 1
        assert summary['suspended_funds_count'] == 0
        assert summary['realized_funds_count'] == 0
        
        # Verify fund status breakdown
        assert summary['fund_status_breakdown']['active_funds_count'] == 2
        assert summary['fund_status_breakdown']['completed_funds_count'] == 1
        
        # Cleanup
        db_session.rollback()
    
    def test_fund_coordination_workflow(self, db_session: Session):
        """Test fund coordination workflow between company and fund domains."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory(
            name='Coordination Test Company',
            company_type=CompanyType.VENTURE_CAPITAL,
            status=CompanyStatus.ACTIVE
        )
        
        entity = EntityFactory()
        
        fund_data = {
            'name': 'Coordination Test Fund',
            'fund_type': FundType.COST_BASED.value,
            'tracking_type': FundType.COST_BASED.value,
            'currency': 'USD',
            'description': 'Fund for coordination testing',
            'commitment_amount': 5000000.0,
            'expected_irr': 20.0,
            'expected_duration_months': 60
        }
        
        # Act: Use fund coordination service
        coordination_service = FundCoordinationService()
        
        # Validate business rules
        validation_result = coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Create fund through coordination
        fund = coordination_service.coordinate_fund_creation(
            company, entity, fund_data, db_session
        )
        
        # Assert: Verify coordination workflow
        assert validation_result['is_valid'] is True
        assert len(validation_result['errors']) == 0
        
        assert fund is not None
        assert fund.id is not None
        assert fund.investment_company_id == company.id
        assert fund.entity_id == entity.id
        assert fund.name == fund_data['name']
        assert fund.commitment_amount == fund_data['commitment_amount']
        
        # Verify company portfolio reflects the new fund
        db_session.refresh(company)
        assert len(company.funds) == 1
        assert company.funds[0].id == fund.id
        
        # Cleanup
        db_session.rollback()
    
    def test_portfolio_fund_management_workflow(self, db_session: Session):
        """Test portfolio fund management operations workflow."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, FundFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory(
            name='Management Test Company',
            company_type=CompanyType.REAL_ESTATE,
            status=CompanyStatus.ACTIVE
        )
        
        entity = EntityFactory()
        
        # Create initial fund
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            status=FundStatus.ACTIVE,
            commitment_amount=3000000.0,
            current_equity_balance=2800000.0
        )
        
        db_session.commit()
        
        # Act: Test portfolio operations
        portfolio_service = CompanyPortfolioService()
        
        # Update fund in portfolio
        update_data = {
            'commitment_amount': 3500000.0,
            'expected_irr': 18.0
        }
        
        updated_fund = portfolio_service.update_fund_in_portfolio(
            company, fund.id, update_data, db_session
        )
        
        # Get updated portfolio summary
        summary = portfolio_service.get_portfolio_summary(company, db_session)
        
        # Assert: Verify fund update workflow
        assert updated_fund is not None
        assert updated_fund.commitment_amount == 3500000.0
        assert updated_fund.expected_irr == 18.0
        
        # Verify portfolio summary reflects changes
        assert summary['total_committed_capital'] == 3500000.0
        
        # Cleanup
        db_session.rollback()
    
    def test_portfolio_event_integration_workflow(self, db_session: Session):
        """Test portfolio event integration workflow."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, FundFactory, EntityFactory, FundEventFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory(
            name='Event Test Company',
            company_type=CompanyType.INFRASTRUCTURE,
            status=CompanyStatus.ACTIVE
        )
        
        entity = EntityFactory()
        
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            status=FundStatus.ACTIVE,
            commitment_amount=15000000.0
        )
        
        # Create fund events to test last activity tracking
        event1 = FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            event_date=date.today(),
            amount=1000000.0
        )
        
        event2 = FundEventFactory(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            event_date=date.today(),
            amount=500000.0
        )
        
        db_session.commit()
        
        # Act: Get last activity information
        portfolio_service = CompanyPortfolioService()
        last_activity = portfolio_service.get_last_activity_info(company, db_session)
        
        # Assert: Verify event integration
        assert last_activity is not None
        assert last_activity['last_activity_date'] is not None
        assert last_activity['days_since_last_activity'] == 0  # Today
        
        # Verify activity date format
        activity_date = datetime.fromisoformat(last_activity['last_activity_date']).date()
        assert activity_date == date.today()
        
        # Cleanup
        db_session.rollback()
    
    def test_portfolio_calculation_service_integration(self, db_session: Session):
        """Test portfolio calculation service integration workflow."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, FundFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory(
            name='Calculation Test Company',
            company_type=CompanyType.CREDIT,
            status=CompanyStatus.ACTIVE
        )
        
        entity1 = EntityFactory()
        entity2 = EntityFactory()
        
        # Create funds with different characteristics
        fund1 = FundFactory(
            investment_company=company,
            entity=entity1,
            status=FundStatus.ACTIVE,
            commitment_amount=8000000.0,
            current_equity_balance=7500000.0
        )
        
        fund2 = FundFactory(
            investment_company=company,
            entity=entity2,
            status=FundStatus.ACTIVE,
            commitment_amount=12000000.0,
            current_equity_balance=13500000.0
        )
        
        fund3 = FundFactory(
            investment_company=company,
            entity=entity1,
            status=FundStatus.SUSPENDED,
            commitment_amount=3000000.0,
            current_equity_balance=2800000.0
        )
        
        db_session.commit()
        
        # Act: Test calculation service integration
        calculation_service = CompanyCalculationService()
        
        total_funds = calculation_service.calculate_total_funds_under_management(company, db_session)
        total_commitments = calculation_service.calculate_total_commitments(company, db_session)
        
        # Assert: Verify calculation service integration
        assert total_funds == 3  # All funds regardless of status
        assert total_commitments == 23000000.0  # 8M + 12M + 3M
        
        # Test portfolio service integration with calculation service
        portfolio_service = CompanyPortfolioService()
        
        portfolio_funds = portfolio_service.get_total_funds_under_management(company, db_session)
        portfolio_commitments = portfolio_service.get_total_commitments(company, db_session)
        
        assert portfolio_funds == total_funds
        assert portfolio_commitments == total_commitments
        
        # Cleanup
        db_session.rollback()
    
    def test_portfolio_error_handling_workflow(self, db_session: Session):
        """Test portfolio workflow error handling."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, FundFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory(
            name='Error Test Company',
            company_type=CompanyType.HEDGE_FUND,
            status=CompanyStatus.ACTIVE
        )
        
        entity = EntityFactory()
        
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            status=FundStatus.ACTIVE,
            commitment_amount=5000000.0
        )
        
        db_session.commit()
        
        # Act & Assert: Test error handling scenarios
        
        portfolio_service = CompanyPortfolioService()
        
        # Test updating non-existent fund
        with pytest.raises(ValueError) as exc_info:
            portfolio_service.update_fund_in_portfolio(
                company, 99999, {'commitment_amount': 6000000.0}, db_session
            )
        
        assert 'not found in company' in str(exc_info.value)
        
        # Test removing non-existent fund
        with pytest.raises(ValueError) as exc_info:
            portfolio_service.remove_fund_from_portfolio(company, 99999, db_session)
        
        assert 'not found in company' in str(exc_info.value)
        
        # Test fund coordination with invalid data
        coordination_service = FundCoordinationService()
        
        invalid_fund_data = {
            'name': '',  # Invalid: empty name
            'fund_type': 'INVALID_TYPE',  # Invalid: non-existent type
            'tracking_type': 'INVALID_TRACKING'  # Invalid: non-existent tracking
        }
        
        with pytest.raises(ValueError) as exc_info:
            coordination_service.coordinate_fund_creation(
                company, entity, invalid_fund_data, db_session
            )
        
        # Cleanup
        db_session.rollback()
    
    def test_portfolio_performance_workflow(self, db_session: Session):
        """Test portfolio workflow performance characteristics."""
        import time
        
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, FundFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory(
            name='Performance Test Company',
            company_type=CompanyType.FAMILY_OFFICE,
            status=CompanyStatus.ACTIVE
        )
        
        entity = EntityFactory()
        
        # Create multiple funds for performance testing
        funds = []
        for i in range(10):
            fund = FundFactory(
                investment_company=company,
                entity=entity,
                status=FundStatus.ACTIVE,
                commitment_amount=1000000.0 + (i * 100000.0),
                current_equity_balance=950000.0 + (i * 95000.0)
            )
            funds.append(fund)
        
        db_session.commit()
        
        # Act: Measure portfolio operations performance
        portfolio_service = CompanyPortfolioService()
        
        # Measure portfolio summary calculation time
        start_time = time.time()
        summary = portfolio_service.get_portfolio_summary(company, db_session)
        summary_time = time.time() - start_time
        
        # Measure total funds calculation time
        start_time = time.time()
        total_funds = portfolio_service.get_total_funds_under_management(company, db_session)
        total_funds_time = time.time() - start_time
        
        # Measure total commitments calculation time
        start_time = time.time()
        total_commitments = portfolio_service.get_total_commitments(company, db_session)
        total_commitments_time = time.time() - start_time
        
        # Assert: Verify performance characteristics
        assert summary is not None
        assert total_funds == 10
        assert total_commitments > 0
        
        # Performance assertions: operations should be fast (< 50ms each)
        # These are reasonable expectations for database operations with 10 funds
        assert summary_time < 0.05, f"Portfolio summary took {summary_time:.3f}s, expected < 0.05s"
        assert total_funds_time < 0.05, f"Total funds calculation took {total_funds_time:.3f}s, expected < 0.05s"
        assert total_commitments_time < 0.05, f"Total commitments calculation took {total_commitments_time:.3f}s, expected < 0.05s"
        
        # Cleanup
        db_session.rollback()
    
    def test_portfolio_data_consistency_workflow(self, db_session: Session):
        """Test portfolio workflow data consistency."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, FundFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory(
            name='Consistency Test Company',
            company_type=CompanyType.INVESTMENT_BANK,
            status=CompanyStatus.ACTIVE
        )
        
        entity = EntityFactory()
        
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            status=FundStatus.ACTIVE,
            commitment_amount=7500000.0,
            current_equity_balance=7000000.0
        )
        
        db_session.commit()
        
        # Act: Test data consistency across operations
        portfolio_service = CompanyPortfolioService()
        
        # Get initial portfolio state
        initial_summary = portfolio_service.get_portfolio_summary(company, db_session)
        initial_total_funds = portfolio_service.get_total_funds_under_management(company, db_session)
        initial_total_commitments = portfolio_service.get_total_commitments(company, db_session)
        
        # Update fund
        update_data = {'commitment_amount': 8000000.0}
        updated_fund = portfolio_service.update_fund_in_portfolio(
            company, fund.id, update_data, db_session
        )
        
        # Get updated portfolio state
        updated_summary = portfolio_service.get_portfolio_summary(company, db_session)
        updated_total_funds = portfolio_service.get_total_funds_under_management(company, db_session)
        updated_total_commitments = portfolio_service.get_total_commitments(company, db_session)
        
        # Assert: Verify data consistency
        assert initial_total_funds == 1
        assert initial_total_commitments == 7500000.0
        assert initial_summary['total_committed_capital'] == 7500000.0
        
        assert updated_total_funds == 1
        assert updated_total_commitments == 8000000.0
        assert updated_summary['total_committed_capital'] == 8000000.0
        
        # Verify fund was actually updated
        assert updated_fund.commitment_amount == 8000000.0
        
        # Verify database consistency
        db_session.refresh(company)
        assert len(company.funds) == 1
        assert company.funds[0].commitment_amount == 8000000.0
        
        # Cleanup
        db_session.rollback()
    
    def test_portfolio_cross_domain_coordination_workflow(self, db_session: Session):
        """Test portfolio workflow with cross-domain coordination."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, FundFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        company = InvestmentCompanyFactory(
            name='Cross-Domain Test Company',
            company_type=CompanyType.ASSET_MANAGEMENT,
            status=CompanyStatus.ACTIVE
        )
        
        entity = EntityFactory()
        
        # Act: Test cross-domain fund creation
        portfolio_service = CompanyPortfolioService()
        
        fund = portfolio_service.create_fund(
            company=company,
            entity=entity,
            name='Cross-Domain Fund',
            fund_type=FundType.NAV_BASED.value,
            tracking_type=FundType.NAV_BASED.value,
            currency='EUR',
            description='Fund for cross-domain testing',
            commitment_amount=12000000.0,
            expected_irr=16.5,
            expected_duration_months=96,
            session=db_session
        )
        
        # Assert: Verify cross-domain coordination
        assert fund is not None
        assert fund.id is not None
        assert fund.investment_company_id == company.id
        assert fund.entity_id == entity.id
        
        # Verify company portfolio reflects cross-domain changes
        db_session.refresh(company)
        assert len(company.funds) == 1
        assert company.funds[0].id == fund.id
        
        # Verify entity portfolio reflects cross-domain changes
        db_session.refresh(entity)
        assert len(entity.funds) == 1
        assert entity.funds[0].id == fund.id
        
        # Verify portfolio calculations work across domains
        total_funds = portfolio_service.get_total_funds_under_management(company, db_session)
        total_commitments = portfolio_service.get_total_commitments(company, db_session)
        
        assert total_funds == 1
        assert total_commitments == 12000000.0
        
        # Cleanup
        db_session.rollback()
