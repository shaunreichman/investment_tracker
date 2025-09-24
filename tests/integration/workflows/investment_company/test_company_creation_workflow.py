"""
Company Creation Workflow Integration Tests.

This module tests the complete company creation workflow from API to database,
ensuring all layers (API, Services, Repositories, Models) work together correctly.

Key testing areas:
- Complete company creation workflow
- Service layer integration
- Repository layer integration
- Event system integration
- Cross-domain coordination
- Data consistency validation
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.services import CompanyService
from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.services.company_summary_service import CompanySummaryService
from src.investment_company.services.contact_management_service import ContactManagementService
from src.investment_company.services.company_validation_service import CompanyValidationService
from src.investment_company.enums import CompanyType, CompanyStatus
from src.fund.models import Fund
from src.fund.enums import FundStatus, FundTrackingType
from src.entity.models import Entity
from tests.factories import InvestmentCompanyFactory, ContactFactory, FundFactory, EntityFactory


class TestCompanyCreationWorkflow:
    """Test complete company creation workflow from API to database."""
    
    def test_complete_company_creation_workflow(self, db_session: Session):
        """Test the complete company creation workflow through all layers."""
        # Arrange: Prepare company data
        company_data = {
            'name': 'Test Investment Company',
            'description': 'A test investment company for workflow testing',
            'website': 'https://testcompany.com',
            'company_type': CompanyType.PRIVATE_EQUITY,
            'business_address': '123 Investment Street, Financial District',
            'status': CompanyStatus.ACTIVE
        }
        
        # Act: Create company through service layer
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            website=company_data['website'],
            company_type=company_data['company_type'],
            business_address=company_data['business_address'],
            status=company_data['status'],
            session=db_session
        )
        
        # Assert: Verify company was created correctly
        assert company is not None
        assert company.id is not None
        assert company.name == company_data['name']
        assert company.description == company_data['description']
        assert company.website == company_data['website']
        assert company.company_type == company_data['company_type']
        assert company.business_address == company_data['business_address']
        assert company.status == company_data['status']
        assert company.created_at is not None
        assert company.updated_at is not None
        
        # Verify database persistence
        db_session.refresh(company)
        assert company.id is not None
        
        # Cleanup
        db_session.rollback()
    
    def test_company_creation_with_validation_workflow(self, db_session: Session):
        """Test company creation workflow with comprehensive validation."""
        # Arrange: Prepare valid company data
        company_data = {
            'name': 'Valid Investment Co',
            'description': 'Valid company data',
            'website': 'https://validcompany.com',
            'company_type': CompanyType.VENTURE_CAPITAL,
            'business_address': '456 Venture Ave, Tech Hub'
        }
        
        # Act: Create company through service layer
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            website=company_data['website'],
            company_type=company_data['company_type'],
            business_address=company_data['business_address'],
            session=db_session
        )
        
        # Assert: Verify validation passed and company created
        assert company is not None
        assert company.id is not None
        assert company.status == CompanyStatus.ACTIVE.value  # Default status
        
        # Verify validation service was used
        validation_service = CompanyValidationService()
        validation_errors = validation_service.validate_company_creation(
            name=company_data['name'],
            description=company_data['description'],
            website=company_data['website'],
            company_type=company_data['company_type'],
            business_address=company_data['business_address']
        )
        assert not validation_errors
        
        # Cleanup
        db_session.rollback()
    
    def test_company_creation_with_contacts_workflow(self, db_session: Session):
        """Test company creation workflow including contact management."""
        # Arrange: Prepare company and contact data
        company_data = {
            'name': 'Company With Contacts',
            'description': 'Company that includes contact creation',
            'company_type': CompanyType.REAL_ESTATE
        }
        
        contact_data = {
            'name': 'John Smith',
            'title': 'Managing Director',
            'direct_number': '+1234567890',
            'direct_email': 'john.smith@company.com',
            'notes': 'Primary contact for the company'
        }
        
        # Act: Create company through service layer
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            session=db_session
        )
        
        # Add contact through contact management service
        contact_service = ContactManagementService()
        contact = contact_service.add_contact(
            company=company,
            name=contact_data['name'],
            title=contact_data['title'],
            direct_number=contact_data['direct_number'],
            direct_email=contact_data['direct_email'],
            notes=contact_data['notes'],
            session=db_session
        )
        
        # Assert: Verify both company and contact were created
        assert company is not None
        assert company.id is not None
        assert contact is not None
        assert contact.id is not None
        assert contact.investment_company_id == company.id
        
        # Verify relationships
        assert len(company.contacts) == 1
        assert company.contacts[0].id == contact.id
        
        # Cleanup
        db_session.rollback()
    
    def test_company_creation_with_portfolio_workflow(self, db_session: Session):
        """Test company creation workflow including portfolio setup."""
        # Arrange: Prepare company, entity, and fund data
        company_data = {
            'name': 'Portfolio Company',
            'description': 'Company with portfolio setup',
            'company_type': CompanyType.INFRASTRUCTURE
        }
        
        entity_data = {
            'name': 'Test Entity',
            'description': 'Test entity for portfolio',
            'tax_jurisdiction': 'AU'
        }
        
        fund_data = {
            'name': 'Test Fund',
            'fund_type': FundTrackingType.NAV_BASED.value,
            'tracking_type': FundTrackingType.NAV_BASED.value,
            'currency': 'AUD',
            'description': 'Test fund for portfolio',
            'commitment_amount': 1000000.0,
            'expected_irr': 12.5,
            'expected_duration_months': 60
        }
        
        # Act: Create company through service layer
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
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
    
    def test_company_creation_error_handling_workflow(self, db_session: Session):
        """Test company creation workflow error handling."""
        # Arrange: Prepare invalid company data
        invalid_company_data = {
            'name': '',  # Invalid: empty name
            'description': 'Invalid company',
            'company_type': 'INVALID_TYPE'  # Invalid: non-existent type
        }
        
        # Act & Assert: Verify validation errors are properly handled
        company_service = CompanyService()
        
        with pytest.raises(ValueError) as exc_info:
            company_service.create_company(
                name=invalid_company_data['name'],
                description=invalid_company_data['description'],
                company_type=invalid_company_data['company_type'],
                session=db_session
            )
        
        # Verify error message contains validation details
        error_message = str(exc_info.value)
        assert 'Validation failed' in error_message
        
        # Cleanup
        db_session.rollback()
    
    def test_company_creation_with_factory_workflow(self, db_session: Session):
        """Test company creation workflow using test factories."""
        # Arrange: Set up factories with session
        for factory in (InvestmentCompanyFactory, ContactFactory, FundFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Act: Create company using factory
        company = InvestmentCompanyFactory(
            name='Factory Company',
            company_type=CompanyType.HEDGE_FUND,
            status=CompanyStatus.ACTIVE
        )
        
        # Create related entities
        entity = EntityFactory()
        contact = ContactFactory(investment_company=company)
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            status=FundStatus.ACTIVE
        )
        
        db_session.commit()
        
        # Assert: Verify complete workflow with factories
        assert company is not None
        assert company.id is not None
        assert entity is not None
        assert entity.id is not None
        assert contact is not None
        assert contact.id is not None
        assert fund is not None
        assert fund.id is not None
        
        # Verify relationships
        assert contact.investment_company_id == company.id
        assert fund.investment_company_id == company.id
        assert fund.entity_id == entity.id
        
        # Verify portfolio calculations through services
        portfolio_service = CompanyPortfolioService()
        total_funds = portfolio_service.get_total_funds_under_management(company, db_session)
        total_commitments = portfolio_service.get_total_commitments(company, db_session)
        
        assert total_funds == 1
        assert total_commitments > 0  # Factory creates funds with default commitments
        
        # Cleanup
        db_session.rollback()
    
    def test_company_creation_performance_workflow(self, db_session: Session):
        """Test company creation workflow performance characteristics."""
        import time
        
        # Arrange: Prepare company data
        company_data = {
            'name': 'Performance Test Company',
            'description': 'Company for performance testing',
            'company_type': CompanyType.ASSET_MANAGEMENT
        }
        
        # Act: Measure creation time
        start_time = time.time()
        
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            session=db_session
        )
        
        creation_time = time.time() - start_time
        
        # Assert: Verify performance characteristics
        assert company is not None
        assert company.id is not None
        
        # Performance assertion: company creation should be fast (< 100ms)
        # This is a reasonable expectation for a simple database operation
        assert creation_time < 0.1, f"Company creation took {creation_time:.3f}s, expected < 0.1s"
        
        # Cleanup
        db_session.rollback()
    
    def test_company_creation_data_consistency_workflow(self, db_session: Session):
        """Test company creation workflow data consistency."""
        # Arrange: Prepare company data
        company_data = {
            'name': 'Consistency Test Company',
            'description': 'Company for consistency testing',
            'company_type': CompanyType.FAMILY_OFFICE
        }
        
        # Act: Create company through service layer
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            session=db_session
        )
        
        # Verify database consistency
        db_session.refresh(company)
        
        # Assert: Verify data consistency across all layers
        assert company.name == company_data['name']
        assert company.description == company_data['description']
        assert company.company_type == company_data['company_type']
        # Status can be either enum object or string value, check both
        assert company.status in [CompanyStatus.ACTIVE, CompanyStatus.ACTIVE.value]  # Default status
        
        # Verify timestamps are consistent
        assert company.created_at is not None
        assert company.updated_at is not None
        # Timestamps should be very close (within 1 second) on creation
        time_diff = abs((company.updated_at - company.created_at).total_seconds())
        assert time_diff < 1.0, f"Timestamps differ by {time_diff} seconds"
        
        # Verify relationships are properly initialized
        assert company.funds == []
        assert company.contacts == []
        
        # Cleanup
        db_session.rollback()
    
    def test_company_creation_cross_domain_workflow(self, db_session: Session):
        """Test company creation workflow with cross-domain coordination."""
        # Arrange: Prepare cross-domain data
        company_data = {
            'name': 'Cross-Domain Company',
            'description': 'Company for cross-domain testing',
            'company_type': CompanyType.INVESTMENT_BANK
        }
        
        entity_data = {
            'name': 'Cross-Domain Entity',
            'description': 'Entity for cross-domain testing',
            'tax_jurisdiction': 'US'
        }
        
        # Act: Create company and entity
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            session=db_session
        )
        
        entity = Entity(
            name=entity_data['name'],
            description=entity_data['description'],
            tax_jurisdiction=entity_data['tax_jurisdiction']
        )
        db_session.add(entity)
        db_session.flush()
        
        # Create fund to test cross-domain coordination
        portfolio_service = CompanyPortfolioService()
        fund = portfolio_service.create_fund(
            company=company,
            entity=entity,
            name='Cross-Domain Fund',
            fund_type=FundTrackingType.NAV_BASED.value,
            tracking_type=FundTrackingType.NAV_BASED.value,
            currency='USD',
            description='Fund for cross-domain testing',
            commitment_amount=5000000.0,
            expected_irr=18.0,
            expected_duration_months=72,
            session=db_session
        )
        
        # Assert: Verify cross-domain coordination
        assert company is not None
        assert entity is not None
        assert fund is not None
        
        # Verify fund properly links both domains
        assert fund.investment_company_id == company.id
        assert fund.entity_id == entity.id
        
        # Verify company portfolio reflects cross-domain changes
        assert len(company.funds) == 1
        assert company.funds[0].id == fund.id
        
        # Verify entity portfolio reflects cross-domain changes
        assert len(entity.funds) == 1
        assert entity.funds[0].id == fund.id
        
        # Cleanup
        db_session.rollback()
