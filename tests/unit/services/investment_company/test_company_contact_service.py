"""
Company Contact Service Unit Tests.

This module tests the CompanyContactService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository logic directly.

Test Coverage:
- Contact retrieval operations
- Contact creation with company validation
- Contact deletion
- Service layer orchestration
- Error handling
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.company.services.company_contact_service import CompanyContactService
from src.company.models import Contact, Company
from src.company.enums.company_contact_enums import SortFieldContact
from src.shared.enums.shared_enums import SortOrder
from tests.factories.company_factories import ContactFactory, CompanyFactory


class TestCompanyContactService:
    """Test suite for CompanyContactService."""

    @pytest.fixture
    def service(self):
        """Create a CompanyContactService instance for testing."""
        return CompanyContactService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_contact_data(self):
        """Sample contact data for testing."""
        return {
            'name': 'John Doe',
            'title': 'Investment Manager',
            'direct_number': '+61 2 1234 5678',
            'direct_email': 'john.doe@testcompany.com',
            'notes': 'Primary contact for investment decisions'
        }

    @pytest.fixture
    def mock_contact(self):
        """Mock contact instance."""
        return ContactFactory.build(id=1, name='John Doe')

    @pytest.fixture
    def mock_company(self):
        """Mock company instance."""
        return CompanyFactory.build(id=1, name='Test Company')

    ################################################################################
    # Test get_contacts method
    ################################################################################

    def test_get_contacts_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that get_contacts calls repository with correct parameters."""
        # Arrange
        expected_contacts = [ContactFactory.build() for _ in range(2)]
        with patch.object(service.company_contact_repository, 'get_contacts', return_value=expected_contacts) as mock_repo:
            # Act
            result = service.get_contacts(mock_session)

            # Assert
            assert result == expected_contacts
            mock_repo.assert_called_once_with(
                mock_session, 
                None, 
                SortFieldContact.NAME,
                SortOrder.ASC
            )

    def test_get_contacts_passes_filters_to_repository(self, service, mock_session):
        """Test that get_contacts passes all filters to repository."""
        # Arrange
        company_id = 1
        sort_by = SortFieldContact.NAME
        sort_order = SortOrder.DESC
        expected_contacts = [ContactFactory.build()]
        
        with patch.object(service.company_contact_repository, 'get_contacts', return_value=expected_contacts) as mock_repo:
            # Act
            result = service.get_contacts(
                mock_session, 
                company_ids=[company_id],
                sort_by=sort_by,
                sort_order=sort_order
            )

            # Assert
            assert result == expected_contacts
            mock_repo.assert_called_once_with(
                mock_session, 
                [company_id], 
                sort_by,
                sort_order
            )

    ################################################################################
    # Test get_contact_by_id method
    ################################################################################

    def test_get_contact_by_id_calls_repository_with_correct_id(self, service, mock_session, mock_contact):
        """Test that get_contact_by_id calls repository with correct ID."""
        # Arrange
        contact_id = 1
        with patch.object(service.company_contact_repository, 'get_contact_by_id', return_value=mock_contact) as mock_repo:
            # Act
            result = service.get_contact_by_id(contact_id, mock_session)

            # Assert
            assert result == mock_contact
            mock_repo.assert_called_once_with(contact_id, mock_session)

    def test_get_contact_by_id_returns_none_when_not_found(self, service, mock_session):
        """Test that get_contact_by_id returns None when contact not found."""
        # Arrange
        contact_id = 999
        with patch.object(service.company_contact_repository, 'get_contact_by_id', return_value=None) as mock_repo:
            # Act
            result = service.get_contact_by_id(contact_id, mock_session)

            # Assert
            assert result is None
            mock_repo.assert_called_once_with(contact_id, mock_session)

    ################################################################################
    # Test create_contact method
    ################################################################################

    def test_create_contact_successfully_creates_contact(self, service, mock_session, sample_contact_data, mock_contact, mock_company):
        """Test successful contact creation."""
        # Arrange
        company_id = 1
        with patch('src.company.repositories.company_repository.CompanyRepository') as mock_company_repo_class, \
             patch.object(service.company_contact_repository, 'create_contact', return_value=mock_contact) as mock_repo:
            
            # Setup company repository mock
            mock_company_repo = Mock()
            mock_company_repo.get_company_by_id.return_value = mock_company
            mock_company_repo_class.return_value = mock_company_repo
            
            # Act
            result = service.create_contact(company_id, sample_contact_data, mock_session)

            # Assert
            assert result == mock_contact
            mock_company_repo.get_company_by_id.assert_called_once_with(company_id, mock_session)
            
            expected_data = {
                **sample_contact_data,
                'company_id': company_id
            }
            mock_repo.assert_called_once_with(expected_data, mock_session)

    def test_create_contact_raises_error_when_company_not_found(self, service, mock_session, sample_contact_data):
        """Test that create_contact raises ValueError when company not found."""
        # Arrange
        company_id = 999
        with patch('src.company.repositories.company_repository.CompanyRepository') as mock_company_repo_class:
            # Setup company repository mock
            mock_company_repo = Mock()
            mock_company_repo.get_company_by_id.return_value = None
            mock_company_repo_class.return_value = mock_company_repo
            
            # Act & Assert
            with pytest.raises(ValueError, match="Company not found"):
                service.create_contact(company_id, sample_contact_data, mock_session)
            
            mock_company_repo.get_company_by_id.assert_called_once_with(company_id, mock_session)

    def test_create_contact_raises_error_when_repository_fails(self, service, mock_session, sample_contact_data, mock_company):
        """Test that create_contact raises ValueError when repository fails."""
        # Arrange
        company_id = 1
        with patch('src.company.repositories.company_repository.CompanyRepository') as mock_company_repo_class, \
             patch.object(service.company_contact_repository, 'create_contact', return_value=None) as mock_repo:
            
            # Setup company repository mock
            mock_company_repo = Mock()
            mock_company_repo.get_company_by_id.return_value = mock_company
            mock_company_repo_class.return_value = mock_company_repo
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to create contact"):
                service.create_contact(company_id, sample_contact_data, mock_session)

    def test_create_contact_preserves_original_data(self, service, mock_session, mock_contact, mock_company):
        """Test that create_contact preserves original data while adding company_id."""
        # Arrange
        company_id = 1
        contact_data = {
            'name': 'Jane Smith',
            'title': 'Analyst',
            'direct_number': '+61 2 9876 5432',
            'direct_email': 'jane.smith@testcompany.com',
            'notes': 'Secondary contact',
            'custom_field': 'custom_value'
        }
        
        with patch('src.company.repositories.company_repository.CompanyRepository') as mock_company_repo_class, \
             patch.object(service.company_contact_repository, 'create_contact', return_value=mock_contact) as mock_repo:
            
            # Setup company repository mock
            mock_company_repo = Mock()
            mock_company_repo.get_company_by_id.return_value = mock_company
            mock_company_repo_class.return_value = mock_company_repo
            
            # Act
            result = service.create_contact(company_id, contact_data, mock_session)

            # Assert
            assert result == mock_contact
            expected_data = {
                **contact_data,
                'company_id': company_id
            }
            mock_repo.assert_called_once_with(expected_data, mock_session)

    ################################################################################
    # Test delete_contact method
    ################################################################################

    def test_delete_contact_successfully_deletes_contact(self, service, mock_session, mock_contact):
        """Test successful contact deletion."""
        # Arrange
        contact_id = 1
        with patch.object(service.company_contact_repository, 'get_contact_by_id', return_value=mock_contact) as mock_get_contact, \
             patch.object(service.company_contact_repository, 'delete_contact', return_value=True) as mock_delete:
            
            # Act
            result = service.delete_contact(contact_id, mock_session)

            # Assert
            assert result is True
            mock_get_contact.assert_called_once_with(contact_id, mock_session)
            mock_delete.assert_called_once_with(contact_id, mock_session)

    def test_delete_contact_raises_error_when_contact_not_found(self, service, mock_session):
        """Test that delete_contact raises ValueError when contact not found."""
        # Arrange
        contact_id = 999
        with patch.object(service.company_contact_repository, 'get_contact_by_id', return_value=None) as mock_get_contact:
            # Act & Assert
            with pytest.raises(ValueError, match="Contact not found"):
                service.delete_contact(contact_id, mock_session)
            
            mock_get_contact.assert_called_once_with(contact_id, mock_session)

    def test_delete_contact_raises_error_when_repository_fails(self, service, mock_session, mock_contact):
        """Test that delete_contact raises ValueError when repository deletion fails."""
        # Arrange
        contact_id = 1
        with patch.object(service.company_contact_repository, 'get_contact_by_id', return_value=mock_contact) as mock_get_contact, \
             patch.object(service.company_contact_repository, 'delete_contact', return_value=False) as mock_delete:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to delete contact"):
                service.delete_contact(contact_id, mock_session)
            
            mock_get_contact.assert_called_once_with(contact_id, mock_session)
            mock_delete.assert_called_once_with(contact_id, mock_session)

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.company_contact_repository is not None
        assert hasattr(service, 'company_contact_repository')
