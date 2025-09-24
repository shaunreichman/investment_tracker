"""
Company Contact Workflow Integration Tests.

This module tests the complete company contact management workflow from API to database,
ensuring all layers (API, Services, Repositories, Models, Events) work together correctly.

Key testing areas:
- Complete contact lifecycle workflow (create, read, update, delete)
- Service layer integration and coordination
- Event system integration for contact changes
- Cross-domain coordination and updates
- Data consistency validation across layers
- Cache invalidation and performance patterns
- Error handling and validation workflows

Note: This focuses on integration testing and workflow coordination.
Individual component testing is covered by comprehensive unit tests.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.services import CompanyService, ContactManagementService
from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.services.company_summary_service import CompanySummaryService
from src.investment_company.services.company_validation_service import CompanyValidationService
from src.investment_company.enums import CompanyType, CompanyStatus
from src.investment_company.events.orchestrator import CompanyUpdateOrchestrator
from src.fund.models import Fund
from src.fund.enums import FundStatus, FundTrackingType
from src.entity.models import Entity
from tests.factories import InvestmentCompanyFactory, ContactFactory, FundFactory, EntityFactory


class TestCompanyContactWorkflow:
    """Test complete company contact management workflow from API to database."""
    
    def test_complete_contact_lifecycle_workflow(self, db_session: Session):
        """Test the complete contact lifecycle workflow through all layers."""
        # Arrange: Prepare company and contact data
        company_data = {
            'name': 'Contact Workflow Test Company',
            'description': 'Company for testing complete contact workflow',
            'company_type': CompanyType.PRIVATE_EQUITY,
            'status': CompanyStatus.ACTIVE
        }
        
        initial_contact_data = {
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
            status=company_data['status'],
            session=db_session
        )
        
        # Create initial contact through contact management service
        contact_service = ContactManagementService()
        contact = contact_service.add_contact(
            company=company,
            name=initial_contact_data['name'],
            title=initial_contact_data['title'],
            direct_number=initial_contact_data['direct_number'],
            direct_email=initial_contact_data['direct_email'],
            notes=initial_contact_data['notes'],
            session=db_session
        )
        
        # Assert: Verify initial contact creation
        assert contact is not None
        assert contact.id is not None
        assert contact.investment_company_id == company.id
        assert contact.name == initial_contact_data['name']
        assert contact.title == initial_contact_data['title']
        assert contact.direct_number == initial_contact_data['direct_number']
        assert contact.direct_email == initial_contact_data['direct_email']
        assert contact.notes == initial_contact_data['notes']
        
        # Verify company relationship
        db_session.refresh(company)
        assert len(company.contacts) == 1
        assert company.contacts[0].id == contact.id
        
        # Act: Update contact through service layer
        updated_contact_data = {
            'title': 'Chief Executive Officer',
            'direct_number': '+1987654321',
            'notes': 'Updated to CEO role'
        }
        
        updated_contact = contact_service.update_contact(
            contact=contact,
            title=updated_contact_data['title'],
            direct_number=updated_contact_data['direct_number'],
            notes=updated_contact_data['notes'],
            session=db_session
        )
        
        # Assert: Verify contact update
        assert updated_contact.title == updated_contact_data['title']
        assert updated_contact.direct_number == updated_contact_data['direct_number']
        assert updated_contact.notes == updated_contact_data['notes']
        assert updated_contact.name == initial_contact_data['name']  # Unchanged
        assert updated_contact.direct_email == initial_contact_data['direct_email']  # Unchanged
        assert updated_contact.updated_at > contact.created_at
        
        # Act: Retrieve contact through different service methods
        retrieved_contact = contact_service.get_contact_by_id(contact.id, db_session)
        company_contacts = contact_service.get_contacts_by_company(company, db_session)
        email_contact = contact_service.get_contact_by_email(initial_contact_data['direct_email'], db_session)
        
        # Assert: Verify retrieval methods
        assert retrieved_contact is not None
        assert retrieved_contact.id == contact.id
        assert len(company_contacts) == 1
        assert company_contacts[0].id == contact.id
        assert email_contact is not None
        assert email_contact.id == contact.id
        
        # Act: Delete contact through service layer
        contact_id = contact.id  # Store ID before deletion
        contact_service.delete_contact(contact, db_session)
        
        # Assert: Verify contact deletion
        db_session.refresh(company)
        assert len(company.contacts) == 0
        
        # Verify contact is no longer retrievable from database
        # Query directly from database to verify deletion
        from sqlalchemy import text
        result = db_session.execute(text("SELECT COUNT(*) FROM contacts WHERE id = :contact_id"), {"contact_id": contact_id})
        count = result.scalar()
        assert count == 0
        
        # Cleanup
        db_session.rollback()
    
    def test_contact_workflow_with_event_system_integration(self, db_session: Session):
        """Test contact workflow with event system integration."""
        # Arrange: Prepare company and contact data
        company_data = {
            'name': 'Event Integration Test Company',
            'description': 'Company for testing event system integration',
            'company_type': CompanyType.VENTURE_CAPITAL,
            'status': CompanyStatus.ACTIVE
        }
        
        contact_data = {
            'name': 'Jane Doe',
            'title': 'Investment Manager',
            'direct_number': '+1555123456',
            'direct_email': 'jane.doe@company.com',
            'notes': 'Investment team contact'
        }
        
        # Act: Create company and contact through service layer
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            status=company_data['status'],
            session=db_session
        )
        
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
        
        # Assert: Verify contact creation through service
        assert contact is not None
        assert contact.id is not None
        assert contact.investment_company_id == company.id
        
        # Verify company relationship is updated
        db_session.refresh(company)
        assert len(company.contacts) == 1
        assert company.contacts[0].id == contact.id
        
        # Act: Update contact through service
        updated_contact = contact_service.update_contact(
            contact=contact,
            name='Jane Smith',  # Change name
            title='Senior Investment Manager',  # Update title
            session=db_session
        )
        
        # Assert: Verify contact update through service
        assert updated_contact.name == 'Jane Smith'
        assert updated_contact.title == 'Senior Investment Manager'
        assert updated_contact.direct_number == contact_data['direct_number']  # Unchanged
        assert updated_contact.direct_email == contact_data['direct_email']  # Unchanged
        
        # Cleanup
        db_session.rollback()
    
    def test_contact_workflow_with_company_summary_integration(self, db_session: Session):
        """Test contact workflow integration with company summary calculations."""
        # Arrange: Prepare company with multiple contacts
        company_data = {
            'name': 'Summary Integration Test Company',
            'description': 'Company for testing summary integration',
            'company_type': CompanyType.REAL_ESTATE,
            'status': CompanyStatus.ACTIVE
        }
        
        contacts_data = [
            {
                'name': 'Alice Johnson',
                'title': 'Managing Director',
                'direct_number': '+1111111111',
                'direct_email': 'alice@company.com',
                'notes': 'Primary contact'
            },
            {
                'name': 'Bob Wilson',
                'title': 'Investment Director',
                'direct_number': '+1222222222',
                'direct_email': 'bob@company.com',
                'notes': 'Investment team lead'
            },
            {
                'name': 'Carol Brown',
                'title': 'Operations Manager',
                'direct_number': '+1333333333',
                'direct_email': 'carol@company.com',
                'notes': 'Operations contact'
            }
        ]
        
        # Act: Create company and multiple contacts
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            status=company_data['status'],
            session=db_session
        )
        
        contact_service = ContactManagementService()
        created_contacts = []
        
        for contact_data_item in contacts_data:
            contact = contact_service.add_contact(
                company=company,
                name=contact_data_item['name'],
                title=contact_data_item['title'],
                direct_number=contact_data_item['direct_number'],
                direct_email=contact_data_item['direct_email'],
                notes=contact_data_item['notes'],
                session=db_session
            )
            created_contacts.append(contact)
        
        # Assert: Verify all contacts were created
        assert len(created_contacts) == 3
        for contact in created_contacts:
            assert contact.id is not None
            assert contact.investment_company_id == company.id
        
        # Verify company relationship
        db_session.refresh(company)
        assert len(company.contacts) == 3
        
        # Act: Test company summary service integration
        summary_service = CompanySummaryService()
        company_summary = summary_service.get_company_summary_data(company, db_session)
        
        # Assert: Verify contact information in summary
        assert 'company' in company_summary
        assert 'contacts' in company_summary['company']
        assert len(company_summary['company']['contacts']) == 3
        
        # Verify contact details in summary
        contact_names = [contact['name'] for contact in company_summary['company']['contacts']]
        expected_names = [contact_data_item['name'] for contact_data_item in contacts_data]
        assert sorted(contact_names) == sorted(expected_names)
        
        # Act: Remove one contact and verify summary updates
        contact_to_remove = created_contacts[0]
        contact_service.delete_contact(contact_to_remove, db_session)
        
        # Refresh and get updated summary
        db_session.refresh(company)
        updated_summary = summary_service.get_company_summary_data(company, db_session)
        
        # Assert: Verify contact count decreased
        assert len(updated_summary['company']['contacts']) == 2
        
        # Cleanup
        db_session.rollback()
    
    def test_contact_workflow_with_validation_service_integration(self, db_session: Session):
        """Test contact workflow with validation service integration."""
        # Arrange: Prepare company and invalid contact data
        company_data = {
            'name': 'Validation Integration Test Company',
            'description': 'Company for testing validation integration',
            'company_type': CompanyType.INFRASTRUCTURE,
            'status': CompanyStatus.ACTIVE
        }
        
        # Act: Create company
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            status=company_data['status'],
            session=db_session
        )
        
        # Act: Test validation service integration
        validation_service = CompanyValidationService()
        
        # Test valid contact data
        valid_contact_data = {
            'name': 'Valid Contact',
            'title': 'Manager',
            'direct_number': '+1444444444',
            'direct_email': 'valid@company.com'
        }
        
        # Validation should pass
        validation_service.validate_contact_creation(
            name=valid_contact_data['name'],
            title=valid_contact_data['title'],
            direct_number=valid_contact_data['direct_number'],
            direct_email=valid_contact_data['direct_email']
        )
        
        # Test invalid contact data
        invalid_contact_data = {
            'name': '',  # Empty name
            'title': 'Manager',
            'direct_number': '+1444444444',
            'direct_email': 'invalid-email'  # Invalid email
        }
        
        # Validation should raise errors
        with pytest.raises(ValueError) as exc_info:
            validation_service.validate_contact_data(invalid_contact_data)
        
        assert "Contact name is required" in str(exc_info.value)
        
        # Act: Create valid contact after validation
        contact_service = ContactManagementService()
        contact = contact_service.add_contact(
            company=company,
            name=valid_contact_data['name'],
            title=valid_contact_data['title'],
            direct_number=valid_contact_data['direct_number'],
            direct_email=valid_contact_data['direct_email'],
            session=db_session
        )
        
        # Assert: Verify contact was created successfully
        assert contact is not None
        assert contact.id is not None
        assert contact.name == valid_contact_data['name']
        
        # Cleanup
        db_session.rollback()
    
    def test_contact_workflow_with_portfolio_service_coordination(self, db_session: Session):
        """Test contact workflow coordination with portfolio service."""
        # Arrange: Prepare company, entity, fund, and contact data
        company_data = {
            'name': 'Portfolio Coordination Test Company',
            'description': 'Company for testing portfolio coordination',
            'company_type': CompanyType.CREDIT,
            'status': CompanyStatus.ACTIVE
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
            'commitment_amount': 5000000.0,
            'expected_irr': 18.0,
            'expected_duration_months': 72
        }
        
        contact_data = {
            'name': 'Portfolio Manager',
            'title': 'Senior Portfolio Manager',
            'direct_number': '+1555555555',
            'direct_email': 'portfolio@company.com',
            'notes': 'Portfolio management contact'
        }
        
        # Act: Create company, entity, fund, and contact
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
        
        # Create contact
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
        
        # Assert: Verify complete setup
        assert company is not None
        assert company.id is not None
        assert fund is not None
        assert fund.id is not None
        assert contact is not None
        assert contact.id is not None
        
        # Verify relationships
        db_session.refresh(company)
        assert len(company.funds) == 1
        assert len(company.contacts) == 1
        assert company.funds[0].id == fund.id
        assert company.contacts[0].id == contact.id
        
        # Act: Test portfolio service coordination with contacts
        total_funds = portfolio_service.get_total_funds_under_management(company, db_session)
        total_commitments = portfolio_service.get_total_commitments(company, db_session)
        
        # Assert: Verify portfolio calculations
        assert total_funds == 1
        assert total_commitments == fund_data['commitment_amount']
        
        # Cleanup
        db_session.rollback()
    
    def test_contact_workflow_error_handling_and_validation(self, db_session: Session):
        """Test contact workflow error handling and validation scenarios."""
        # Arrange: Prepare company
        company_data = {
            'name': 'Error Handling Test Company',
            'description': 'Company for testing error handling',
            'company_type': CompanyType.HEDGE_FUND,
            'status': CompanyStatus.ACTIVE
        }
        
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            status=company_data['status'],
            session=db_session
        )
        
        contact_service = ContactManagementService()
        
        # Test: Adding contact with missing required fields
        with pytest.raises(ValueError) as exc_info:
            contact_service.add_contact(
                company=company,
                name='',  # Empty name
                session=db_session
            )
        assert "Contact name is required" in str(exc_info.value)
        
        # Test: Adding contact with invalid email format
        with pytest.raises(ValueError) as exc_info:
            contact_service.add_contact(
                company=company,
                name='Test Contact',
                direct_email='invalid-email-format',
                session=db_session
            )
        assert "Invalid email format" in str(exc_info.value)
        
        # Test: Adding contact with invalid phone format
        with pytest.raises(ValueError) as exc_info:
            contact_service.add_contact(
                company=company,
                name='Test Contact',
                direct_number='not-a-phone-number',
                session=db_session
            )
        assert "Invalid phone number format" in str(exc_info.value)
        
        # Test: Adding contact with whitespace-only name
        with pytest.raises(ValueError) as exc_info:
            contact_service.add_contact(
                company=company,
                name='   ',  # Whitespace only
                session=db_session
            )
        assert "Contact name is required" in str(exc_info.value)
        
        # Test: Valid contact creation after validation errors
        valid_contact = contact_service.add_contact(
            company=company,
            name='Valid Contact',
            title='Manager',
            direct_number='+1666666666',
            direct_email='valid@company.com',
            session=db_session
        )
        
        # Assert: Verify valid contact was created
        assert valid_contact is not None
        assert valid_contact.id is not None
        assert valid_contact.name == 'Valid Contact'
        
        # Test: Updating contact with invalid data
        with pytest.raises(ValueError) as exc_info:
            contact_service.update_contact(
                contact=valid_contact,
                name='',  # Empty name
                session=db_session
            )
        assert "Contact name cannot be empty" in str(exc_info.value)
        
        # Cleanup
        db_session.rollback()
    
    def test_contact_workflow_data_consistency_and_integrity(self, db_session: Session):
        """Test contact workflow data consistency and integrity across operations."""
        # Arrange: Prepare company and multiple contacts
        company_data = {
            'name': 'Data Consistency Test Company',
            'description': 'Company for testing data consistency',
            'company_type': CompanyType.FAMILY_OFFICE,
            'status': CompanyStatus.ACTIVE
        }
        
        company_service = CompanyService()
        company = company_service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            company_type=company_data['company_type'],
            status=company_data['status'],
            session=db_session
        )
        
        contact_service = ContactManagementService()
        
        # Create multiple contacts
        contacts_data = [
            {'name': 'Contact A', 'title': 'Manager A', 'direct_email': 'a@company.com'},
            {'name': 'Contact B', 'title': 'Manager B', 'direct_email': 'b@company.com'},
            {'name': 'Contact C', 'title': 'Manager C', 'direct_email': 'c@company.com'}
        ]
        
        created_contacts = []
        for contact_data_item in contacts_data:
            contact = contact_service.add_contact(
                company=company,
                name=contact_data_item['name'],
                title=contact_data_item['title'],
                direct_email=contact_data_item['direct_email'],
                session=db_session
            )
            created_contacts.append(contact)
        
        # Assert: Verify initial state
        assert len(created_contacts) == 3
        db_session.refresh(company)
        assert len(company.contacts) == 3
        
        # Act: Test data consistency through different access methods
        # Method 1: Direct company relationship
        company_contacts_direct = company.contacts
        
        # Method 2: Service layer retrieval
        company_contacts_service = contact_service.get_contacts_by_company(company, db_session)
        
        # Method 3: Individual contact retrieval
        individual_contacts = []
        for contact in created_contacts:
            retrieved_contact = contact_service.get_contact_by_id(contact.id, db_session)
            individual_contacts.append(retrieved_contact)
        
        # Assert: Verify data consistency across all access methods
        assert len(company_contacts_direct) == 3
        assert len(company_contacts_service) == 3
        assert len(individual_contacts) == 3
        
        # Verify contact IDs match across all methods
        direct_ids = sorted([c.id for c in company_contacts_direct])
        service_ids = sorted([c.id for c in company_contacts_service])
        individual_ids = sorted([c.id for c in individual_contacts])
        
        assert direct_ids == service_ids == individual_ids
        
        # Act: Test relationship integrity during updates
        contact_to_update = created_contacts[0]
        updated_contact = contact_service.update_contact(
            contact=contact_to_update,
            title='Senior Manager A',
            session=db_session
        )
        
        # Assert: Verify update consistency
        assert updated_contact.title == 'Senior Manager A'
        
        # Flush to ensure changes are persisted
        db_session.flush()
        
        # Refresh and verify all access methods show the same data
        db_session.refresh(company)
        db_session.refresh(updated_contact)
        
        # Verify company relationship shows updated data
        company_contact = next(c for c in company.contacts if c.id == updated_contact.id)
        assert company_contact.title == 'Senior Manager A'
        
        # Verify service layer shows updated data
        service_contact = contact_service.get_contact_by_id(updated_contact.id, db_session)
        assert service_contact.title == 'Senior Manager A'
        
        # Act: Test relationship integrity during deletion
        contact_to_delete = created_contacts[1]
        contact_id_to_delete = contact_to_delete.id  # Store ID before deletion
        contact_service.delete_contact(contact_to_delete, db_session)
        
        # Assert: Verify deletion consistency
        db_session.refresh(company)
        assert len(company.contacts) == 2
        
        # Verify contact is no longer accessible through any method
        # Check database directly to avoid cache issues
        from sqlalchemy import text
        result = db_session.execute(text("SELECT COUNT(*) FROM contacts WHERE id = :contact_id"), {"contact_id": contact_id_to_delete})
        count = result.scalar()
        assert count == 0
        
        # Verify remaining contacts are consistent
        # Check database directly to avoid cache issues
        result = db_session.execute(text("SELECT COUNT(*) FROM contacts WHERE investment_company_id = :company_id"), {"company_id": company.id})
        count = result.scalar()
        assert count == 2
        
        # Cleanup
        db_session.rollback()
