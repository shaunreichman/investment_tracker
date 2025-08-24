"""
Tests for CompanyRepository.

This module tests the CompanyRepository class to ensure it provides
clean data access abstraction without breaking existing functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.investment_company.repositories.company_repository import CompanyRepository
from src.investment_company.models import InvestmentCompany
from src.investment_company.enums import CompanyType, CompanyStatus
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
    
    def test_get_by_id_cache_hit(self):
        """Test that get_by_id returns cached result when available."""
        # Arrange
        company_id = 1
        mock_company = Mock(spec=InvestmentCompany)
        mock_company.id = company_id
        mock_company.name = "Test Company"
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.first.return_value = mock_company
        result1 = self.repository.get_by_id(company_id, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_by_id(company_id, self.mock_session)
        
        # Assert
        assert result1 == mock_company
        assert result2 == mock_company
        assert result1 is result2  # Same object from cache
    
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
    
    def test_get_by_name_cache_hit(self):
        """Test that get_by_name returns cached result when available."""
        # Arrange
        company_name = "Test Company"
        mock_company = Mock(spec=InvestmentCompany)
        mock_company.name = company_name
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.first.return_value = mock_company
        result1 = self.repository.get_by_name(company_name, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_by_name(company_name, self.mock_session)
        
        # Assert
        assert result1 == mock_company
        assert result2 == mock_company
        assert result1 is result2  # Same object from cache
    
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
    
    def test_get_all_cache_hit(self):
        """Test that get_all returns cached result when available."""
        # Arrange
        mock_companies = [
            Mock(spec=InvestmentCompany, id=1, name="Company 1"),
            Mock(spec=InvestmentCompany, id=2, name="Company 2")
        ]
        
        # First call - should hit database and cache
        self.mock_query.all.return_value = mock_companies
        result1 = self.repository.get_all(self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_all(self.mock_session)
        
        # Assert
        assert result1 == mock_companies
        assert result2 == mock_companies
        assert result1 is result2  # Same object from cache
    
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
    
    def test_get_companies_with_fund_counts_cache_hit(self):
        """Test that get_companies_with_fund_counts returns cached result when available."""
        # Arrange
        mock_companies_data = [
            (Mock(spec=InvestmentCompany, id=1, name="Company 1"), 2, 1000000.0, 500000.0)
        ]
        
        # First call - should hit database and cache
        self.mock_query.outerjoin.return_value.group_by.return_value.all.return_value = mock_companies_data
        result1 = self.repository.get_companies_with_fund_counts(self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_companies_with_fund_counts(self.mock_session)
        
        # Assert
        assert result1 == result2
        assert result1 is result2  # Same object from cache
    
    def test_get_companies_with_summary_success(self):
        """Test successful retrieval of companies with summary data."""
        # Arrange
        mock_companies = [
            Mock(spec=InvestmentCompany, id=1, name="Company 1", description="Desc 1"),
            Mock(spec=InvestmentCompany, id=2, name="Company 2", description="Desc 2")
        ]
        
        # Mock the funds relationship for each company
        mock_companies[0].funds = [Mock(commitment_amount=1000000.0, current_equity_balance=500000.0)]
        mock_companies[1].funds = [Mock(commitment_amount=500000.0, current_equity_balance=250000.0)]
        
        # Mock the query with load_only
        self.mock_query.options.return_value.all.return_value = mock_companies
        
        # Act
        result = self.repository.get_companies_with_summary(self.mock_session)
        
        # Assert
        assert len(result) == 2
        assert result[0]['fund_count'] == 1
        assert result[0]['total_commitments'] == 1000000.0
        assert result[1]['fund_count'] == 1
        assert result[1]['total_commitments'] == 500000.0
    
    def test_get_companies_with_summary_cache_hit(self):
        """Test that get_companies_with_summary returns cached result when available."""
        # Arrange
        mock_companies = [Mock(spec=InvestmentCompany, id=1, name="Company 1")]
        mock_companies[0].funds = []
        
        # First call - should hit database and cache
        self.mock_query.options.return_value.all.return_value = mock_companies
        result1 = self.repository.get_companies_with_summary(self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_companies_with_summary(self.mock_session)
        
        # Assert
        assert result1 == result2
        assert result1 is result2  # Same object from cache
    
    def test_get_companies_by_type_success(self):
        """Test successful retrieval of companies by type."""
        # Arrange
        company_type = CompanyType.PRIVATE_EQUITY
        mock_companies = [
            Mock(spec=InvestmentCompany, id=1, name="Company 1", company_type=company_type),
            Mock(spec=InvestmentCompany, id=2, name="Company 2", company_type=company_type)
        ]
        
        self.mock_query.filter.return_value.all.return_value = mock_companies
        
        # Act
        result = self.repository.get_companies_by_type(company_type.value, self.mock_session)
        
        # Assert
        assert result == mock_companies
        self.mock_session.query.assert_called_once_with(InvestmentCompany)
        self.mock_query.filter.assert_called_once()
    
    def test_get_companies_by_type_cache_hit(self):
        """Test that get_companies_by_type returns cached result when available."""
        # Arrange
        company_type = CompanyType.VENTURE_CAPITAL
        mock_companies = [Mock(spec=InvestmentCompany, id=1, name="Company 1")]
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.all.return_value = mock_companies
        result1 = self.repository.get_companies_by_type(company_type.value, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_companies_by_type(company_type.value, self.mock_session)
        
        # Assert
        assert result1 == result2
        assert result1 is result2  # Same object from cache
    
    def test_get_companies_by_status_success(self):
        """Test successful retrieval of companies by status."""
        # Arrange
        status = CompanyStatus.ACTIVE
        mock_companies = [
            Mock(spec=InvestmentCompany, id=1, name="Company 1", status=status),
            Mock(spec=InvestmentCompany, id=2, name="Company 2", status=status)
        ]
        
        self.mock_query.filter.return_value.all.return_value = mock_companies
        
        # Act
        result = self.repository.get_companies_by_status(status.value, self.mock_session)
        
        # Assert
        assert result == mock_companies
        self.mock_session.query.assert_called_once_with(InvestmentCompany)
        self.mock_query.filter.assert_called_once()
    
    def test_get_companies_by_status_cache_hit(self):
        """Test that get_companies_by_status returns cached result when available."""
        # Arrange
        status = CompanyStatus.INACTIVE
        mock_companies = [Mock(spec=InvestmentCompany, id=1, name="Company 1")]
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.all.return_value = mock_companies
        result1 = self.repository.get_companies_by_status(status.value, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_companies_by_status(status.value, self.mock_session)
        
        # Assert
        assert result1 == result2
        assert result1 is result2  # Same object from cache
    
    def test_search_companies_success(self):
        """Test successful search of companies."""
        # Arrange
        search_term = "Private Equity"
        mock_companies = [
            Mock(spec=InvestmentCompany, id=1, name="Company 1", company_type=CompanyType.PRIVATE_EQUITY),
            Mock(spec=InvestmentCompany, id=2, name="Company 2", description="Private equity firm")
        ]
        
        self.mock_query.filter.return_value.all.return_value = mock_companies
        
        # Act
        result = self.repository.search_companies(search_term, self.mock_session)
        
        # Assert
        assert result == mock_companies
        self.mock_session.query.assert_called_once_with(InvestmentCompany)
        self.mock_query.filter.assert_called_once()
    
    def test_search_companies_cache_hit(self):
        """Test that search_companies returns cached result when available."""
        # Arrange
        search_term = "Venture"
        mock_companies = [Mock(spec=InvestmentCompany, id=1, name="Company 1")]
        
        # First call - should hit database and cache
        self.mock_query.filter.return_value.all.return_value = mock_companies
        result1 = self.repository.search_companies(search_term, self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.search_companies(search_term, self.mock_session)
        
        # Assert
        assert result1 == result2
        assert result1 is result2  # Same object from cache
    
    def test_get_companies_with_active_funds_success(self):
        """Test successful retrieval of companies with active funds."""
        # Arrange
        mock_companies = [
            Mock(spec=InvestmentCompany, id=1, name="Company 1"),
            Mock(spec=InvestmentCompany, id=2, name="Company 2")
        ]
        
        self.mock_query.join.return_value.filter.return_value.distinct.return_value.all.return_value = mock_companies
        
        # Act
        result = self.repository.get_companies_with_active_funds(self.mock_session)
        
        # Assert
        assert result == mock_companies
        self.mock_session.query.assert_called_once_with(InvestmentCompany)
        self.mock_query.join.assert_called_once()
        self.mock_query.join.return_value.filter.assert_called_once()
        self.mock_query.join.return_value.filter.return_value.distinct.assert_called_once()
    
    def test_get_companies_with_active_funds_cache_hit(self):
        """Test that get_companies_with_active_funds returns cached result when available."""
        # Arrange
        mock_companies = [Mock(spec=InvestmentCompany, id=1, name="Company 1")]
        
        # First call - should hit database and cache
        self.mock_query.join.return_value.filter.return_value.distinct.return_value.all.return_value = mock_companies
        result1 = self.repository.get_companies_with_active_funds(self.mock_session)
        
        # Second call - should hit cache, not database
        result2 = self.repository.get_companies_with_active_funds(self.mock_session)
        
        # Assert
        assert result1 == result2
        assert result1 is result2  # Same object from cache
    
    def test_cache_cleared_after_create(self):
        """Test that cache is cleared after creating a company."""
        # Arrange
        company_data = {'name': 'New Company'}
        mock_company = Mock(spec=InvestmentCompany)
        
        # Mock get_by_name to return None
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_name', lambda name, session: None)
            m.setattr(InvestmentCompany, '__new__', lambda cls, **kwargs: mock_company)
            m.setattr(InvestmentCompany, '__init__', lambda self, **kwargs: None)
            
            # Populate cache first
            self.repository._cache['companies:all'] = ['cached_data']
            self.repository._cache['company:1'] = 'cached_company'
            
            # Act
            self.repository.create(company_data, self.mock_session)
            
            # Assert
            assert len(self.repository._cache) == 0  # Cache should be cleared
    
    def test_cache_cleared_after_update(self):
        """Test that cache is cleared after updating a company."""
        # Arrange
        company_id = 1
        update_data = {'description': 'Updated'}
        mock_company = Mock(spec=InvestmentCompany)
        
        # Mock get_by_id to return existing company
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: mock_company if cid == company_id else None)
            
            # Populate cache first
            self.repository._cache['companies:all'] = ['cached_data']
            self.repository._cache[f'company:{company_id}'] = 'cached_company'
            
            # Act
            self.repository.update(company_id, update_data, self.mock_session)
            
            # Assert
            assert len(self.repository._cache) == 0  # Cache should be cleared
    
    def test_cache_cleared_after_delete(self):
        """Test that cache is cleared after deleting a company."""
        # Arrange
        company_id = 1
        mock_company = Mock(spec=InvestmentCompany)
        
        # Mock get_by_id to return existing company
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.repository, 'get_by_id', lambda cid, session: mock_company if cid == company_id else None)
            
            # Populate cache first
            self.repository._cache['companies:all'] = ['cached_data']
            self.repository._cache[f'company:{company_id}'] = 'cached_company'
            
            # Act
            self.repository.delete(company_id, self.mock_session)
            
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
    
    def test_clear_company_cache_method(self):
        """Test the _clear_company_cache method."""
        # Arrange
        company_id = 1
        self.repository._cache['company:1'] = 'company1'
        self.repository._cache['companies:all'] = 'all_companies'
        self.repository._cache['companies:with_fund_counts'] = 'fund_counts'
        self.repository._cache['companies:with_active_funds'] = 'active_funds'
        self.repository._cache['other_key'] = 'other_value'
        
        # Act
        self.repository._clear_company_cache(company_id)
        
        # Assert
        assert 'company:1' not in self.repository._cache
        assert 'companies:all' not in self.repository._cache
        assert 'companies:with_fund_counts' not in self.repository._cache
        assert 'companies:with_active_funds' not in self.repository._cache
        assert 'other_key' in self.repository._cache  # Should remain
