"""
Tests for ContactRepository.

This module tests the ContactRepository class to ensure it provides
clean data access abstraction without breaking existing functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.investment_company.repositories.contact_repository import ContactRepository
from src.investment_company.models import Contact, InvestmentCompany


class TestContactRepository:
    """Test cases for ContactRepository."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repository = ContactRepository()
        self.mock_session = Mock(spec=Session)
        self.mock_query = Mock()
        self.mock_session.query.return_value = self.mock_query
    
    def test_get_by_id_success(self):
        """Test successful retrieval of contact by ID."""
        # Arrange
        contact_id = 1
        mock_contact = Mock(spec=Contact)
        mock_contact.id = contact_id
        mock_contact.name = "Test Contact"
        
        self.mock_query.filter.return_value.first.return_value = mock_contact
        
        # Act
        result = self.repository.get_by_id(contact_id, self.mock_session)
        
        # Assert
        assert result == mock_contact
        self.mock_session.query.assert_called_once_with(Contact)
        self.mock_query.filter.assert_called_once()
    
    def test_get_by_id_cache_hit(self):
        """Test that get_by_id returns cached result when available."""
        # Arrange
        contact_id = 1
        mock_contact = Mock(spec=Contact)
        mock_contact.id = contact_id
        mock_contact.name = "Test Contact"
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.first.return_value = mock_contact
        result1 = self.repository.get_by_id(contact_id, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_by_id(contact_id, self.mock_session)
        
        # Assert
        assert result1 == mock_contact
        assert result2 == mock_contact
        assert result1 is result2  # Same object from cache
    
    def test_get_by_company_success(self):
        """Test successful retrieval of contacts by company ID."""
        # Arrange
        company_id = 1
        mock_contacts = [
            Mock(spec=Contact, id=1, name="Contact 1"),
            Mock(spec=Contact, id=2, name="Contact 2")
        ]
        
        self.mock_query.filter.return_value.all.return_value = mock_contacts
        
        # Act
        result = self.repository.get_by_company(company_id, self.mock_session)
        
        # Assert
        assert result == mock_contacts
        self.mock_session.query.assert_called_once_with(Contact)
        self.mock_query.filter.assert_called_once()
    
    def test_get_by_company_cache_hit(self):
        """Test that get_by_company returns cached result when available."""
        # Arrange
        company_id = 1
        mock_contacts = [
            Mock(spec=Contact, id=1, name="Contact 1"),
            Mock(spec=Contact, id=2, name="Contact 2")
        ]
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.all.return_value = mock_contacts
        result1 = self.repository.get_by_company(company_id, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_by_company(company_id, self.mock_session)
        
        # Assert
        assert result1 == mock_contacts
        assert result2 == mock_contacts
        assert result1 is result2  # Same object from cache
    
    def test_get_by_email_success(self):
        """Test successful retrieval of contact by email."""
        # Arrange
        email = "test@example.com"
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 1
        mock_contact.direct_email = email
        
        self.mock_query.filter.return_value.first.return_value = mock_contact
        
        # Act
        result = self.repository.get_by_email(email, self.mock_session)
        
        # Assert
        assert result == mock_contact
        self.mock_session.query.assert_called_once_with(Contact)
        self.mock_query.filter.assert_called_once()
    
    def test_get_by_email_cache_hit(self):
        """Test that get_by_email returns cached result when available."""
        # Arrange
        email = "test@example.com"
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 1
        mock_contact.direct_email = email
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.first.return_value = mock_contact
        result1 = self.repository.get_by_email(email, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_by_email(email, self.mock_session)
        
        # Assert
        assert result1 == mock_contact
        assert result2 == mock_contact
        assert result1 is result2  # Same object from cache
    
    def test_get_by_email_not_found(self):
        """Test retrieval of non-existent contact by email."""
        # Arrange
        email = "nonexistent@example.com"
        self.mock_query.filter.return_value.first.return_value = None
        
        # Act
        result = self.repository.get_by_email(email, self.mock_session)
        
        # Assert
        assert result is None
    
    def test_get_by_name_success(self):
        """Test successful retrieval of contacts by name (partial match)."""
        # Arrange
        name = "John"
        mock_contacts = [
            Mock(spec=Contact, id=1, name="John Smith"),
            Mock(spec=Contact, id=2, name="John Doe")
        ]
        
        self.mock_query.filter.return_value.all.return_value = mock_contacts
        
        # Act
        result = self.repository.get_by_name(name, self.mock_session)
        
        # Assert
        assert result == mock_contacts
        self.mock_session.query.assert_called_once_with(Contact)
        self.mock_query.filter.assert_called_once()
    
    def test_get_by_name_cache_hit(self):
        """Test that get_by_name returns cached result when available."""
        # Arrange
        name = "Jane"
        mock_contacts = [Mock(spec=Contact, id=1, name="Jane Smith")]
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.all.return_value = mock_contacts
        result1 = self.repository.get_by_name(name, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_by_name(name, self.mock_session)
        
        # Assert
        assert result1 == mock_contacts
        assert result2 == mock_contacts
        assert result1 is result2  # Same object from cache
    
    def test_get_by_name_not_found(self):
        """Test retrieval of contacts by name when none found."""
        # Arrange
        name = "Nonexistent"
        self.mock_query.filter.return_value.all.return_value = []
        
        # Act
        result = self.repository.get_by_name(name, self.mock_session)
        
        # Assert
        assert result == []
    
    def test_create_success(self):
        """Test successful creation of contact."""
        # Arrange
        contact_data = {
            'name': 'New Contact',
            'title': 'Manager',
            'investment_company_id': 1,
            'direct_email': 'test@example.com'
        }
        
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 1
        mock_contact.name = contact_data['name']
        
        # Mock the Contact constructor
        with pytest.MonkeyPatch().context() as m:
            m.setattr(Contact, '__new__', lambda cls, **kwargs: mock_contact)
            m.setattr(Contact, '__init__', lambda self, **kwargs: None)
            
            # Act
            result = self.repository.create(contact_data, self.mock_session)
            
            # Assert
            assert result == mock_contact
            self.mock_session.add.assert_called_once_with(mock_contact)
            self.mock_session.flush.assert_called_once()
    
    def test_create_missing_name(self):
        """Test contact creation with missing name."""
        # Arrange
        contact_data = {
            'title': 'Manager',
            'investment_company_id': 1
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Contact name is required"):
            self.repository.create(contact_data, self.mock_session)
    
    def test_create_missing_company_id(self):
        """Test contact creation with missing company ID."""
        # Arrange
        contact_data = {
            'name': 'New Contact',
            'title': 'Manager'
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Investment company ID is required"):
            self.repository.create(contact_data, self.mock_session)
    
    def test_update_success(self):
        """Test successful update of contact."""
        # Arrange
        contact_id = 1
        update_data = {'title': 'Senior Manager'}
        
        mock_contact = Mock(spec=Contact)
        mock_contact.id = contact_id
        mock_contact.title = 'Manager'
        
        # Mock get_by_id to return existing contact
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: mock_contact if cid == contact_id else None)
            
            # Act
            result = self.repository.update(contact_id, update_data, self.mock_session)
            
            # Assert
            assert result == mock_contact
            assert mock_contact.title == 'Senior Manager'
            self.mock_session.flush.assert_called_once()
    
    def test_update_not_found(self):
        """Test update of non-existent contact."""
        # Arrange
        contact_id = 999
        update_data = {'title': 'Updated Title'}
        
        # Mock get_by_id to return None
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: None)
            
            # Act
            result = self.repository.update(contact_id, update_data, self.mock_session)
            
            # Assert
            assert result is None
    
    def test_delete_success(self):
        """Test successful deletion of contact."""
        # Arrange
        contact_id = 1
        mock_contact = Mock(spec=Contact)
        mock_contact.id = contact_id
        
        # Mock get_by_id to return existing contact
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: mock_contact if cid == contact_id else None)
            
            # Act
            result = self.repository.delete(contact_id, self.mock_session)
            
            # Assert
            assert result is True
            self.mock_session.delete.assert_called_once_with(mock_contact)
            self.mock_session.flush.assert_called_once()
    
    def test_delete_not_found(self):
        """Test deletion of non-existent contact."""
        # Arrange
        contact_id = 999
        
        # Mock get_by_id to return None
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: None)
            
            # Act
            result = self.repository.delete(contact_id, self.mock_session)
            
            # Assert
            assert result is False
    
    def test_search_contacts_success(self):
        """Test successful search of contacts."""
        # Arrange
        search_term = "Manager"
        company_id = 1
        mock_contacts = [
            Mock(spec=Contact, id=1, name="Manager 1"),
            Mock(spec=Contact, id=2, name="Manager 2")
        ]
        
        # Mock the query building
        self.mock_query.filter.return_value.filter.return_value.all.return_value = mock_contacts
        
        # Act
        result = self.repository.search_contacts(search_term, company_id, self.mock_session)
        
        # Assert
        assert result == mock_contacts
        self.mock_session.query.assert_called_once_with(Contact)
    
    def test_search_contacts_without_company_filter(self):
        """Test search of contacts without company filter."""
        # Arrange
        search_term = "Manager"
        mock_contacts = [
            Mock(spec=Contact, id=1, name="Manager 1"),
            Mock(spec=Contact, id=2, name="Manager 2")
        ]
        
        # Mock the query building
        self.mock_query.filter.return_value.all.return_value = mock_contacts
        
        # Act
        result = self.repository.search_contacts(search_term, None, self.mock_session)
        
        # Assert
        assert result == mock_contacts
        self.mock_session.query.assert_called_once_with(Contact)
    
    def test_search_contacts_cache_hit(self):
        """Test that search_contacts returns cached result when available."""
        # Arrange
        search_term = "Developer"
        company_id = 1
        mock_contacts = [Mock(spec=Contact, id=1, name="Developer 1")]
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.filter.return_value.all.return_value = mock_contacts
        result1 = self.repository.search_contacts(search_term, company_id, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.search_contacts(search_term, company_id, self.mock_session)
        
        # Assert
        assert result1 == result2
        assert result1 is result2  # Same object from cache
    
    def test_get_contacts_with_company_info_success(self):
        """Test successful retrieval of contacts with company information."""
        # Arrange
        company_id = 1
        mock_contact1 = Mock(spec=Contact)
        mock_contact1.id = 1
        mock_contact1.name = "Contact 1"
        mock_contact1.title = "Manager"
        
        mock_contact2 = Mock(spec=Contact)
        mock_contact2.id = 2
        mock_contact2.name = "Contact 2"
        mock_contact2.title = "Director"
        
        mock_contacts_data = [
            (mock_contact1, "Company A", "Private Equity"),
            (mock_contact2, "Company A", "Private Equity")
        ]
        
        # Mock the query with JOIN
        self.mock_query.join.return_value.filter.return_value.all.return_value = mock_contacts_data
        
        # Act
        result = self.repository.get_contacts_with_company_info(company_id, self.mock_session)
        
        # Assert
        assert len(result) == 2
        assert result[0]['name'] == "Contact 1"
        assert result[0]['company_name'] == "Company A"
        assert result[0]['company_type'] == "Private Equity"
        assert result[1]['name'] == "Contact 2"
        assert result[1]['company_name'] == "Company A"
        assert result[1]['company_type'] == "Private Equity"
    
    def test_get_contacts_with_company_info_cache_hit(self):
        """Test that get_contacts_with_company_info returns cached result when available."""
        # Arrange
        company_id = 1
        mock_contacts_data = [
            (Mock(spec=Contact, id=1, name="Contact 1"), "Company A", "Private Equity")
        ]
        
        # First call - should hit database and cache
        self.mock_query.join.return_value.filter.return_value.all.return_value = mock_contacts_data
        result1 = self.repository.get_contacts_with_company_info(company_id, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_contacts_with_company_info(company_id, self.mock_session)
        
        # Assert
        assert result1 == result2
        assert result1 is result2  # Same object from cache
    
    def test_get_contacts_by_title_success(self):
        """Test successful retrieval of contacts by title."""
        # Arrange
        title = "Manager"
        company_id = 1
        mock_contacts = [
            Mock(spec=Contact, id=1, name="Contact 1", title=title),
            Mock(spec=Contact, id=2, name="Contact 2", title=title)
        ]
        
        # Mock the query building
        self.mock_query.filter.return_value.filter.return_value.all.return_value = mock_contacts
        
        # Act
        result = self.repository.get_contacts_by_title(title, company_id, self.mock_session)
        
        # Assert
        assert result == mock_contacts
        self.mock_session.query.assert_called_once_with(Contact)
        self.mock_query.filter.assert_called()
    
    def test_get_contacts_by_title_without_company_filter(self):
        """Test retrieval of contacts by title without company filter."""
        # Arrange
        title = "Director"
        mock_contacts = [
            Mock(spec=Contact, id=1, name="Contact 1", title=title),
            Mock(spec=Contact, id=2, name="Contact 2", title=title)
        ]
        
        # Mock the query building
        self.mock_query.filter.return_value.all.return_value = mock_contacts
        
        # Act
        result = self.repository.get_contacts_by_title(title, None, self.mock_session)
        
        # Assert
        assert result == mock_contacts
        self.mock_session.query.assert_called_once_with(Contact)
        self.mock_query.filter.assert_called_once()
    
    def test_get_contacts_by_title_cache_hit(self):
        """Test that get_contacts_by_title returns cached result when available."""
        # Arrange
        title = "Analyst"
        company_id = 1
        mock_contacts = [Mock(spec=Contact, id=1, name="Contact 1", title=title)]
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.filter.return_value.all.return_value = mock_contacts
        result1 = self.repository.get_contacts_by_title(title, company_id, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_contacts_by_title(title, company_id, self.mock_session)
        
        # Assert
        assert result1 == result2
        assert result1 is result2  # Same object from cache
    
    def test_bulk_create_contacts_success(self):
        """Test successful bulk creation of contacts."""
        # Arrange
        contacts_data = [
            {
                'name': 'Contact 1',
                'title': 'Manager',
                'investment_company_id': 1,
                'direct_email': 'contact1@example.com'
            },
            {
                'name': 'Contact 2',
                'title': 'Director',
                'investment_company_id': 1,
                'direct_email': 'contact2@example.com'
            }
        ]
        
        mock_contact1 = Mock(spec=Contact)
        mock_contact1.id = 1
        mock_contact1.name = 'Contact 1'
        
        mock_contact2 = Mock(spec=Contact)
        mock_contact2.id = 2
        mock_contact2.name = 'Contact 2'
        
        # Mock the Contact constructor
        with pytest.MonkeyPatch().context() as m:
            m.setattr(Contact, '__new__', lambda cls, **kwargs: mock_contact1 if kwargs.get('name') == 'Contact 1' else mock_contact2)
            m.setattr(Contact, '__init__', lambda self, **kwargs: None)
            
            # Act
            result = self.repository.bulk_create_contacts(contacts_data, self.mock_session)
            
            # Assert
            assert len(result) == 2
            assert result[0].name == 'Contact 1'
            assert result[1].name == 'Contact 2'
            assert self.mock_session.add.call_count == 2
            self.mock_session.flush.assert_called_once()
    
    def test_bulk_create_contacts_missing_name(self):
        """Test bulk creation with missing name."""
        # Arrange
        contacts_data = [
            {
                'title': 'Manager',
                'investment_company_id': 1
            }
        ]
        
        # Act & Assert
        with pytest.raises(ValueError, match="Contact name is required"):
            self.repository.bulk_create_contacts(contacts_data, self.mock_session)
    
    def test_bulk_create_contacts_missing_company_id(self):
        """Test bulk creation with missing company ID."""
        # Arrange
        contacts_data = [
            {
                'name': 'Contact 1',
                'title': 'Manager'
            }
        ]
        
        # Act & Assert
        with pytest.raises(ValueError, match="Investment company ID is required"):
            self.repository.bulk_create_contacts(contacts_data, self.mock_session)
    
    def test_cache_cleared_after_create(self):
        """Test that cache is cleared after creating a contact."""
        # Arrange
        contact_data = {
            'name': 'New Contact',
            'investment_company_id': 1
        }
        mock_contact = Mock(spec=Contact)
        
        # Mock the Contact constructor
        with pytest.MonkeyPatch().context() as m:
            m.setattr(Contact, '__new__', lambda cls, **kwargs: mock_contact)
            m.setattr(Contact, '__init__', lambda self, **kwargs: None)
            
            # Populate cache first
            self.repository._cache['contacts:company:1'] = ['cached_contacts']
            self.repository._cache['contact:1'] = 'cached_contact'
            
            # Act
            self.repository.create(contact_data, self.mock_session)
            
            # Assert
            assert len(self.repository._cache) == 0  # Cache should be cleared
    
    def test_cache_cleared_after_update(self):
        """Test that cache is cleared after updating a contact."""
        # Arrange
        contact_id = 1
        update_data = {'title': 'Updated Title'}
        mock_contact = Mock(spec=Contact)
        
        # Mock get_by_id to return existing contact
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: mock_contact if cid == contact_id else None)
            
            # Populate cache first
            self.repository._cache['contacts:company:1'] = ['cached_contacts']
            self.repository._cache[f'contact:{contact_id}'] = 'cached_contact'
            
            # Act
            self.repository.update(contact_id, update_data, self.mock_session)
            
            # Assert
            assert len(self.repository._cache) == 0  # Cache should be cleared
    
    def test_cache_cleared_after_delete(self):
        """Test that cache is cleared after deleting a contact."""
        # Arrange
        contact_id = 1
        mock_contact = Mock(spec=Contact)
        mock_contact.investment_company_id = 1
        
        # Mock get_by_id to return existing contact
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: mock_contact if cid == contact_id else None)
            
            # Populate cache first
            self.repository._cache['contacts:company:1'] = ['cached_contacts']
            self.repository._cache[f'contact:{contact_id}'] = 'cached_contact'
            
            # Act
            self.repository.delete(contact_id, self.mock_session)
            
            # Assert
            assert len(self.repository._cache) == 0  # Cache should be cleared
    
    def test_cache_cleared_after_bulk_create(self):
        """Test that cache is cleared after bulk creating contacts."""
        # Arrange
        contacts_data = [
            {
                'name': 'Contact 1',
                'investment_company_id': 1
            }
        ]
        
        mock_contact = Mock(spec=Contact)
        
        # Mock the Contact constructor
        with pytest.MonkeyPatch().context() as m:
            m.setattr(Contact, '__new__', lambda cls, **kwargs: mock_contact)
            m.setattr(Contact, '__init__', lambda self, **kwargs: None)
            
            # Populate cache first
            self.repository._cache['contacts:company:1'] = ['cached_contacts']
            
            # Act
            self.repository.bulk_create_contacts(contacts_data, self.mock_session)
            
            # Assert
            assert len(self.repository._cache) == 0  # Cache should be cleared
    
    def test_clear_cache_method(self):
        """Test the _clear_cache method."""
        # Arrange
        self.repository._cache['key1'] = 'value1'
        self.repository._cache['key2'] = 'value2'
        
        # Act
        self.repository._clear_cache()
        
        # Assert
        assert len(self.repository._cache) == 0
    
    def test_clear_contact_cache_method(self):
        """Test the _clear_contact_cache method."""
        # Arrange
        contact_id = 1
        self.repository._cache['contact:1'] = 'contact1'
        self.repository._cache['contacts:all'] = 'all_contacts'
        self.repository._cache['other_key'] = 'other_value'
        
        # Act
        self.repository._clear_contact_cache(contact_id)
        
        # Assert
        assert 'contact:1' not in self.repository._cache
        assert 'contacts:all' not in self.repository._cache
        assert 'other_key' in self.repository._cache  # Should remain
    
    def test_clear_company_contacts_cache_method(self):
        """Test the _clear_company_contacts_cache method."""
        # Arrange
        company_id = 1
        self.repository._cache['contacts:company:1'] = 'company_contacts'
        self.repository._cache['contacts:with_company:1'] = 'contacts_with_company'
        self.repository._cache['other_key'] = 'other_value'
        
        # Act
        self.repository._clear_company_contacts_cache(company_id)
        
        # Assert
        assert 'contacts:company:1' not in self.repository._cache
        assert 'contacts:with_company:1' not in self.repository._cache
        assert 'other_key' in self.repository._cache  # Should remain
    
    def test_search_contacts_with_none_session(self):
        """Test search_contacts with None session raises error."""
        # Arrange
        search_term = "Manager"
        company_id = 1
        
        # Act & Assert
        with pytest.raises(AttributeError):
            self.repository.search_contacts(search_term, company_id, None)
    
    def test_get_contacts_by_title_with_none_session(self):
        """Test get_contacts_by_title with None session raises error."""
        # Arrange
        title = "Manager"
        company_id = 1
        
        # Act & Assert
        with pytest.raises(AttributeError):
            self.repository.get_contacts_by_title(title, company_id, None)
