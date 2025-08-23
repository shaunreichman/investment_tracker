"""
Cross-Domain Integration Tests.

This module tests the integration between investment company, fund, and entity domains,
ensuring proper coordination and data consistency across the system.
"""

import pytest
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.services.company_summary_service import CompanySummaryService
from src.investment_company.events.orchestrator import CompanyUpdateOrchestrator
from src.fund.models import Fund
from src.fund.enums import FundStatus, FundType
from src.entity.models import Entity


class TestCrossDomainIntegration:
    """Test cross-domain integration between company, fund, and entity domains."""
    
    def test_fund_creation_coordination(self, db_session: Session):
        """Test that fund creation properly coordinates between company and fund domains."""
        # Create test company and entity
        company = InvestmentCompany(
            name="Test Investment Co",
            description="Test company for integration testing",
            company_type="Private Equity"
        )
        db_session.add(company)
        
        entity = Entity(
            name="Test Entity",
            description="Test entity for integration testing",
            tax_jurisdiction="AU"
        )
        db_session.add(entity)
        
        db_session.flush()
        
        # Test fund creation through company portfolio service
        portfolio_service = CompanyPortfolioService()
        fund = portfolio_service.create_fund(
            company=company,
            entity=entity,
            name="Test Fund",
            fund_type="Private Equity",
            tracking_type=FundType.NAV_BASED,
            currency="AUD",
            description="Test fund for integration testing",
            commitment_amount=1000000.0,
            expected_irr=15.0,
            expected_duration_months=60,
            session=db_session
        )
        
        # Verify fund was created and properly linked
        assert fund is not None
        assert fund.name == "Test Fund"
        assert fund.investment_company_id == company.id
        assert fund.entity_id == entity.id
        assert fund.status == FundStatus.ACTIVE
        
        # Verify company portfolio was updated
        company_funds = [f for f in company.funds]
        assert len(company_funds) == 1
        assert company_funds[0].id == fund.id
        
        # Verify entity relationship was maintained
        entity_funds = [f for f in entity.funds]
        assert len(entity_funds) == 1
        assert entity_funds[0].id == fund.id
        
        db_session.rollback()
    
    def test_portfolio_update_coordination(self, db_session: Session):
        """Test that portfolio updates properly coordinate across domains."""
        # Create test data
        company = InvestmentCompany(
            name="Test Company",
            description="Test company for portfolio coordination",
            company_type="Venture Capital"
        )
        db_session.add(company)
        
        entity = Entity(
            name="Test Entity",
            description="Test entity for portfolio coordination",
            tax_jurisdiction="AU"
        )
        db_session.add(entity)
        
        db_session.flush()
        
        # Create a fund
        portfolio_service = CompanyPortfolioService()
        fund = portfolio_service.create_fund(
            company=company,
            entity=entity,
            name="Test Portfolio Fund",
            fund_type="Venture Capital",
            tracking_type=FundType.COST_BASED,
            currency="AUD",
            description="Test fund for portfolio coordination",
            commitment_amount=500000.0,
            expected_irr=20.0,
            expected_duration_months=48,
            session=db_session
        )
        
        # Test portfolio summary update
        portfolio_summary = portfolio_service.get_portfolio_summary(company, db_session)
        
        # Verify portfolio summary is correct
        assert portfolio_summary['total_committed_capital'] == 500000.0
        assert portfolio_summary['active_funds_count'] == 1
        assert portfolio_summary['fund_status_breakdown']['active_funds_count'] == 1
        
        # Test fund update coordination
        updated_fund = portfolio_service.update_fund_in_portfolio(
            company=company,
            fund_id=fund.id,
            fund_data={'description': 'Updated description'},
            session=db_session
        )
        
        # Verify fund was updated
        assert updated_fund.description == 'Updated description'
        
        db_session.rollback()
    
    def test_event_driven_coordination(self, db_session: Session):
        """Test that events properly coordinate updates across domains."""
        # Create test company
        company = InvestmentCompany(
            name="Test Event Company",
            description="Test company for event coordination",
            company_type="Private Equity"
        )
        db_session.add(company)
        db_session.flush()
        
        # Test company creation through orchestrator
        orchestrator = CompanyUpdateOrchestrator()
        company_data = {
            'name': 'Test Event Company',
            'description': 'Test company for event coordination',
            'company_type': 'Private Equity'
        }
        
        # This should trigger the complete event pipeline
        created_company = orchestrator.create_company(company_data, db_session)
        
        # Verify company was created
        assert created_company is not None
        assert created_company.name == 'Test Event Company'
        
        # Verify event was processed (check logs or event registry)
        # The orchestrator should have triggered cross-domain coordination
        
        db_session.rollback()
    
    def test_entity_coordination(self, db_session: Session):
        """Test that entity changes properly coordinate with company domain."""
        # Create test entity
        entity = Entity(
            name="Test Entity for Coordination",
            description="Test entity for company coordination",
            tax_jurisdiction="AU"
        )
        db_session.add(entity)
        db_session.flush()
        
        # Create company that will work with this entity
        company = InvestmentCompany(
            name="Test Entity Company",
            description="Test company for entity coordination",
            company_type="Private Equity"
        )
        db_session.add(company)
        db_session.flush()
        
        # Create fund linking company and entity
        portfolio_service = CompanyPortfolioService()
        fund = portfolio_service.create_fund(
            company=company,
            entity=entity,
            name="Entity Coordination Fund",
            fund_type="Private Equity",
            tracking_type=FundType.NAV_BASED,
            currency="AUD",
            description="Test fund for entity coordination",
            commitment_amount=750000.0,
            expected_irr=18.0,
            expected_duration_months=72,
            session=db_session
        )
        
        # Verify relationships are properly established
        assert fund.investment_company_id == company.id
        assert fund.entity_id == entity.id
        
        # Verify entity has access to fund
        entity_funds = [f for f in entity.funds]
        assert len(entity_funds) == 1
        assert entity_funds[0].id == fund.id
        
        # Verify company has access to fund
        company_funds = [f for f in company.funds]
        assert len(company_funds) == 1
        assert company_funds[0].id == fund.id
        
        db_session.rollback()
    
    def test_error_handling_across_domains(self, db_session: Session):
        """Test that errors in one domain don't break coordination in others."""
        # Create test company
        company = InvestmentCompany(
            name="Test Error Company",
            description="Test company for error handling",
            company_type="Private Equity"
        )
        db_session.add(company)
        db_session.flush()
        
        # Test that invalid fund creation doesn't break company operations
        portfolio_service = CompanyPortfolioService()
        
        # Try to create fund with invalid entity (None)
        with pytest.raises(ValueError, match="Entity is required"):
            portfolio_service.create_fund(
                company=company,
                entity=None,  # Invalid entity
                name="Invalid Fund",
                fund_type="Private Equity",
                tracking_type=FundType.NAV_BASED,
                currency="AUD",
                session=db_session
            )
        
        # Verify company is still intact
        assert company.id is not None
        assert company.name == "Test Error Company"
        
        # Verify no funds were created
        assert len(company.funds) == 0
        
        db_session.rollback()
    
    def test_performance_across_domains(self, db_session: Session):
        """Test that cross-domain operations maintain good performance."""
        import time
        
        # Create test company
        company = InvestmentCompany(
            name="Test Performance Company",
            description="Test company for performance testing",
            company_type="Private Equity"
        )
        db_session.add(company)
        
        # Create multiple entities
        entities = []
        for i in range(5):
            entity = Entity(
                name=f"Test Entity {i}",
                description=f"Test entity {i} for performance testing",
                tax_jurisdiction="AU"
            )
            db_session.add(entity)
            entities.append(entity)
        
        db_session.flush()
        
        # Measure time for creating multiple funds
        portfolio_service = CompanyPortfolioService()
        start_time = time.time()
        
        funds = []
        for i, entity in enumerate(entities):
            fund = portfolio_service.create_fund(
                company=company,
                entity=entity,
                name=f"Performance Fund {i}",
                fund_type="Private Equity",
                tracking_type=FundType.NAV_BASED,
                currency="AUD",
                description=f"Performance test fund {i}",
                commitment_amount=100000.0 * (i + 1),
                expected_irr=15.0 + i,
                expected_duration_months=60,
                session=db_session
            )
            funds.append(fund)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Verify all funds were created
        assert len(funds) == 5
        assert len(company.funds) == 5
        
        # Performance assertion: 5 fund creations should complete in reasonable time
        # This is a basic performance gate - adjust based on your system's capabilities
        assert creation_time < 5.0  # Should complete in under 5 seconds
        
        # Test portfolio summary performance
        start_time = time.time()
        portfolio_summary = portfolio_service.get_portfolio_summary(company, db_session)
        end_time = time.time()
        summary_time = end_time - start_time
        
        # Portfolio summary should be fast
        assert summary_time < 1.0  # Should complete in under 1 second
        
        # Verify summary data
        assert portfolio_summary['total_committed_capital'] == 1500000.0  # Sum of 100k, 200k, 300k, 400k, 500k
        assert portfolio_summary['active_funds_count'] == 5
        
        db_session.rollback()


# Test data setup helpers
@pytest.fixture
def sample_company(db_session: Session) -> InvestmentCompany:
    """Create a sample company for testing."""
    company = InvestmentCompany(
        name="Sample Test Company",
        description="Sample company for integration testing",
        company_type="Private Equity"
    )
    db_session.add(company)
    db_session.flush()
    return company


@pytest.fixture
def sample_entity(db_session: Session) -> Entity:
    """Create a sample entity for testing."""
    entity = Entity(
        name="Sample Test Entity",
        description="Sample entity for integration testing",
        tax_jurisdiction="AU"
    )
    db_session.add(entity)
    db_session.flush()
    return entity


@pytest.fixture
def sample_fund(db_session: Session, sample_company: InvestmentCompany, sample_entity: Entity) -> Fund:
    """Create a sample fund for testing."""
    portfolio_service = CompanyPortfolioService()
    fund = portfolio_service.create_fund(
        company=sample_company,
        entity=sample_entity,
        name="Sample Test Fund",
        fund_type="Private Equity",
        tracking_type=FundType.NAV_BASED,
        currency="AUD",
        description="Sample fund for integration testing",
        commitment_amount=1000000.0,
        expected_irr=15.0,
        expected_duration_months=60,
        session=db_session
    )
    return fund

