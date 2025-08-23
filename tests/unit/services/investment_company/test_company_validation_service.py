"""
Enterprise-grade unit tests for CompanyValidationService.

This module demonstrates professional testing patterns including:
- Proper test organization and structure
- Test data builders for consistent test data
- Clean test isolation with proper setup/teardown
- Comprehensive test coverage with clear arrange/act/assert
- Logical grouping of related test scenarios
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from src.investment_company.services.company_validation_service import CompanyValidationService
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.enums import CompanyType, CompanyStatus


class ValidationTestDataBuilder:
    """Test data builder for creating consistent validation test objects."""
    
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
            'status': Mock(),
            'investment_company_id': 1
        }
        defaults['status'].value = kwargs.get('status_value', 'ACTIVE')
        defaults.update(kwargs)
        
        fund = Mock()
        for key, value in defaults.items():
            if key != 'status_value':
                setattr(fund, key, value)
        return fund
    
    @staticmethod
    def create_session() -> Mock:
        """Create a mock database session."""
        return Mock(spec=Session)


class TestCompanyValidationService:
    """Enterprise-grade test suite for CompanyValidationService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.validation_service = CompanyValidationService()
        self.mock_session = ValidationTestDataBuilder.create_session()
    
    def teardown_method(self):
        """Clean up after each test method."""
        pass  # No cleanup needed for this service


class TestCompanyValidationServiceInitialization(TestCompanyValidationService):
    """Test CompanyValidationService initialization."""
    
    def test_init_creates_service(self):
        """Test that CompanyValidationService initializes correctly."""
        # Arrange & Act
        service = CompanyValidationService()
        
        # Assert
        assert service is not None
        assert isinstance(service, CompanyValidationService)


class TestCompanyCreationValidation(TestCompanyValidationService):
    """Test company creation validation methods."""
    
    def test_validate_company_creation_success(self):
        """Test successful company creation validation."""
        # Arrange
        company_data = {
            'name': 'Test Company',
            'description': 'Test Description',
            'website': 'https://test.com',
            'company_type': 'Private Equity',
            'business_address': '123 Test St'
        }
        
        # Act
        errors = self.validation_service.validate_company_creation(
            name=company_data['name'],
            description=company_data['description'],
            website=company_data['website'],
            company_type=company_data['company_type'],
            business_address=company_data['business_address']
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_company_creation_missing_name(self):
        """Test company creation validation fails with missing name."""
        # Act
        errors = self.validation_service.validate_company_creation(
            name='',
            description='Test Description'
        )
        
        # Assert
        assert 'name' in errors
        assert 'Company name is required' in errors['name']
    
    def test_validate_company_creation_whitespace_name(self):
        """Test company creation validation fails with whitespace-only name."""
        # Act
        errors = self.validation_service.validate_company_creation(
            name='   ',
            description='Test Description'
        )
        
        # Assert
        assert 'name' in errors
        assert 'Company name is required' in errors['name']
    
    def test_validate_company_creation_name_too_long(self):
        """Test company creation validation fails with name too long."""
        # Arrange
        long_name = 'A' * 256
        
        # Act
        errors = self.validation_service.validate_company_creation(
            name=long_name,
            description='Test Description'
        )
        
        # Assert
        assert 'name' in errors
        assert 'Company name must be 255 characters or less' in errors['name']
    
    def test_validate_company_creation_invalid_company_type(self):
        """Test company creation validation fails with invalid company type."""
        # Act
        errors = self.validation_service.validate_company_creation(
            name='Test Company',
            company_type='Invalid Type'
        )
        
        # Assert
        assert 'company_type' in errors
        assert 'Invalid company type' in errors['company_type']
    
    def test_validate_company_creation_valid_company_types(self):
        """Test company creation validation succeeds with all valid company types."""
        # Arrange
        valid_types = [
            'Private Equity', 'Venture Capital', 'Real Estate', 'Infrastructure',
            'Credit', 'Hedge Fund', 'Family Office', 'Investment Bank',
            'Asset Management', 'Other'
        ]
        
        # Act & Assert
        for company_type in valid_types:
            errors = self.validation_service.validate_company_creation(
                name='Test Company',
                company_type=company_type
            )
            assert 'company_type' not in errors, f"Failed for type: {company_type}"
    
    def test_validate_company_creation_invalid_website(self):
        """Test company creation validation fails with invalid website."""
        # Arrange
        invalid_websites = [
            'not-a-url',
            'ftp://invalid.com',
            'http://',
            'https://',
            'www.invalid.com',
            'invalid.com'
        ]
        
        # Act & Assert
        for website in invalid_websites:
            errors = self.validation_service.validate_company_creation(
                name='Test Company',
                website=website
            )
            assert 'website' in errors, f"Failed for website: {website}"
            assert 'Invalid website URL format' in errors['website']
    
    def test_validate_company_creation_valid_websites(self):
        """Test company creation validation succeeds with valid websites."""
        # Arrange
        valid_websites = [
            'https://example.com',
            'http://example.com',
            'https://www.example.com',
            'https://subdomain.example.com',
            'https://example.com/path',
            'https://example.com/path?param=value'
        ]
        
        # Act & Assert
        for website in valid_websites:
            errors = self.validation_service.validate_company_creation(
                name='Test Company',
                website=website
            )
            assert 'website' not in errors, f"Failed for website: {website}"


class TestCompanyUpdateValidation(TestCompanyValidationService):
    """Test company update validation methods."""
    
    def test_validate_company_update_success(self):
        """Test successful company update validation."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        
        # Act
        errors = self.validation_service.validate_company_update(
            company=mock_company,
            name='Updated Company',
            description='Updated Description'
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_company_update_no_changes(self):
        """Test company update validation with no changes."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        
        # Act
        errors = self.validation_service.validate_company_update(
            company=mock_company
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_company_update_invalid_name(self):
        """Test company update validation fails with invalid name."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        
        # Act
        errors = self.validation_service.validate_company_update(
            company=mock_company,
            name=''
        )
        
        # Assert
        assert 'name' in errors
        assert 'Company name is required' in errors['name']
    
    def test_validate_company_update_invalid_status(self):
        """Test company update validation fails with invalid status."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        
        # Act
        errors = self.validation_service.validate_company_update(
            company=mock_company,
            status='INVALID_STATUS'
        )
        
        # Assert
        assert 'status' in errors
        assert 'Invalid company status' in errors['status']
    
    def test_validate_company_update_valid_statuses(self):
        """Test company update validation succeeds with all valid statuses."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        valid_statuses = ['ACTIVE', 'INACTIVE', 'SUSPENDED', 'CLOSED']
        
        # Act & Assert
        for status in valid_statuses:
            errors = self.validation_service.validate_company_update(
                company=mock_company,
                status=status
            )
            assert 'status' not in errors, f"Failed for status: {status}"


class TestContactValidation(TestCompanyValidationService):
    """Test contact validation methods."""
    
    def test_validate_contact_creation_success(self):
        """Test successful contact creation validation."""
        # Act
        errors = self.validation_service.validate_contact_creation(
            name='John Doe',
            title='Manager',
            direct_number='+1234567890',
            direct_email='john@test.com',
            notes='Test contact'
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_contact_creation_missing_name(self):
        """Test contact creation validation fails with missing name."""
        # Act
        errors = self.validation_service.validate_contact_creation(
            name='',
            title='Manager'
        )
        
        # Assert
        assert 'name' in errors
        assert 'Contact name is required' in errors['name']
    
    def test_validate_contact_creation_name_too_long(self):
        """Test contact creation validation fails with name too long."""
        # Arrange
        long_name = 'A' * 256
        
        # Act
        errors = self.validation_service.validate_contact_creation(
            name=long_name,
            title='Manager'
        )
        
        # Assert
        assert 'name' in errors
        assert 'Contact name must be 255 characters or less' in errors['name']
    
    def test_validate_contact_creation_invalid_email(self):
        """Test contact creation validation fails with invalid email."""
        # Arrange
        invalid_emails = [
            'not-an-email',
            'missing@domain',
            '@missing-local.com',
            'spaces in@email.com',
            'multiple@@at.com'
        ]
        
        # Act & Assert
        for email in invalid_emails:
            errors = self.validation_service.validate_contact_creation(
                name='John Doe',
                direct_email=email
            )
            assert 'direct_email' in errors, f"Failed for email: {email}"
            assert 'Invalid email format' in errors['direct_email']
    
    def test_validate_contact_creation_valid_emails(self):
        """Test contact creation validation succeeds with valid emails."""
        # Arrange
        valid_emails = [
            'test@example.com',
            'user.name@domain.com',
            'user+tag@example.co.uk',
            '123@numbers.com',
            'user-name@domain.org',
            '.start@email.com',  # This is technically valid per RFC standards
            'end.@email.com'     # This is technically valid per RFC standards
        ]
        
        # Act & Assert
        for email in valid_emails:
            errors = self.validation_service.validate_contact_creation(
                name='John Doe',
                direct_email=email
            )
            assert 'direct_email' not in errors, f"Failed for email: {email}"
    
    def test_validate_contact_creation_invalid_phone(self):
        """Test contact creation validation fails with invalid phone numbers."""
        # Arrange
        invalid_phones = [
            '123',  # Too short
            'A1234567890',  # Contains letters
            '123-456-7890-1234567890',  # Too long
            '123.456.7890',  # Invalid format
            '123/456/7890'   # Invalid format
        ]
        
        # Act & Assert
        for phone in invalid_phones:
            errors = self.validation_service.validate_contact_creation(
                name='John Doe',
                direct_number=phone
            )
            assert 'direct_number' in errors, f"Failed for phone: {phone}"
            assert 'Invalid phone number format' in errors['direct_number']
    
    def test_validate_contact_creation_valid_phones(self):
        """Test contact creation validation succeeds with valid phone numbers."""
        # Arrange
        valid_phones = [
            '+1234567890',
            '123-456-7890',
            '(123) 456-7890',
            '123 456 7890',
            '+1 (234) 567-8900',
            '1234567890'
        ]
        
        # Act & Assert
        for phone in valid_phones:
            errors = self.validation_service.validate_contact_creation(
                name='John Doe',
                direct_number=phone
            )
            assert 'direct_number' not in errors, f"Failed for phone: {phone}"
    
    def test_validate_contact_update_success(self):
        """Test successful contact update validation."""
        # Arrange
        mock_contact = ValidationTestDataBuilder.create_contact()
        
        # Act
        errors = self.validation_service.validate_contact_update(
            contact=mock_contact,
            name='Updated Name',
            title='Updated Title'
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_contact_update_no_changes(self):
        """Test contact update validation with no changes."""
        # Arrange
        mock_contact = ValidationTestDataBuilder.create_contact()
        
        # Act
        errors = self.validation_service.validate_contact_update(
            contact=mock_contact
        )
        
        # Assert
        assert errors == {}


class TestCompanyDeletionValidation(TestCompanyValidationService):
    """Test company deletion validation methods."""
    
    def test_validate_company_deletion_success(self):
        """Test successful company deletion validation."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        
        # Act
        errors = self.validation_service.validate_company_deletion(
            company=mock_company,
            session=self.mock_session
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_company_deletion_with_active_funds(self):
        """Test company deletion validation fails with active funds."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        mock_fund = ValidationTestDataBuilder.create_fund(status_value='ACTIVE')
        mock_company.funds = [mock_fund]
        
        # Act
        errors = self.validation_service.validate_company_deletion(
            company=mock_company,
            session=self.mock_session
        )
        
        # Assert
        assert 'funds' in errors
        assert 'Cannot delete company with 1 active funds' in errors['funds']
    
    def test_validate_company_deletion_with_contacts(self):
        """Test company deletion validation fails with contacts."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        mock_contact = ValidationTestDataBuilder.create_contact()
        mock_company.contacts = [mock_contact]
        
        # Act
        errors = self.validation_service.validate_company_deletion(
            company=mock_company,
            session=self.mock_session
        )
        
        # Assert
        assert 'contacts' in errors
        assert 'Cannot delete company with 1 contacts' in errors['contacts']
    
    def test_validate_company_deletion_with_multiple_funds_and_contacts(self):
        """Test company deletion validation fails with multiple funds and contacts."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        
        mock_fund1 = ValidationTestDataBuilder.create_fund(status_value='ACTIVE')
        mock_fund2 = ValidationTestDataBuilder.create_fund(status_value='ACTIVE')
        
        mock_contact1 = ValidationTestDataBuilder.create_contact()
        mock_contact2 = ValidationTestDataBuilder.create_contact()
        mock_contact3 = ValidationTestDataBuilder.create_contact()
        
        mock_company.funds = [mock_fund1, mock_fund2]  # 2 funds
        mock_company.contacts = [mock_contact1, mock_contact2, mock_contact3]  # 3 contacts
        
        # Act
        errors = self.validation_service.validate_company_deletion(
            company=mock_company,
            session=self.mock_session
        )
        
        # Assert
        assert 'funds' in errors
        assert 'Cannot delete company with 2 active funds' in errors['funds']
        assert 'contacts' in errors
        assert 'Cannot delete company with 3 contacts' in errors['contacts']


class TestDataIntegrityValidation(TestCompanyValidationService):
    """Test data integrity validation methods."""
    
    def test_validate_company_data_integrity_success(self):
        """Test successful company data integrity validation."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        
        # Act
        errors = self.validation_service.validate_company_data_integrity(
            company=mock_company,
            session=self.mock_session
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_company_data_integrity_missing_name(self):
        """Test company data integrity validation fails with missing name."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        mock_company.name = ''
        
        # Act
        errors = self.validation_service.validate_company_data_integrity(
            company=mock_company,
            session=self.mock_session
        )
        
        # Assert
        assert 'name' in errors
        assert 'Company name is required' in errors['name']
    
    def test_validate_company_data_integrity_whitespace_name(self):
        """Test company data integrity validation fails with whitespace-only name."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        mock_company.name = '   '
        
        # Act
        errors = self.validation_service.validate_company_data_integrity(
            company=mock_company,
            session=self.mock_session
        )
        
        # Assert
        assert 'name' in errors
        assert 'Company name is required' in errors['name']
    
    def test_validate_company_data_integrity_fund_relationship_violation(self):
        """Test company data integrity validation fails with fund relationship violation."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        mock_fund = ValidationTestDataBuilder.create_fund()
        mock_fund.investment_company_id = 999  # Different company ID
        mock_company.funds = [mock_fund]
        
        # Act
        errors = self.validation_service.validate_company_data_integrity(
            company=mock_company,
            session=self.mock_session
        )
        
        # Assert
        assert 'funds' in errors
        assert 'Fund relationship integrity violation' in errors['funds']
    
    def test_validate_company_data_integrity_contact_relationship_violation(self):
        """Test company data integrity validation fails with contact relationship violation."""
        # Arrange
        mock_company = ValidationTestDataBuilder.create_company()
        mock_contact = ValidationTestDataBuilder.create_contact()
        mock_contact.investment_company_id = 999  # Different company ID
        mock_company.contacts = [mock_contact]
        
        # Act
        errors = self.validation_service.validate_company_data_integrity(
            company=mock_company,
            session=self.mock_session
        )
        
        # Assert
        assert 'contacts' in errors
        assert 'Contact relationship integrity violation' in errors['contacts']


class TestBusinessRules(TestCompanyValidationService):
    """Test business rules documentation methods."""
    
    def test_get_company_business_rules(self):
        """Test that business rules are returned correctly."""
        # Act
        rules = self.validation_service.get_company_business_rules()
        
        # Assert
        assert isinstance(rules, dict)
        assert 'naming' in rules
        assert 'relationships' in rules
        assert 'deletion' in rules
        assert 'validation' in rules
        
        # Verify naming rules
        naming_rules = rules['naming']
        assert 'Company name must be unique across the system' in naming_rules
        assert 'Company name cannot be empty or contain only whitespace' in naming_rules
        assert 'Company name should be descriptive and professional' in naming_rules
        
        # Verify relationship rules
        relationship_rules = rules['relationships']
        assert 'Company can have multiple funds' in relationship_rules
        assert 'Company can have multiple contacts' in relationship_rules
        assert 'Funds must reference valid company ID' in relationship_rules
        assert 'Contacts must reference valid company ID' in relationship_rules
        
        # Verify deletion rules
        deletion_rules = rules['deletion']
        assert 'Company cannot be deleted if it has active funds' in deletion_rules
        assert 'Company cannot be deleted if it has contacts' in deletion_rules
        assert 'Deletion is permanent and cannot be undone' in deletion_rules
        
        # Verify validation rules
        validation_rules = rules['validation']
        assert 'Website URL must be valid format if provided' in validation_rules
        assert 'Company type must be from approved list if specified' in validation_rules
        assert 'Company status must be from approved list' in validation_rules
        assert 'All required fields must be provided' in validation_rules


class TestPrivateValidationMethods(TestCompanyValidationService):
    """Test private validation helper methods."""
    
    def test_is_valid_website(self):
        """Test website validation helper method."""
        # Valid websites
        assert self.validation_service._is_valid_website('https://example.com')
        assert self.validation_service._is_valid_website('http://example.com')
        assert self.validation_service._is_valid_website('https://www.example.com')
        assert self.validation_service._is_valid_website('https://subdomain.example.com')
        
        # Invalid websites
        assert not self.validation_service._is_valid_website('not-a-url')
        assert not self.validation_service._is_valid_website('ftp://example.com')
        assert not self.validation_service._is_valid_website('http://')
        assert not self.validation_service._is_valid_website('www.example.com')
    
    def test_is_valid_company_type(self):
        """Test company type validation helper method."""
        # Valid types
        assert self.validation_service._is_valid_company_type('Private Equity')
        assert self.validation_service._is_valid_company_type('Venture Capital')
        assert self.validation_service._is_valid_company_type('Real Estate')
        assert self.validation_service._is_valid_company_type('Other')
        
        # Invalid types
        assert not self.validation_service._is_valid_company_type('Invalid Type')
        assert not self.validation_service._is_valid_company_type('')
        assert not self.validation_service._is_valid_company_type(None)
    
    def test_is_valid_company_status(self):
        """Test company status validation helper method."""
        # Valid statuses
        assert self.validation_service._is_valid_company_status('ACTIVE')
        assert self.validation_service._is_valid_company_status('INACTIVE')
        assert self.validation_service._is_valid_company_status('SUSPENDED')
        assert self.validation_service._is_valid_company_status('CLOSED')
        
        # Invalid statuses
        assert not self.validation_service._is_valid_company_status('INVALID_STATUS')
        assert not self.validation_service._is_valid_company_status('')
        assert not self.validation_service._is_valid_company_status(None)
    
    def test_is_valid_email(self):
        """Test email validation helper method."""
        # Valid emails
        assert self.validation_service._is_valid_email('test@example.com')
        assert self.validation_service._is_valid_email('user.name@domain.com')
        assert self.validation_service._is_valid_email('user+tag@example.co.uk')
        assert self.validation_service._is_valid_email('123@numbers.com')
        
        # Invalid emails
        assert not self.validation_service._is_valid_email('not-an-email')
        assert not self.validation_service._is_valid_email('missing@domain')
        assert not self.validation_service._is_valid_email('@missing-local.com')
        assert not self.validation_service._is_valid_email('spaces in@email.com')
    
    def test_is_valid_phone_number(self):
        """Test phone number validation helper method."""
        # Valid phone numbers
        assert self.validation_service._is_valid_phone_number('+1234567890')
        assert self.validation_service._is_valid_phone_number('123-456-7890')
        assert self.validation_service._is_valid_phone_number('(123) 456-7890')
        assert self.validation_service._is_valid_phone_number('123 456 7890')
        assert self.validation_service._is_valid_phone_number('1234567890')
        
        # Invalid phone numbers
        assert not self.validation_service._is_valid_phone_number('123')  # Too short
        assert not self.validation_service._is_valid_phone_number('A1234567890')  # Contains letters
        assert not self.validation_service._is_valid_phone_number('123.456.7890')  # Invalid format
        assert not self.validation_service._is_valid_phone_number('123/456/7890')  # Invalid format
