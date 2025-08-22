"""
Tests for CompanyRepository.

This module tests the CompanyRepository class to ensure it provides
clean data access abstraction without breaking existing functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from src.investment_company.repositories.company_repository import CompanyRepository
from src.investment_company.models import InvestmentCompany
from src.fund.models import Fund
from src.fund.enums import FundStatus


class TestCompanyRepository:
    """Test cases for CompanyRepository."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repository = CompanyRepository()
        self.mock_session = Mock(spec=Session)
        self.mock_query = Mock()
        self.mock_session.query.return_value = self.mock_query
    
    def test_get_by_id_success(self):
        """Test successful retrieval of company by ID."""
        # Arrange
        company_id = 1
        mock_company = Mock(spec=InvestmentCompany)
        mock_company.id = company_id
        mock_company.name = "Test Company"
        
        self.mock_query.filter.return_value.first.return_value = mock_company
        
        # Act
        result = self.repository.get_by_id(company_id, self.mock_session)
        
        # Assert
        assert result == mock_company
        self.mock_session.query.assert_called_once_with(InvestmentCompany)
        self.mock_query.filter.assert_called_once()
    
    def test_get_by_id_not_found(self):
        """Test retrieval of non-existent company by ID."""
        # Arrange
        company_id = 999
        self.mock_query.filter.return_value.first.return_value = None
        
        # Act
        result = self.repository.get_by_id(company_id, self.mock_session)
        
        # Assert
        assert result is None
    
    def test_get_by_name_success(self):
        """Test successful retrieval of company by name."""
        # Arrange
        company_name = "Test Company"
        mock_company = Mock(spec=InvestmentCompany)
        mock_company.name = company_name
        
        self.mock_query.filter.return_value.first.return_value = mock_company
        
        # Act
        result = self.repository.get_by_name(company_name, self.mock_session)
        
        # Assert
        assert result == mock_company
        self.mock_session.query.assert_called_once_with(InvestmentCompany)
        self.mock_query.filter.assert_called_once()
    
    def test_get_all_success(self):
        """Test successful retrieval of all companies."""
        # Arrange
        mock_companies = [
            Mock(spec=InvestmentCompany, id=1, name="Company 1"),
            Mock(spec=InvestmentCompany, id=2, name="Company 2")
        ]
        
        self.mock_query.all.return_value = mock_companies
        
        # Act
        result = self.repository.get_all(self.mock_session)
        
        # Assert
        assert result == mock_companies
        self.mock_session.query.assert_called_once_with(InvestmentCompany)
        self.mock_query.all.assert_called_once()
    
    def test_create_success(self):
        """Test successful creation of company."""
        # Arrange
        company_data = {
            'name': 'New Company',
            'description': 'Test Description',
            'company_type': 'Private Equity'
        }
        
        mock_company = Mock(spec=InvestmentCompany)
        mock_company.id = 1
        mock_company.name = company_data['name']
        
        # Mock get_by_name to return None (no existing company)
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_name', lambda name, session: None)
            m.setattr(InvestmentCompany, '__new__', lambda cls, **kwargs: mock_company)
            m.setattr(InvestmentCompany, '__init__', lambda self, **kwargs: None)
            
            # Act
            result = self.repository.create(company_data, self.mock_session)
            
            # Assert
            assert result == mock_company
            self.mock_session.add.assert_called_once_with(mock_company)
            self.mock_session.flush.assert_called_once()
    
    def test_create_missing_name(self):
        """Test company creation with missing name."""
        # Arrange
        company_data = {
            'description': 'Test Description',
            'company_type': 'Private Equity'
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Company name is required"):
            self.repository.create(company_data, self.mock_session)
    
    def test_create_duplicate_name(self):
        """Test company creation with duplicate name."""
        # Arrange
        company_data = {'name': 'Existing Company'}
        existing_company = Mock(spec=InvestmentCompany)
        
        # Mock get_by_name to return existing company
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_name', lambda name, session: existing_company if name == 'Existing Company' else None)
            
            # Act & Assert
            with pytest.raises(ValueError, match="Investment company with name 'Existing Company' already exists"):
                self.repository.create(company_data, self.mock_session)
    
    def test_update_success(self):
        """Test successful update of company."""
        # Arrange
        company_id = 1
        update_data = {'description': 'Updated Description'}
        
        mock_company = Mock(spec=InvestmentCompany)
        mock_company.id = company_id
        mock_company.description = 'Old Description'
        
        # Mock get_by_id to return existing company
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: mock_company if cid == company_id else None)
            
            # Act
            result = self.repository.update(company_id, update_data, self.mock_session)
            
            # Assert
            assert result == mock_company
            assert mock_company.description == 'Updated Description'
            self.mock_session.flush.assert_called_once()
    
    def test_update_not_found(self):
        """Test update of non-existent company."""
        # Arrange
        company_id = 999
        update_data = {'description': 'Updated Description'}
        
        # Mock get_by_id to return None
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: None)
            
            # Act
            result = self.repository.update(company_id, update_data, self.mock_session)
            
            # Assert
            assert result is None
    
    def test_delete_success(self):
        """Test successful deletion of company."""
        # Arrange
        company_id = 1
        mock_company = Mock(spec=InvestmentCompany)
        mock_company.id = company_id
        
        # Mock get_by_id to return existing company
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: mock_company if cid == company_id else None)
            
            # Act
            result = self.repository.delete(company_id, self.mock_session)
            
            # Assert
            assert result is True
            self.mock_session.delete.assert_called_once_with(mock_company)
            self.mock_session.flush.assert_called_once()
    
    def test_delete_not_found(self):
        """Test deletion of non-existent company."""
        # Arrange
        company_id = 999
        
        # Mock get_by_id to return None
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: None)
            
            # Act
            result = self.repository.delete(company_id, self.mock_session)
            
            # Assert
            assert result is False
    
    def test_get_companies_with_fund_counts_success(self):
        """Test successful retrieval of companies with fund counts."""
        # Arrange
        mock_companies_data = [
            (Mock(spec=InvestmentCompany, id=1, name="Company 1"), 2, 1000000.0, 500000.0),
            (Mock(spec=InvestmentCompany, id=2, name="Company 2"), 1, 500000.0, 250000.0)
        ]
        
        self.mock_query.outerjoin.return_value.group_by.return_value.all.return_value = mock_companies_data
        
        # Act
        result = self.repository.get_companies_with_fund_counts(self.mock_session)
        
        # Assert
        assert len(result) == 2
        assert result[0]['fund_count'] == 2
        assert result[0]['total_commitments'] == 1000000.0
        assert result[1]['fund_count'] == 1
        assert result[1]['total_commitments'] == 500000.0
