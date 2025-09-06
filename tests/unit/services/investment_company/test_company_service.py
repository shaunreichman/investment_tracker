"""
Enterprise-grade unit tests for CompanyService.

This module demonstrates professional testing patterns including:
- Proper test organization and structure
- Test data builders for consistent test data
- Clean mocking strategies with proper isolation
- Comprehensive test coverage with clear arrange/act/assert
- Proper setup/teardown for test isolation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any

from src.investment_company.services.company_service import CompanyService
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.enums import CompanyType, CompanyStatus
from src.fund.models import Fund
from src.entity.models import Entity


class CompanyTestDataBuilder:
    """Test data builder for creating consistent test objects."""
    
    @staticmethod
    def create_company(**kwargs) -> Mock:
        """Create a mock InvestmentCompany with sensible defaults."""
        defaults = {
            'id': 1,
            'name': 'Test Company',
            'description': 'Test Description',
            'website': 'https://test.com',
            'company_type': CompanyType.PRIVATE_EQUITY,
            'status': CompanyStatus.ACTIVE,
            'business_address': '123 Test St',
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
            'funds': [],
            'contacts': []
        }
        defaults.update(kwargs)
        
        company = Mock(spec=InvestmentCompany)
        for key, value in defaults.items():
            setattr(company, key, value)
        return company
    
    @staticmethod
    def create_contact(**kwargs) -> Mock:
        """Create a mock Contact with sensible defaults."""
        defaults = {
            'id': 1,
            'name': 'John Doe',
            'title': 'Manager',
            'direct_number': '+1234567890',
            'direct_email': 'john@test.com',
            'notes': 'Test contact',
            'created_at': datetime.now(timezone.utc),
            'investment_company_id': 1
        }
        defaults.update(kwargs)
        
        contact = Mock(spec=Contact)
        for key, value in defaults.items():
            setattr(contact, key, value)
        return contact
    
    @staticmethod
    def create_fund(**kwargs) -> Mock:
        """Create a mock Fund with sensible defaults."""
        defaults = {
            'id': 1,
            'name': 'Test Fund',
            'fund_type': 'Private Equity',
            'tracking_type': 'ACTIVE',
            'entity_id': 1,
            'investment_company_id': 1,
            'created_at': datetime.now(timezone.utc)
        }
        defaults.update(kwargs)
        
        fund = Mock(spec=Fund)
        for key, value in defaults.items():
            setattr(fund, key, value)
        return fund
    
    @staticmethod
    def create_company_data(**kwargs) -> Dict[str, Any]:
        """Create company data dictionary with sensible defaults."""
        defaults = {
            'name': 'Test Company',
            'description': 'Test Description',
            'website': 'https://test.com',
            'company_type': 'Private Equity',
            'business_address': '123 Test St'
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_contact_data(**kwargs) -> Dict[str, Any]:
        """Create contact data dictionary with sensible defaults."""
        defaults = {
            'name': 'John Doe',
            'title': 'Manager',
            'direct_number': '+1234567890',
            'direct_email': 'john@test.com',
            'notes': 'Test contact'
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_fund_data(**kwargs) -> Dict[str, Any]:
        """Create fund data dictionary with sensible defaults."""
        defaults = {
            'entity': 'Test Entity',
            'name': 'Test Fund',
            'fund_type': 'Private Equity',
            'tracking_type': 'ACTIVE',
            'currency': 'AUD',
            'description': 'Test fund description',
            'commitment_amount': 1000000,
            'expected_irr': 15.5,
            'expected_duration_months': 60
        }
        defaults.update(kwargs)
        return defaults


class TestCompanyService:
    """Enterprise-grade test suite for CompanyService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_session = Mock(spec=Session)
        self.service = CompanyService()
        
        # Store original service attributes for restoration
        self._original_attributes = {
            'company_repository': self.service.company_repository,
            'contact_repository': self.service.contact_repository,
            'portfolio_service': self.service.portfolio_service,
            'summary_service': self.service.summary_service,
            'contact_service': self.service.contact_service,
            'validation_service': self.service.validation_service
        }
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Restore original service attributes to prevent test pollution
        for attr_name, original_value in self._original_attributes.items():
            setattr(self.service, attr_name, original_value)
    
    def _mock_service_dependencies(self):
        """Mock all service dependencies for isolated testing."""
        self.service.company_repository = Mock()
        self.service.contact_repository = Mock()
        self.service.portfolio_service = Mock()
        self.service.summary_service = Mock()
        self.service.contact_service = Mock()
        self.service.validation_service = Mock()


class TestCompanyServiceInitialization(TestCompanyService):
    """Test CompanyService initialization and dependency management."""
    
    def test_init_creates_all_required_services(self):
        """Test that CompanyService initializes all required service dependencies."""
        # Arrange & Act
        service = CompanyService()
        
        # Assert
        assert service.company_repository is not None
        assert service.contact_repository is not None
        assert service.portfolio_service is not None
        assert service.summary_service is not None
        assert service.contact_service is not None
        assert service.validation_service is not None


class TestCompanyServiceCreation(TestCompanyService):
    """Test company creation functionality."""
    
    def setup_method(self):
        """Set up test fixtures for creation tests."""
        super().setup_method()
        self._mock_service_dependencies()
    
    def test_create_company_success(self):
        """Test successful company creation with all required data."""
        # Arrange
        company_data = CompanyTestDataBuilder.create_company_data()
        mock_company = CompanyTestDataBuilder.create_company()
        
        self.service.validation_service.validate_company_creation.return_value = {}
        self.service.company_repository.create.return_value = mock_company
        
        # Act
        result = self.service.create_company(
            name=company_data['name'],
            description=company_data['description'],
            website=company_data['website'],
            company_type=company_data['company_type'],
            business_address=company_data['business_address'],
            session=self.mock_session
        )
        
        # Assert
        assert result == mock_company
        self.service.validation_service.validate_company_creation.assert_called_once_with(
            name=company_data['name'],
            description=company_data['description'],
            website=company_data['website'],
            company_type=company_data['company_type'],
            business_address=company_data['business_address']
        )
        self.service.company_repository.create.assert_called_once()
    
    def test_create_company_with_default_status(self):
        """Test company creation sets default status when not provided."""
        # Arrange
        mock_company = CompanyTestDataBuilder.create_company()
        
        self.service.validation_service.validate_company_creation.return_value = {}
        self.service.company_repository.create.return_value = mock_company
        
        # Act
        result = self.service.create_company(
            name='Test Company',
            session=self.mock_session
        )
        
        # Assert
        assert result == mock_company
        self.service.company_repository.create.assert_called_once()
        # Verify the repository was called with the correct data including default status
        call_args = self.service.company_repository.create.call_args
        assert call_args[0][0]['status'] == CompanyStatus.ACTIVE.value
    
    def test_create_company_with_custom_status(self):
        """Test company creation with custom status."""
        # Arrange
        mock_company = CompanyTestDataBuilder.create_company()
        
        self.service.validation_service.validate_company_creation.return_value = {}
        self.service.company_repository.create.return_value = mock_company
        
        # Act
        result = self.service.create_company(
            name='Test Company',
            status='INACTIVE',
            session=self.mock_session
        )
        
        # Assert
        assert result == mock_company
        self.service.company_repository.create.assert_called_once()
        # Verify the repository was called with the correct data including custom status
        call_args = self.service.company_repository.create.call_args
        assert call_args[0][0]['status'] == 'INACTIVE'
    
    def test_create_company_validation_failure(self):
        """Test company creation fails when validation fails."""
        # Arrange
        validation_errors = {'name': ['Company name is required']}
        self.service.validation_service.validate_company_creation.return_value = validation_errors
        
        # Act & Assert
        with pytest.raises(ValueError, match="Validation failed: {'name': \\['Company name is required'\\]}"):
            self.service.create_company(
                name='',
                session=self.mock_session
            )


class TestCompanyServiceUpdate(TestCompanyService):
    """Test company update functionality."""
    
    def setup_method(self):
        """Set up test fixtures for update tests."""
        super().setup_method()
        self._mock_service_dependencies()
    
    def test_update_company_success(self):
        """Test successful company update."""
        # Arrange
        company_data = {'name': 'Updated Company', 'description': 'Updated Description'}
        mock_company = CompanyTestDataBuilder.create_company()
        
        self.service.company_repository.get_by_id.return_value = mock_company
        self.service.company_repository.update.return_value = mock_company
        self.service.validation_service.validate_company_update.return_value = {}
        
        # Act
        result = self.service.update_company(
            company_id=1,
            company_data=company_data,
            session=self.mock_session
        )
        
        # Assert
        assert result == mock_company
        self.service.company_repository.get_by_id.assert_called_once_with(1, self.mock_session)
        self.service.company_repository.update.assert_called_once_with(1, company_data, self.mock_session)
        self.service.validation_service.validate_company_update.assert_called_once()
    
    def test_update_company_not_found(self):
        """Test company update when company doesn't exist."""
        # Arrange
        self.service.company_repository.get_by_id.return_value = None
        
        # Act
        result = self.service.update_company(
            company_id=999,
            company_data={'name': 'Updated'},
            session=self.mock_session
        )
        
        # Assert
        assert result is None
        self.service.company_repository.get_by_id.assert_called_once_with(999, self.mock_session)
    
    def test_update_company_validation_failure(self):
        """Test company update fails when validation fails."""
        # Arrange
        mock_company = CompanyTestDataBuilder.create_company()
        validation_errors = {'name': ['Company name is required']}
        
        self.service.company_repository.get_by_id.return_value = mock_company
        self.service.validation_service.validate_company_update.return_value = validation_errors
        
        # Act & Assert
        with pytest.raises(ValueError, match="Validation failed: {'name': \\['Company name is required'\\]}"):
            self.service.update_company(
                company_id=1,
                company_data={'name': ''},
                session=self.mock_session
            )
    
    def test_update_company_delegates_to_repository(self):
        """Test that company update delegates to repository."""
        # Arrange
        company_data = {'name': 'Updated Company'}
        mock_company = CompanyTestDataBuilder.create_company()
        
        self.service.company_repository.get_by_id.return_value = mock_company
        self.service.company_repository.update.return_value = mock_company
        self.service.validation_service.validate_company_update.return_value = {}
        
        # Act
        result = self.service.update_company(
            company_id=1,
            company_data=company_data,
            session=self.mock_session
        )
        
        # Assert
        assert result == mock_company
        self.service.company_repository.update.assert_called_once_with(1, company_data, self.mock_session)


class TestCompanyServiceDeletion(TestCompanyService):
    """Test company deletion functionality."""
    
    def setup_method(self):
        """Set up test fixtures for deletion tests."""
        super().setup_method()
        self._mock_service_dependencies()
    
    def test_delete_company_success(self):
        """Test successful company deletion."""
        # Arrange
        mock_company = CompanyTestDataBuilder.create_company()
        
        self.service.company_repository.get_by_id.return_value = mock_company
        self.service.company_repository.delete.return_value = True
        self.service.validation_service.validate_company_deletion.return_value = {}
        
        # Act
        result = self.service.delete_company(
            company_id=1,
            session=self.mock_session
        )
        
        # Assert
        assert result is True
        self.service.company_repository.get_by_id.assert_called_once_with(1, self.mock_session)
        self.service.company_repository.delete.assert_called_once_with(1, self.mock_session)
        self.service.validation_service.validate_company_deletion.assert_called_once_with(mock_company, self.mock_session)
    
    def test_delete_company_not_found(self):
        """Test company deletion when company doesn't exist."""
        # Arrange
        self.service.company_repository.get_by_id.return_value = None
        
        # Act
        result = self.service.delete_company(
            company_id=999,
            session=self.mock_session
        )
        
        # Assert
        assert result is False
        self.service.company_repository.get_by_id.assert_called_once_with(999, self.mock_session)
    
    def test_delete_company_validation_failure(self):
        """Test company deletion fails when validation fails."""
        # Arrange
        mock_company = CompanyTestDataBuilder.create_company()
        validation_errors = {'funds': ['Cannot delete company with active funds']}
        
        self.service.company_repository.get_by_id.return_value = mock_company
        self.service.validation_service.validate_company_deletion.return_value = validation_errors
        
        # Act & Assert
        with pytest.raises(ValueError, match="Deletion validation failed: {'funds': \\['Cannot delete company with active funds'\\]}"):
            self.service.delete_company(
                company_id=1,
                session=self.mock_session
            )


class TestCompanyServiceRetrieval(TestCompanyService):
    """Test company retrieval functionality."""
    
    def setup_method(self):
        """Set up test fixtures for retrieval tests."""
        super().setup_method()
        self._mock_service_dependencies()
    
    def test_get_company_summary_success(self):
        """Test successful company summary retrieval."""
        # Arrange
        mock_company = CompanyTestDataBuilder.create_company()
        expected_summary = {'total_funds': 5, 'total_contacts': 3}
        
        self.service.company_repository.get_by_id.return_value = mock_company
        self.service.summary_service.get_company_summary_data.return_value = expected_summary
        
        # Act
        result = self.service.get_company_summary(
            company_id=1,
            session=self.mock_session
        )
        
        # Assert
        assert result == expected_summary
        self.service.company_repository.get_by_id.assert_called_once_with(1, self.mock_session)
        self.service.summary_service.get_company_summary_data.assert_called_once_with(mock_company, self.mock_session)
    
    def test_get_company_summary_not_found(self):
        """Test company summary retrieval when company doesn't exist."""
        # Arrange
        self.service.company_repository.get_by_id.return_value = None
        
        # Act
        result = self.service.get_company_summary(
            company_id=999,
            session=self.mock_session
        )
        
        # Assert
        assert result is None
        self.service.company_repository.get_by_id.assert_called_once_with(999, self.mock_session)
    
    def test_get_company_performance_success(self):
        """Test successful company performance retrieval."""
        # Arrange
        mock_company = CompanyTestDataBuilder.create_company()
        expected_performance = {'total_irr': 15.5, 'fund_count': 3}
        
        self.service.company_repository.get_by_id.return_value = mock_company
        self.service.summary_service.get_company_performance_summary.return_value = expected_performance
        
        # Act
        result = self.service.get_company_performance(
            company_id=1,
            session=self.mock_session
        )
        
        # Assert
        assert result == expected_performance
        self.service.company_repository.get_by_id.assert_called_once_with(1, self.mock_session)
        self.service.summary_service.get_company_performance_summary.assert_called_once_with(mock_company, self.mock_session)
    
    def test_get_company_performance_not_found(self):
        """Test company performance retrieval when company doesn't exist."""
        # Arrange
        self.service.company_repository.get_by_id.return_value = None
        
        # Act
        result = self.service.get_company_performance(
            company_id=999,
            session=self.mock_session
        )
        
        # Assert
        assert result is None
        self.service.company_repository.get_by_id.assert_called_once_with(999, self.mock_session)
    
    def test_get_all_companies(self):
        """Test retrieval of all companies."""
        # Arrange
        expected_companies = [CompanyTestDataBuilder.create_company()]
        self.service.company_repository.get_all.return_value = expected_companies
        
        # Act
        result = self.service.get_all_companies(self.mock_session)
        
        # Assert
        assert result == expected_companies
        self.service.company_repository.get_all.assert_called_once_with(self.mock_session)
    
    def test_get_company_by_id_success(self):
        """Test successful company retrieval by ID."""
        # Arrange
        mock_company = CompanyTestDataBuilder.create_company()
        self.service.company_repository.get_by_id.return_value = mock_company
        
        # Act
        result = self.service.get_company_by_id(
            company_id=1,
            session=self.mock_session
        )
        
        # Assert
        assert result == mock_company
        self.service.company_repository.get_by_id.assert_called_once_with(1, self.mock_session)
    
    def test_get_company_by_id_not_found(self):
        """Test company retrieval by ID when company doesn't exist."""
        # Arrange
        self.service.company_repository.get_by_id.return_value = None
        
        # Act
        result = self.service.get_company_by_id(
            company_id=999,
            session=self.mock_session
        )
        
        # Assert
        assert result is None
        self.service.company_repository.get_by_id.assert_called_once_with(999, self.mock_session)


class TestCompanyServiceContactManagement(TestCompanyService):
    """Test contact management functionality."""
    
    def setup_method(self):
        """Set up test fixtures for contact management tests."""
        super().setup_method()
        self._mock_service_dependencies()
    
    def test_add_contact_to_company_success(self):
        """Test successful contact addition to company."""
        # Arrange
        contact_data = CompanyTestDataBuilder.create_contact_data()
        mock_company = CompanyTestDataBuilder.create_company()
        mock_contact = CompanyTestDataBuilder.create_contact()
        
        self.service.company_repository.get_by_id.return_value = mock_company
        self.service.contact_service.add_contact.return_value = mock_contact
        
        # Act
        result = self.service.add_contact_to_company(
            company_id=1,
            contact_data=contact_data,
            session=self.mock_session
        )
        
        # Assert
        assert result == mock_contact
        self.service.company_repository.get_by_id.assert_called_once_with(1, self.mock_session)
        self.service.contact_service.add_contact.assert_called_once_with(
            company=mock_company,
            name=contact_data['name'],
            title=contact_data['title'],
            direct_number=contact_data['direct_number'],
            direct_email=contact_data['direct_email'],
            notes=contact_data['notes'],
            session=self.mock_session
        )
    
    def test_add_contact_to_company_not_found(self):
        """Test contact addition when company doesn't exist."""
        # Arrange
        self.service.company_repository.get_by_id.return_value = None
        
        # Act
        result = self.service.add_contact_to_company(
            company_id=999,
            contact_data={'name': 'John Doe'},
            session=self.mock_session
        )
        
        # Assert
        assert result is None
        self.service.company_repository.get_by_id.assert_called_once_with(999, self.mock_session)


class TestCompanyServiceFundManagement(TestCompanyService):
    """Test fund management functionality."""
    
    def setup_method(self):
        """Set up test fixtures for fund management tests."""
        super().setup_method()
        self._mock_service_dependencies()
    
    def test_create_fund_for_company_success(self):
        """Test successful fund creation for company."""
        # Arrange
        fund_data = CompanyTestDataBuilder.create_fund_data()
        mock_company = CompanyTestDataBuilder.create_company()
        mock_fund = CompanyTestDataBuilder.create_fund()
        
        self.service.company_repository.get_by_id.return_value = mock_company
        self.service.portfolio_service.create_fund.return_value = mock_fund
        
        # Act
        result = self.service.create_fund_for_company(
            company_id=1,
            fund_data=fund_data,
            session=self.mock_session
        )
        
        # Assert
        assert result == mock_fund
        self.service.company_repository.get_by_id.assert_called_once_with(1, self.mock_session)
        self.service.portfolio_service.create_fund.assert_called_once_with(
            company=mock_company,
            entity=fund_data['entity'],
            name=fund_data['name'],
            fund_type=fund_data['fund_type'],
            tracking_type=fund_data['tracking_type'],
            currency=fund_data['currency'],
            description=fund_data['description'],
            commitment_amount=fund_data['commitment_amount'],
            expected_irr=fund_data['expected_irr'],
            expected_duration_months=fund_data['expected_duration_months'],
            session=self.mock_session
        )
    
    def test_create_fund_for_company_not_found(self):
        """Test fund creation when company doesn't exist."""
        # Arrange
        self.service.company_repository.get_by_id.return_value = None
        
        # Act
        result = self.service.create_fund_for_company(
            company_id=999,
            fund_data={'name': 'Test Fund'},
            session=self.mock_session
        )
        
        # Assert
        assert result is None
        self.service.company_repository.get_by_id.assert_called_once_with(999, self.mock_session)
