"""
Enterprise-grade unit tests for CompanyCalculationService.

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

from src.investment_company.services.company_calculation_service import CompanyCalculationService
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.enums import CompanyType, CompanyStatus
from src.fund.models import Fund
from src.fund.enums import FundStatus
from src.entity.models import Entity


class CalculationTestDataBuilder:
    """Test data builder for creating consistent calculation test objects."""
    
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
            'abn': '12345678901'
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


class TestCompanyCalculationService:
    """Enterprise-grade test suite for CompanyCalculationService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.calculation_service = CompanyCalculationService()
        self.mock_session = CalculationTestDataBuilder.create_session()
    
    def teardown_method(self):
        """Clean up after each test method."""
        pass
    
    # ============================================================================
    # PORTFOLIO CALCULATIONS TESTS
    # ============================================================================
    
    def test_calculate_total_funds_under_management_with_funds(self):
        """Test calculating total funds when company has funds."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(id=1, name='Fund 1')
        fund2 = CalculationTestDataBuilder.create_fund(id=2, name='Fund 2')
        fund3 = CalculationTestDataBuilder.create_fund(id=3, name='Fund 3')
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2, fund3]
        )
        
        # Act
        result = self.calculation_service.calculate_total_funds_under_management(
            company, self.mock_session
        )
        
        # Assert
        assert result == 3
        assert isinstance(result, int)
    
    def test_calculate_total_funds_under_management_without_funds(self):
        """Test calculating total funds when company has no funds."""
        # Arrange
        company = CalculationTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.calculation_service.calculate_total_funds_under_management(
            company, self.mock_session
        )
        
        # Assert
        assert result == 0
        assert isinstance(result, int)
    
    def test_calculate_total_funds_under_management_with_none_funds(self):
        """Test calculating total funds when company funds is None."""
        # Arrange
        company = CalculationTestDataBuilder.create_company(funds=None)
        
        # Act
        result = self.calculation_service.calculate_total_funds_under_management(
            company, self.mock_session
        )
        
        # Assert
        assert result == 0
        assert isinstance(result, int)
    
    def test_calculate_total_commitments_with_funds(self):
        """Test calculating total commitments when company has funds."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, commitment_amount=1000000.0
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, commitment_amount=2500000.0
        )
        fund3 = CalculationTestDataBuilder.create_fund(
            id=3, commitment_amount=1500000.0
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2, fund3]
        )
        
        # Act
        result = self.calculation_service.calculate_total_commitments(
            company, self.mock_session
        )
        
        # Assert
        assert result == 5000000.0
        assert isinstance(result, float)
    
    def test_calculate_total_commitments_without_funds(self):
        """Test calculating total commitments when company has no funds."""
        # Arrange
        company = CalculationTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.calculation_service.calculate_total_commitments(
            company, self.mock_session
        )
        
        # Assert
        assert result == 0.0
        assert isinstance(result, float)
    
    def test_calculate_total_commitments_with_none_commitment_amounts(self):
        """Test calculating total commitments when some funds have None commitment amounts."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, commitment_amount=1000000.0
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, commitment_amount=None
        )
        fund3 = CalculationTestDataBuilder.create_fund(
            id=3, commitment_amount=1500000.0
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2, fund3]
        )
        
        # Act
        result = self.calculation_service.calculate_total_commitments(
            company, self.mock_session
        )
        
        # Assert
        assert result == 2500000.0
        assert isinstance(result, float)
    
    def test_calculate_active_funds_count_with_active_funds(self):
        """Test calculating active funds count when company has active funds."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, status=FundStatus.ACTIVE
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, status=FundStatus.ACTIVE
        )
        fund3 = CalculationTestDataBuilder.create_fund(
            id=3, status=FundStatus.COMPLETED
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2, fund3]
        )
        
        # Act
        result = self.calculation_service.calculate_active_funds_count(
            company, self.mock_session
        )
        
        # Assert
        assert result == 2
        assert isinstance(result, int)
    
    def test_calculate_active_funds_count_without_funds(self):
        """Test calculating active funds count when company has no funds."""
        # Arrange
        company = CalculationTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.calculation_service.calculate_active_funds_count(
            company, self.mock_session
        )
        
        # Assert
        assert result == 0
        assert isinstance(result, int)
    
    def test_calculate_completed_funds_count_with_completed_funds(self):
        """Test calculating completed funds count when company has completed funds."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, status=FundStatus.ACTIVE
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, status=FundStatus.COMPLETED
        )
        fund3 = CalculationTestDataBuilder.create_fund(
            id=3, status=FundStatus.COMPLETED
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2, fund3]
        )
        
        # Act
        result = self.calculation_service.calculate_completed_funds_count(
            company, self.mock_session
        )
        
        # Assert
        assert result == 2
        assert isinstance(result, int)
    
    # ============================================================================
    # PERFORMANCE CALCULATIONS TESTS
    # ============================================================================
    
    def test_calculate_average_commitment_size_with_funds(self):
        """Test calculating average commitment size when company has funds."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, commitment_amount=1000000.0
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, commitment_amount=2000000.0
        )
        fund3 = CalculationTestDataBuilder.create_fund(
            id=3, commitment_amount=3000000.0
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2, fund3]
        )
        
        # Act
        result = self.calculation_service.calculate_average_commitment_size(
            company, self.mock_session
        )
        
        # Assert
        expected_average = (1000000.0 + 2000000.0 + 3000000.0) / 3
        assert result == expected_average
        assert isinstance(result, float)
    
    def test_calculate_average_commitment_size_without_funds(self):
        """Test calculating average commitment size when company has no funds."""
        # Arrange
        company = CalculationTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.calculation_service.calculate_average_commitment_size(
            company, self.mock_session
        )
        
        # Assert
        assert result == 0.0
        assert isinstance(result, float)
    
    def test_calculate_average_commitment_size_with_none_commitment_amounts(self):
        """Test calculating average commitment size when some funds have None commitment amounts."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, commitment_amount=1000000.0
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, commitment_amount=None
        )
        fund3 = CalculationTestDataBuilder.create_fund(
            id=3, commitment_amount=3000000.0
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2, fund3]
        )
        
        # Act
        result = self.calculation_service.calculate_average_commitment_size(
            company, self.mock_session
        )
        
        # Assert
        expected_average = (1000000.0 + 3000000.0) / 2
        assert result == expected_average
        assert isinstance(result, float)
    
    def test_calculate_portfolio_diversification_score_with_multiple_funds(self):
        """Test calculating diversification score with multiple funds."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(id=1)
        fund2 = CalculationTestDataBuilder.create_fund(id=2)
        fund3 = CalculationTestDataBuilder.create_fund(id=3)
        fund4 = CalculationTestDataBuilder.create_fund(id=4)
        fund5 = CalculationTestDataBuilder.create_fund(id=5)
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2, fund3, fund4, fund5]
        )
        
        # Act
        result = self.calculation_service.calculate_portfolio_diversification_score(
            company, self.mock_session
        )
        
        # Assert
        expected_score = 5 / 10  # 5 funds out of 10 max for scoring
        assert result == expected_score
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
    
    def test_calculate_portfolio_diversification_score_with_single_fund(self):
        """Test calculating diversification score with single fund."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(id=1)
        company = CalculationTestDataBuilder.create_company(funds=[fund1])
        
        # Act
        result = self.calculation_service.calculate_portfolio_diversification_score(
            company, self.mock_session
        )
        
        # Assert
        assert result == 0.0  # No diversification with 1 fund
        assert isinstance(result, float)
    
    def test_calculate_portfolio_diversification_score_without_funds(self):
        """Test calculating diversification score without funds."""
        # Arrange
        company = CalculationTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.calculation_service.calculate_portfolio_diversification_score(
            company, self.mock_session
        )
        
        # Assert
        assert result == 0.0
        assert isinstance(result, float)
    
    def test_calculate_portfolio_diversification_score_with_max_funds(self):
        """Test calculating diversification score with maximum scoring funds."""
        # Arrange
        funds = []
        for i in range(15):  # More than max_funds_for_scoring (10)
            funds.append(CalculationTestDataBuilder.create_fund(id=i))
        
        company = CalculationTestDataBuilder.create_company(funds=funds)
        
        # Act
        result = self.calculation_service.calculate_portfolio_diversification_score(
            company, self.mock_session
        )
        
        # Assert
        assert result == 1.0  # Maximum score when >= 10 funds
        assert isinstance(result, float)
    
    # ============================================================================
    # SUMMARY CALCULATIONS TESTS
    # ============================================================================
    
    def test_calculate_company_summary_metrics_with_funds(self):
        """Test calculating comprehensive company summary metrics."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, status=FundStatus.ACTIVE, commitment_amount=1000000.0
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, status=FundStatus.ACTIVE, commitment_amount=2000000.0
        )
        fund3 = CalculationTestDataBuilder.create_fund(
            id=3, status=FundStatus.COMPLETED, commitment_amount=1500000.0
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2, fund3]
        )
        
        # Act
        result = self.calculation_service.calculate_company_summary_metrics(
            company, self.mock_session
        )
        
        # Assert
        assert result['total_funds'] == 3
        assert result['active_funds'] == 2
        assert result['completed_funds'] == 1
        assert result['total_commitments'] == 4500000.0
        assert result['average_commitment_size'] == 1500000.0
        assert result['diversification_score'] == 0.3  # 3/10
        assert isinstance(result, dict)
    
    def test_calculate_company_summary_metrics_without_funds(self):
        """Test calculating company summary metrics without funds."""
        # Arrange
        company = CalculationTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.calculation_service.calculate_company_summary_metrics(
            company, self.mock_session
        )
        
        # Assert
        assert result['total_funds'] == 0
        assert result['active_funds'] == 0
        assert result['completed_funds'] == 0
        assert result['total_commitments'] == 0.0
        assert result['average_commitment_size'] == 0.0
        assert result['diversification_score'] == 0.0
        assert isinstance(result, dict)
    
    def test_calculate_portfolio_summary_with_funds(self):
        """Test calculating portfolio summary with funds."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, status=FundStatus.ACTIVE, commitment_amount=1000000.0
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, status=FundStatus.COMPLETED, commitment_amount=2000000.0
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2]
        )
        
        # Act
        result = self.calculation_service.calculate_portfolio_summary(
            company, self.mock_session
        )
        
        # Assert
        assert result['fund_count'] == 2
        assert result['total_commitments'] == 3000000.0
        assert result['active_commitments'] == 1000000.0
        assert result['completed_commitments'] == 2000000.0
        assert 'ACTIVE' in result['funds_by_status']
        assert 'COMPLETED' in result['funds_by_status']
        assert result['funds_by_status']['ACTIVE']['count'] == 1
        assert result['funds_by_status']['ACTIVE']['total_commitments'] == 1000000.0
        assert result['funds_by_status']['COMPLETED']['count'] == 1
        assert result['funds_by_status']['COMPLETED']['total_commitments'] == 2000000.0
        assert isinstance(result, dict)
    
    def test_calculate_portfolio_summary_without_funds(self):
        """Test calculating portfolio summary without funds."""
        # Arrange
        company = CalculationTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.calculation_service.calculate_portfolio_summary(
            company, self.mock_session
        )
        
        # Assert
        assert result['fund_count'] == 0
        assert result['total_commitments'] == 0.0
        assert result['active_commitments'] == 0.0
        assert result['completed_commitments'] == 0.0
        assert result['funds_by_status'] == {}
        assert isinstance(result, dict)
    
    def test_calculate_portfolio_summary_with_none_status_funds(self):
        """Test calculating portfolio summary with funds that have None status."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, status=None, commitment_amount=1000000.0
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, status=FundStatus.ACTIVE, commitment_amount=2000000.0
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2]
        )
        
        # Act
        result = self.calculation_service.calculate_portfolio_summary(
            company, self.mock_session
        )
        
        # Assert
        assert result['fund_count'] == 2
        assert result['total_commitments'] == 3000000.0
        assert result['active_commitments'] == 2000000.0
        assert result['completed_commitments'] == 0.0
        assert 'UNKNOWN' in result['funds_by_status']
        assert 'ACTIVE' in result['funds_by_status']
        assert result['funds_by_status']['UNKNOWN']['count'] == 1
        assert result['funds_by_status']['UNKNOWN']['total_commitments'] == 1000000.0
        assert isinstance(result, dict)
    
    # ============================================================================
    # EDGE CASES AND ERROR HANDLING TESTS
    # ============================================================================
    
    def test_calculate_total_commitments_with_zero_commitment_amounts(self):
        """Test calculating total commitments with zero commitment amounts."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, commitment_amount=0.0
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, commitment_amount=0.0
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2]
        )
        
        # Act
        result = self.calculation_service.calculate_total_commitments(
            company, self.mock_session
        )
        
        # Assert
        assert result == 0.0
        assert isinstance(result, float)
    
    def test_calculate_average_commitment_size_with_zero_commitment_amounts(self):
        """Test calculating average commitment size with zero commitment amounts."""
        # Arrange
        fund1 = CalculationTestDataBuilder.create_fund(
            id=1, commitment_amount=0.0
        )
        fund2 = CalculationTestDataBuilder.create_fund(
            id=2, commitment_amount=0.0
        )
        
        company = CalculationTestDataBuilder.create_company(
            funds=[fund1, fund2]
        )
        
        # Act
        result = self.calculation_service.calculate_average_commitment_size(
            company, self.mock_session
        )
        
        # Assert
        assert result == 0.0
        assert isinstance(result, float)
    
    def test_calculate_portfolio_diversification_score_with_negative_funds(self):
        """Test calculating diversification score with edge case fund counts."""
        # Arrange - This shouldn't happen in practice, but test for robustness
        company = CalculationTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.calculation_service.calculate_portfolio_diversification_score(
            company, self.mock_session
        )
        
        # Assert
        assert result == 0.0
        assert isinstance(result, float)
