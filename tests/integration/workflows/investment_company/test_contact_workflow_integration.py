"""
Integration tests for contact workflow through all refactored layers.

This file tests the complete contact workflow from service layer through
all refactored layers: Services -> Repositories -> Models.

Tests cover:
- Contact creation workflow with investment company validation
- Contact retrieval with various sorting and filtering options
- Contact deletion workflow
- Integration with InvestmentCompany model
- Error handling across all layers
- Database relationship integrity
"""

import pytest
from datetime import datetime, timezone
from typing import List

from tests.factories import (
    InvestmentCompanyFactory, ContactFactory
)
from src.investment_company.models import Contact, InvestmentCompany
from src.investment_company.services.company_contact_service import CompanyContactService
from src.investment_company.enums.company_contact_enums import SortFieldContact
from src.shared.enums.shared_enums import SortOrder


class TestContactWorkflowIntegration:
    """Test complete contact workflow through all refactored layers"""

    def test_contact_creation_workflow_success(self, db_session):
        """Test successful contact creation through service layer flow"""
        # Setup factories with session
        for factory in (InvestmentCompanyFactory, ContactFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create investment company first
        company = InvestmentCompanyFactory.create()
        db_session.commit()
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Contact data for creation
        contact_data = {
            'name': 'John Smith',
            'title': 'Managing Director',
            'direct_number': '+1-555-123-4567',
            'direct_email': 'john.smith@example.com',
            'notes': 'Primary contact for fund management'
        }
        
        # Act: Create contact through service layer
        created_contact = contact_service.create_contact(
            company_id=company.id,
            contact_data=contact_data,
            session=db_session
        )
        db_session.commit()
        
        # Assert: Verify contact was created correctly
        assert created_contact is not None
        assert created_contact.id is not None
        assert created_contact.investment_company_id == company.id
        assert created_contact.name == contact_data['name']
        assert created_contact.title == contact_data['title']
        assert created_contact.direct_number == contact_data['direct_number']
        assert created_contact.direct_email == contact_data['direct_email']
        assert created_contact.notes == contact_data['notes']
        assert created_contact.created_at is not None
        assert created_contact.updated_at is not None
        
        # Verify relationship is established
        assert created_contact.investment_company.id == company.id
        assert created_contact.investment_company.name == company.name

    def test_contact_creation_workflow_invalid_company(self, db_session):
        """Test contact creation with non-existent company"""
        # Setup factories with session
        ContactFactory._meta.sqlalchemy_session = db_session
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Contact data for creation
        contact_data = {
            'name': 'John Smith',
            'title': 'Managing Director',
            'direct_email': 'john.smith@example.com'
        }
        
        # Act & Assert: Should raise ValueError for non-existent company
        with pytest.raises(ValueError, match="Company not found"):
            contact_service.create_contact(
                company_id=99999,  # Non-existent company ID
                contact_data=contact_data,
                session=db_session
            )

    def test_contact_retrieval_workflow_by_company(self, db_session):
        """Test retrieving contacts filtered by company"""
        # Setup factories with session
        for factory in (InvestmentCompanyFactory, ContactFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create two companies with different contacts
        company1 = InvestmentCompanyFactory.create(name="Company Alpha")
        company2 = InvestmentCompanyFactory.create(name="Company Beta")
        db_session.commit()
        
        # Create contacts for each company
        contact1_1 = ContactFactory.create(
            investment_company=company1,
            name="Alice Johnson",
            title="CFO"
        )
        contact1_2 = ContactFactory.create(
            investment_company=company1,
            name="Bob Wilson",
            title="Managing Director"
        )
        contact2_1 = ContactFactory.create(
            investment_company=company2,
            name="Carol Davis",
            title="Operations Manager"
        )
        db_session.commit()
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Act: Retrieve contacts for company1
        company1_contacts = contact_service.get_contacts(
            session=db_session,
            company_ids=[company1.id]
        )
        
        # Act: Retrieve contacts for company2
        company2_contacts = contact_service.get_contacts(
            session=db_session,
            company_ids=[company2.id]
        )
        
        # Act: Retrieve all contacts
        all_contacts = contact_service.get_contacts(session=db_session)
        
        # Assert: Verify filtering works correctly
        assert len(company1_contacts) == 2
        assert len(company2_contacts) == 1
        assert len(all_contacts) == 3
        
        # Verify correct contacts are returned
        company1_names = {contact.name for contact in company1_contacts}
        assert company1_names == {"Alice Johnson", "Bob Wilson"}
        
        company2_names = {contact.name for contact in company2_contacts}
        assert company2_names == {"Carol Davis"}

    def test_contact_retrieval_workflow_sorting(self, db_session):
        """Test contact retrieval with various sorting options"""
        # Setup factories with session
        for factory in (InvestmentCompanyFactory, ContactFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company
        company = InvestmentCompanyFactory.create()
        db_session.commit()
        
        # Create contacts with specific names for sorting test
        contact1 = ContactFactory.create(
            investment_company=company,
            name="Zoe Anderson",
            title="Director"
        )
        contact2 = ContactFactory.create(
            investment_company=company,
            name="Alice Brown",
            title="Manager"
        )
        contact3 = ContactFactory.create(
            investment_company=company,
            name="Charlie Davis",
            title="Analyst"
        )
        db_session.commit()
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Test sorting by name ascending
        contacts_asc = contact_service.get_contacts(
            session=db_session,
            company_ids=[company.id],
            sort_by=SortFieldContact.NAME,
            sort_order=SortOrder.ASC
        )
        
        # Test sorting by name descending
        contacts_desc = contact_service.get_contacts(
            session=db_session,
            company_ids=[company.id],
            sort_by=SortFieldContact.NAME,
            sort_order=SortOrder.DESC
        )
        
        # Assert: Verify sorting works correctly
        assert len(contacts_asc) == 3
        assert len(contacts_desc) == 3
        
        # Check ascending order
        assert contacts_asc[0].name == "Alice Brown"
        assert contacts_asc[1].name == "Charlie Davis"
        assert contacts_asc[2].name == "Zoe Anderson"
        
        # Check descending order
        assert contacts_desc[0].name == "Zoe Anderson"
        assert contacts_desc[1].name == "Charlie Davis"
        assert contacts_desc[2].name == "Alice Brown"

    def test_contact_retrieval_workflow_by_id(self, db_session):
        """Test retrieving a specific contact by ID"""
        # Setup factories with session
        for factory in (InvestmentCompanyFactory, ContactFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and contact
        company = InvestmentCompanyFactory.create()
        contact = ContactFactory.create(
            investment_company=company,
            name="Test Contact",
            title="Test Title",
            direct_email="test@example.com"
        )
        db_session.commit()
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Act: Retrieve contact by ID
        retrieved_contact = contact_service.get_contact_by_id(
            contact_id=contact.id,
            session=db_session
        )
        
        # Assert: Verify correct contact is retrieved
        assert retrieved_contact is not None
        assert retrieved_contact.id == contact.id
        assert retrieved_contact.name == "Test Contact"
        assert retrieved_contact.title == "Test Title"
        assert retrieved_contact.direct_email == "test@example.com"
        assert retrieved_contact.investment_company_id == company.id

    def test_contact_retrieval_workflow_nonexistent_id(self, db_session):
        """Test retrieving contact with non-existent ID"""
        # Initialize service
        contact_service = CompanyContactService()
        
        # Act: Try to retrieve non-existent contact
        retrieved_contact = contact_service.get_contact_by_id(
            contact_id=99999,
            session=db_session
        )
        
        # Assert: Should return None
        assert retrieved_contact is None

    def test_contact_deletion_workflow_success(self, db_session):
        """Test successful contact deletion through service layer"""
        # Setup factories with session
        for factory in (InvestmentCompanyFactory, ContactFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and contact
        company = InvestmentCompanyFactory.create()
        contact = ContactFactory.create(
            investment_company=company,
            name="Contact to Delete",
            title="Test Title"
        )
        db_session.commit()
        
        # Verify contact exists
        assert contact.id is not None
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Act: Delete contact through service layer
        deletion_result = contact_service.delete_contact(
            contact_id=contact.id,
            session=db_session
        )
        db_session.commit()
        
        # Assert: Verify deletion was successful
        assert deletion_result is True
        
        # Verify contact no longer exists
        deleted_contact = contact_service.get_contact_by_id(
            contact_id=contact.id,
            session=db_session
        )
        assert deleted_contact is None

    def test_contact_deletion_workflow_nonexistent_contact(self, db_session):
        """Test contact deletion with non-existent contact ID"""
        # Initialize service
        contact_service = CompanyContactService()
        
        # Act & Assert: Should raise ValueError for non-existent contact
        with pytest.raises(ValueError, match="Contact not found"):
            contact_service.delete_contact(
                contact_id=99999,  # Non-existent contact ID
                session=db_session
            )

    def test_contact_workflow_with_minimal_data(self, db_session):
        """Test contact creation and retrieval with minimal required data"""
        # Setup factories with session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        
        # Create company
        company = InvestmentCompanyFactory.create()
        db_session.commit()
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Contact data with only required fields
        minimal_contact_data = {
            'name': 'Minimal Contact'
            # No title, phone, email, or notes
        }
        
        # Act: Create contact with minimal data
        created_contact = contact_service.create_contact(
            company_id=company.id,
            contact_data=minimal_contact_data,
            session=db_session
        )
        db_session.commit()
        
        # Assert: Verify contact was created with minimal data
        assert created_contact is not None
        assert created_contact.name == 'Minimal Contact'
        assert created_contact.title is None
        assert created_contact.direct_number is None
        assert created_contact.direct_email is None
        assert created_contact.notes is None
        assert created_contact.investment_company_id == company.id

    def test_contact_workflow_timestamp_management(self, db_session):
        """Test that created_at and updated_at timestamps are managed correctly"""
        # Setup factories with session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        
        # Create company
        company = InvestmentCompanyFactory.create()
        db_session.commit()
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Record time before creation
        before_creation = datetime.now(timezone.utc)
        
        # Contact data
        contact_data = {
            'name': 'Timestamp Test Contact',
            'title': 'Test Title'
        }
        
        # Act: Create contact
        created_contact = contact_service.create_contact(
            company_id=company.id,
            contact_data=contact_data,
            session=db_session
        )
        db_session.commit()
        
        # Record time after creation
        after_creation = datetime.now(timezone.utc)
        
        # Assert: Verify timestamps are set correctly
        assert created_contact.created_at is not None
        assert created_contact.updated_at is not None
        
        # Convert timestamps to UTC for comparison (in case they're stored as naive)
        created_at_utc = created_contact.created_at
        if created_at_utc.tzinfo is None:
            created_at_utc = created_at_utc.replace(tzinfo=timezone.utc)
            
        updated_at_utc = created_contact.updated_at
        if updated_at_utc.tzinfo is None:
            updated_at_utc = updated_at_utc.replace(tzinfo=timezone.utc)
            
        assert before_creation <= created_at_utc <= after_creation
        assert before_creation <= updated_at_utc <= after_creation
        
        # Initially, created_at and updated_at should be very close (within 1 second)
        time_diff = abs((created_at_utc - updated_at_utc).total_seconds())
        assert time_diff < 1.0, f"Created and updated timestamps should be within 1 second, but were {time_diff} seconds apart"

    def test_contact_workflow_database_relationship_integrity(self, db_session):
        """Test database relationship integrity between Contact and InvestmentCompany"""
        # Setup factories with session
        for factory in (InvestmentCompanyFactory, ContactFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company
        company = InvestmentCompanyFactory.create(name="Relationship Test Company")
        db_session.commit()
        
        # Create multiple contacts for the company
        contact1 = ContactFactory.create(
            investment_company=company,
            name="Contact One"
        )
        contact2 = ContactFactory.create(
            investment_company=company,
            name="Contact Two"
        )
        db_session.commit()
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Act: Retrieve contacts and verify relationships
        all_contacts = contact_service.get_contacts(
            session=db_session,
            company_ids=[company.id]
        )
        
        # Assert: Verify all relationships are intact
        assert len(all_contacts) == 2
        
        for contact in all_contacts:
            # Verify foreign key relationship
            assert contact.investment_company_id == company.id
            
            # Verify SQLAlchemy relationship
            assert contact.investment_company is not None
            assert contact.investment_company.id == company.id
            assert contact.investment_company.name == "Relationship Test Company"
            
            # Verify contact is in company's contacts (if back_populates is working)
            # Note: This depends on the InvestmentCompany model having a contacts relationship

    def test_contact_workflow_sorting_by_created_at(self, db_session):
        """Test contact retrieval sorted by created_at timestamp"""
        # Setup factories with session
        for factory in (InvestmentCompanyFactory, ContactFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company
        company = InvestmentCompanyFactory.create()
        db_session.commit()
        
        # Create contacts with slight delays to ensure different timestamps
        import time
        
        contact1 = ContactFactory.create(
            investment_company=company,
            name="First Contact"
        )
        db_session.commit()
        time.sleep(0.01)  # Small delay to ensure different timestamps
        
        contact2 = ContactFactory.create(
            investment_company=company,
            name="Second Contact"
        )
        db_session.commit()
        time.sleep(0.01)
        
        contact3 = ContactFactory.create(
            investment_company=company,
            name="Third Contact"
        )
        db_session.commit()
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Act: Retrieve contacts sorted by created_at
        contacts_by_created = contact_service.get_contacts(
            session=db_session,
            company_ids=[company.id],
            sort_by=SortFieldContact.CREATED_AT,
            sort_order=SortOrder.ASC
        )
        
        # Assert: Verify contacts are sorted by creation time
        assert len(contacts_by_created) == 3
        assert contacts_by_created[0].name == "First Contact"
        assert contacts_by_created[1].name == "Second Contact"
        assert contacts_by_created[2].name == "Third Contact"
        
        # Verify timestamps are in ascending order
        for i in range(len(contacts_by_created) - 1):
            assert contacts_by_created[i].created_at <= contacts_by_created[i + 1].created_at

    def test_contact_workflow_edge_case_empty_results(self, db_session):
        """Test contact retrieval when no contacts exist"""
        # Setup factories with session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        
        # Create company with no contacts
        company = InvestmentCompanyFactory.create()
        db_session.commit()
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Act: Retrieve contacts for company with no contacts
        contacts = contact_service.get_contacts(
            session=db_session,
            company_ids=[company.id]
        )
        
        # Assert: Should return empty list
        assert isinstance(contacts, list)
        assert len(contacts) == 0

    def test_contact_workflow_error_handling_invalid_sort_field(self, db_session):
        """Test error handling for invalid sort field in repository"""
        # Setup factories with session
        for factory in (InvestmentCompanyFactory, ContactFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create company and contact
        company = InvestmentCompanyFactory.create()
        ContactFactory.create(investment_company=company)
        db_session.commit()
        
        # Initialize service
        contact_service = CompanyContactService()
        
        # Act & Assert: Should raise ValueError for invalid sort field
        with pytest.raises(ValueError, match="Invalid sort field"):
            # Access repository directly to test validation
            contact_service.company_contact_repository.get_contacts(
                session=db_session,
                company_ids=[company.id],
                sort_by="INVALID_FIELD",  # This should cause validation error
                sort_order=SortOrder.ASC
            )
