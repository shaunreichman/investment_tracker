"""
Tests for ContactRepository.

This module tests the ContactRepository class to ensure it provides
clean data access abstraction without breaking existing functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

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
