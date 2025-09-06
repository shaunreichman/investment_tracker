"""
Enterprise-grade unit tests for FundCoordinationService.

This module demonstrates professional testing patterns including:
- Proper test organization and structure
- Test data builders for consistent test data
- Clean test isolation with proper setup/teardown
- Comprehensive test coverage with clear arrange/act/assert
- Logical grouping of related test scenarios
- Mocking of external dependencies
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone
from typing import Dict, Any

from src.investment_company.services.fund_coordination_service import FundCoordinationService
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.enums import CompanyType, CompanyStatus
from src.fund.models import Fund
from src.fund.enums import FundStatus
from src.entity.models import Entity


class CoordinationTestDataBuilder:
    """Test data builder for creating consistent coordination test objects."""
    
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
            'contacts': [],
            'max_funds': None
        }
        defaults.update(kwargs)
        
        company = Mock(spec=InvestmentCompany)
        for key, value in defaults.items():
            setattr(company, key, value)
        return company
    
    @staticmethod
    def create_fund(**kwargs) -> Mock:
        """Create a mock Fund with sensible defaults."""
        defaults = {
            'id': 1,
            'name': 'Test Fund',
            'status': FundStatus.ACTIVE,
            'investment_company_id': 1,
            'commitment_amount': 1000000.0,
            'current_equity_balance': 950000.0,
            'fund_events': []
        }
        defaults.update(kwargs)
        
        fund = Mock(spec=Fund)
        for key, value in defaults.items():
            setattr(fund, key, value)
        return fund
    
    @staticmethod
    def create_entity(**kwargs) -> Mock:
        """Create a mock Entity with sensible defaults."""
        defaults = {
            'id': 1,
            'name': 'Test Entity',
            'abn': '12345678901',
            'status': Mock(value='ACTIVE')
        }
        defaults.update(kwargs)
        
        entity = Mock(spec=Entity)
        for key, value in defaults.items():
            setattr(entity, key, value)
        return entity
    
    @staticmethod
    def create_session() -> Mock:
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @staticmethod
    def create_fund_data(**kwargs) -> Dict[str, Any]:
        """Create fund creation data with sensible defaults."""
        defaults = {
            'name': 'Test Fund',
            'entity_id': 1,
            'investment_company_id': 1,
            'fund_type': 'Private Equity',
            'tracking_type': 'COST_BASED',
            'currency': 'AUD',
            'description': 'Test fund description',
            'commitment_amount': 1000000.0,
            'expected_irr': 15.0,
            'expected_duration_months': 60
        }
        defaults.update(kwargs)
        return defaults


class TestFundCoordinationService:
    """Enterprise-grade test suite for FundCoordinationService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the fund service
        self.mock_fund_service = Mock()
        self.coordination_service = FundCoordinationService(fund_service=self.mock_fund_service)
        self.mock_session = CoordinationTestDataBuilder.create_session()
    
    def teardown_method(self):
        """Clean up after each test method."""
        pass
    
    # ============================================================================
    # FUND CREATION COORDINATION TESTS
    # ============================================================================
    
    @patch('src.fund.repositories.fund_repository.FundRepository')
    @patch('src.investment_company.services.company_portfolio_service.CompanyPortfolioService')
    @patch('src.investment_company.events.domain.portfolio_updated_event.PortfolioUpdatedEvent')
    @patch('src.investment_company.events.registry.CompanyEventHandlerRegistry')
    def test_coordinate_fund_creation_success(self, mock_registry, mock_event, 
                                            mock_portfolio_service, mock_fund_repo):
        """Test successful fund creation coordination."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Mock fund service response using injected mock
        self.mock_fund_service.create_fund.return_value = {'id': 1}
        
        # Mock fund repository
        mock_fund_repo_instance = Mock()
        mock_fund = CoordinationTestDataBuilder.create_fund()
        mock_fund_repo_instance.get_by_id.return_value = mock_fund
        mock_fund_repo.return_value = mock_fund_repo_instance
        
        # Mock portfolio service
        mock_portfolio_service_instance = Mock()
        mock_portfolio_service.return_value = mock_portfolio_service_instance
        
        # Mock event and registry
        mock_event_instance = Mock()
        mock_event.return_value = mock_event_instance
        mock_registry_instance = Mock()
        mock_registry.return_value = mock_registry_instance
        
        # Act
        result = self.coordination_service.coordinate_fund_creation(
            company, entity, fund_data, self.mock_session
        )
        
        # Assert
        assert result == mock_fund
        self.mock_fund_service.create_fund.assert_called_once_with(fund_data, self.mock_session)
        mock_fund_repo_instance.get_by_id.assert_called_once_with(1, self.mock_session)
        mock_portfolio_service_instance._trigger_portfolio_summary_recalculation.assert_called_once_with(
            company, self.mock_session
        )
        mock_registry_instance.handle_event.assert_called_once()
    
    def test_coordinate_fund_creation_missing_company(self):
        """Test fund creation coordination with missing company."""
        # Arrange
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Company is required for fund creation coordination"):
            self.coordination_service.coordinate_fund_creation(
                None, entity, fund_data, self.mock_session
            )
    
    def test_coordinate_fund_creation_missing_entity(self):
        """Test fund creation coordination with missing entity."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Entity is required for fund creation coordination"):
            self.coordination_service.coordinate_fund_creation(
                company, None, fund_data, self.mock_session
            )
    
    def test_coordinate_fund_creation_missing_fund_name(self):
        """Test fund creation coordination with missing fund name."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        fund_data['name'] = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Fund name is required"):
            self.coordination_service.coordinate_fund_creation(
                company, entity, fund_data, self.mock_session
            )
    
    def test_coordinate_fund_creation_missing_fund_type(self):
        """Test fund creation coordination with missing fund type."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        fund_data['fund_type'] = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Fund type is required"):
            self.coordination_service.coordinate_fund_creation(
                company, entity, fund_data, self.mock_session
            )
    
    def test_coordinate_fund_creation_missing_tracking_type(self):
        """Test fund creation coordination with missing tracking type."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        fund_data['tracking_type'] = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Tracking type is required"):
            self.coordination_service.coordinate_fund_creation(
                company, entity, fund_data, self.mock_session
            )
    
    # ============================================================================
    # FUND VALIDATION COORDINATION TESTS
    # ============================================================================
    
    def test_validate_fund_creation_business_rules_success(self):
        """Test successful business rule validation for fund creation."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert isinstance(result, dict)
        assert 'is_valid' in result
        assert 'errors' in result
        assert 'warnings' in result
    
    def test_validate_fund_creation_business_rules_company_max_funds_exceeded(self):
        """Test business rule validation when company exceeds max funds limit."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company(max_funds=2)
        company.funds = [Mock(), Mock(), Mock()]  # 3 funds, exceeding limit of 2
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is False
        assert len(result['errors']) == 1
        assert "Company has reached maximum fund limit of 2" in result['errors'][0]
        assert len(result['warnings']) == 0
    
    def test_validate_fund_creation_business_rules_company_inactive_warning(self):
        """Test business rule validation with inactive company warning."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        company.status = Mock(value='INACTIVE')
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 1
        assert "Company is inactive - fund creation may be restricted" in result['warnings'][0]
    
    def test_validate_fund_creation_business_rules_entity_inactive_warning(self):
        """Test business rule validation with inactive entity warning."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        entity.status = Mock(value='INACTIVE')
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 1
        assert "Entity is inactive - fund creation may be restricted" in result['warnings'][0]
    
    def test_validate_fund_creation_business_rules_entity_invalid_abn_warning(self):
        """Test business rule validation with invalid entity ABN warning."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        entity.abn = '123'  # Invalid ABN (too short)
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 1
        assert "Entity ABN appears invalid - please verify" in result['warnings'][0]
    
    def test_validate_fund_creation_business_rules_multiple_warnings(self):
        """Test business rule validation with multiple warnings."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        company.status = Mock(value='INACTIVE')
        entity = CoordinationTestDataBuilder.create_entity()
        entity.status = Mock(value='INACTIVE')
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 2
        assert any("Company is inactive" in warning for warning in result['warnings'])
        assert any("Entity is inactive" in warning for warning in result['warnings'])
    
    def test_validate_fund_creation_business_rules_company_no_max_funds(self):
        """Test business rule validation when company has no max funds limit."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company(max_funds=None)
        company.funds = [Mock(), Mock(), Mock()]  # 3 funds, but no limit
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 0
    
    def test_validate_fund_creation_business_rules_entity_no_status(self):
        """Test business rule validation when entity has no status."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        entity.status = None
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 0
    
    def test_validate_fund_creation_business_rules_entity_no_abn(self):
        """Test business rule validation when entity has no ABN."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        entity.abn = None
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 0
    
    # ============================================================================
    # PRIVATE METHOD TESTS
    # ============================================================================
    
    def test_validate_fund_creation_prerequisites_success(self):
        """Test successful validation of fund creation prerequisites."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act & Assert - Should not raise any exceptions
        self.coordination_service._validate_fund_creation_prerequisites(
            company, entity, fund_data
        )
    
    def test_validate_fund_creation_prerequisites_missing_company(self):
        """Test validation of fund creation prerequisites with missing company."""
        # Arrange
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Company is required for fund creation coordination"):
            self.coordination_service._validate_fund_creation_prerequisites(
                None, entity, fund_data
            )
    
    def test_validate_fund_creation_prerequisites_missing_entity(self):
        """Test validation of fund creation prerequisites with missing entity."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Entity is required for fund creation coordination"):
            self.coordination_service._validate_fund_creation_prerequisites(
                company, None, fund_data
            )
    
    def test_validate_fund_creation_prerequisites_missing_fund_name(self):
        """Test validation of fund creation prerequisites with missing fund name."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        fund_data['name'] = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Fund name is required"):
            self.coordination_service._validate_fund_creation_prerequisites(
                company, entity, fund_data
            )
    
    def test_validate_fund_creation_prerequisites_missing_fund_type(self):
        """Test validation of fund creation prerequisites with missing fund type."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        fund_data['fund_type'] = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Fund type is required"):
            self.coordination_service._validate_fund_creation_prerequisites(
                company, entity, fund_data
            )
    
    def test_validate_fund_creation_prerequisites_missing_tracking_type(self):
        """Test validation of fund creation prerequisites with missing tracking type."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        fund_data['tracking_type'] = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Tracking type is required"):
            self.coordination_service._validate_fund_creation_prerequisites(
                company, entity, fund_data
            )
    
    # ============================================================================
    # EDGE CASES AND ERROR HANDLING TESTS
    # ============================================================================
    
    def test_validate_fund_creation_business_rules_empty_funds_list(self):
        """Test business rule validation with empty funds list."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        company.funds = []
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 0
    
    def test_validate_fund_creation_business_rules_none_funds(self):
        """Test business rule validation with None funds."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        company.funds = None
        entity = CoordinationTestDataBuilder.create_entity()
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 0
    
    def test_validate_fund_creation_business_rules_empty_abn(self):
        """Test business rule validation with empty ABN string."""
        # Arrange
        company = CoordinationTestDataBuilder.create_company()
        entity = CoordinationTestDataBuilder.create_entity()
        entity.abn = ""
        fund_data = CoordinationTestDataBuilder.create_fund_data()
        
        # Act
        result = self.coordination_service.validate_fund_creation_business_rules(
            company, entity, fund_data
        )
        
        # Assert
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 1
        assert "Entity ABN appears invalid - please verify" in result['warnings'][0]
