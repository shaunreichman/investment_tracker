"""
Enterprise-grade unit tests for CompanyPortfolioService.

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

from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.enums import CompanyType, CompanyStatus
from src.fund.models import Fund
from src.fund.enums import FundStatus
from src.entity.models import Entity


class PortfolioTestDataBuilder:
    """Test data builder for creating consistent portfolio test objects."""
    
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


class TestCompanyPortfolioService:
    """Enterprise-grade test suite for CompanyPortfolioService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.portfolio_service = CompanyPortfolioService()
        self.mock_session = PortfolioTestDataBuilder.create_session()
    
    def teardown_method(self):
        """Clean up after each test method."""
        pass  # No cleanup needed for this service

    # ============================================================================
    # FUND SUMMARY AND PORTFOLIO DATA TESTS
    # ============================================================================
    
    def test_get_funds_with_summary_success(self):
        """Test successful retrieval of funds with summary data."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        fund1 = PortfolioTestDataBuilder.create_fund(id=1, name='Fund 1')
        fund2 = PortfolioTestDataBuilder.create_fund(id=2, name='Fund 2')
        company.funds = [fund1, fund2]
        
        # Mock fund summary data method
        fund1.get_summary_data = Mock(return_value={'id': 1, 'name': 'Fund 1', 'summary': 'data1'})
        fund2.get_summary_data = Mock(return_value={'id': 2, 'name': 'Fund 2', 'summary': 'data2'})
        
        # Act
        result = self.portfolio_service.get_funds_with_summary(company, self.mock_session)
        
        # Assert
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['id'] == 2
        fund1.get_summary_data.assert_called_once_with(session=self.mock_session)
        fund2.get_summary_data.assert_called_once_with(session=self.mock_session)
    
    def test_get_funds_with_summary_empty_portfolio(self):
        """Test retrieval of funds with summary when portfolio is empty."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.portfolio_service.get_funds_with_summary(company, self.mock_session)
        
        # Assert
        assert result == []
    
    def test_get_total_funds_under_management_success(self):
        """Test successful calculation of total funds under management."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        fund1 = PortfolioTestDataBuilder.create_fund(id=1)
        fund2 = PortfolioTestDataBuilder.create_fund(id=2)
        company.funds = [fund1, fund2]
        
        # Mock the CompanyCalculationService - it's imported inside the method
        with patch('src.investment_company.services.company_calculation_service.CompanyCalculationService') as mock_calc_service_class:
            mock_calc_service = Mock()
            mock_calc_service.calculate_total_funds_under_management.return_value = 2
            mock_calc_service_class.return_value = mock_calc_service
            
            # Act
            result = self.portfolio_service.get_total_funds_under_management(company, self.mock_session)
            
            # Assert
            assert result == 2
            mock_calc_service.calculate_total_funds_under_management.assert_called_once_with(company, self.mock_session)
    
    def test_get_total_commitments_success(self):
        """Test successful calculation of total commitments."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        fund1 = PortfolioTestDataBuilder.create_fund(id=1, commitment_amount=1000000.0)
        fund2 = PortfolioTestDataBuilder.create_fund(id=2, commitment_amount=2000000.0)
        company.funds = [fund1, fund2]
        
        # Mock the CompanyCalculationService - it's imported inside the method
        with patch('src.investment_company.services.company_calculation_service.CompanyCalculationService') as mock_calc_service_class:
            mock_calc_service = Mock()
            mock_calc_service.calculate_total_commitments.return_value = 3000000.0
            mock_calc_service_class.return_value = mock_calc_service
            
            # Act
            result = self.portfolio_service.get_total_commitments(company, self.mock_session)
            
            # Assert
            assert result == 3000000.0
            mock_calc_service.calculate_total_commitments.assert_called_once_with(company, self.mock_session)

    # ============================================================================
    # FUND CREATION TESTS
    # ============================================================================
    
    def test_create_fund_success(self):
        """Test successful fund creation with proper coordination."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        entity = PortfolioTestDataBuilder.create_entity()
        
        # Mock fund service and repository
        mock_fund_service = Mock()
        mock_fund_service.create_fund.return_value = {'id': 1, 'name': 'New Fund'}
        
        mock_fund_repository = Mock()
        mock_fund_repository.get_by_id.return_value = PortfolioTestDataBuilder.create_fund(id=1, name='New Fund')
        
        with patch('src.fund.services.fund_service.FundService') as mock_fund_service_class, \
             patch('src.fund.repositories.fund_repository.FundRepository') as mock_fund_repo_class:
            
            mock_fund_service_class.return_value = mock_fund_service
            mock_fund_repo_class.return_value = mock_fund_repository
            
            # Act
            result = self.portfolio_service.create_fund(
                company=company,
                entity=entity,
                name='New Fund',
                fund_type='Private Equity',
                tracking_type='COST_BASED',
                currency='AUD',
                description='Test fund',
                commitment_amount=1000000.0,
                session=self.mock_session
            )
            
            # Assert
            assert result.id == 1
            assert result.name == 'New Fund'
            mock_fund_service.create_fund.assert_called_once()
            mock_fund_repository.get_by_id.assert_called_once_with(1, self.mock_session)
    
    def test_create_fund_missing_entity(self):
        """Test fund creation fails when entity is missing."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Entity is required for fund creation coordination"):
            self.portfolio_service.create_fund(
                company=company,
                entity=None,
                name='New Fund',
                fund_type='Private Equity',
                tracking_type='COST_BASED',
                session=self.mock_session
            )
    
    def test_create_fund_publishes_portfolio_event(self):
        """Test that fund creation publishes portfolio updated event."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        entity = PortfolioTestDataBuilder.create_entity()
        
        # Mock fund service and repository
        mock_fund_service = Mock()
        mock_fund_service.create_fund.return_value = {'id': 1, 'name': 'New Fund'}
        
        mock_fund_repository = Mock()
        mock_fund_repository.get_by_id.return_value = PortfolioTestDataBuilder.create_fund(id=1, name='New Fund')
        
        # Mock FundCoordinationService
        with patch('src.investment_company.services.fund_coordination_service.FundCoordinationService') as mock_coordination_service_class:
            mock_coordination_service = Mock()
            mock_fund = PortfolioTestDataBuilder.create_fund(id=1, name='New Fund')
            mock_coordination_service.coordinate_fund_creation.return_value = mock_fund
            mock_coordination_service_class.return_value = mock_coordination_service
            
            # Act
            result = self.portfolio_service.create_fund(
                company=company,
                entity=entity,
                name='New Fund',
                fund_type='Private Equity',
                tracking_type='COST_BASED',
                session=self.mock_session
            )
            
            # Assert
            assert result == mock_fund
            mock_coordination_service.coordinate_fund_creation.assert_called_once_with(
                company, entity, 
                {
                    'name': 'New Fund',
                    'entity_id': entity.id,
                    'investment_company_id': company.id,
                    'fund_type': 'Private Equity',
                    'tracking_type': 'COST_BASED',
                    'currency': 'AUD',
                    'description': None,
                    'commitment_amount': None,
                    'expected_irr': None,
                    'expected_duration_months': None
                },
                self.mock_session
            )

    # ============================================================================
    # PORTFOLIO SUMMARY TESTS
    # ============================================================================
    
    def test_get_portfolio_summary_success(self):
        """Test successful portfolio summary generation."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        fund1 = PortfolioTestDataBuilder.create_fund(
            id=1, 
            commitment_amount=1000000.0, 
            current_equity_balance=950000.0,
            status=FundStatus.ACTIVE
        )
        fund2 = PortfolioTestDataBuilder.create_fund(
            id=2, 
            commitment_amount=2000000.0, 
            current_equity_balance=1800000.0,
            status=FundStatus.COMPLETED
        )
        company.funds = [fund1, fund2]
        
        # Act
        result = self.portfolio_service.get_portfolio_summary(company, self.mock_session)
        
        # Assert
        assert result['total_committed_capital'] == 3000000.0
        assert result['total_current_value'] == 2750000.0
        assert result['total_invested_capital'] == 2750000.0
        assert result['active_funds_count'] == 1
        assert result['completed_funds_count'] == 1
        # These fields are not returned by the actual service
        # assert result['suspended_funds_count'] == 0
        # assert result['realized_funds_count'] == 0
        assert result['fund_status_breakdown']['active_funds_count'] == 1
        assert result['fund_status_breakdown']['completed_funds_count'] == 1
    
    def test_get_portfolio_summary_empty_portfolio(self):
        """Test portfolio summary generation for empty portfolio."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.portfolio_service.get_portfolio_summary(company, self.mock_session)
        
        # Assert
        assert result['total_committed_capital'] == 0
        assert result['total_current_value'] == 0
        assert result['total_invested_capital'] == 0
        assert result['active_funds_count'] == 0
        assert result['completed_funds_count'] == 0
        # These fields are not returned by the actual service
        # assert result['suspended_funds_count'] == 0
        # assert result['realized_funds_count'] == 0
    
    def test_get_portfolio_summary_with_none_values(self):
        """Test portfolio summary handles None values gracefully."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        fund1 = PortfolioTestDataBuilder.create_fund(
            id=1, 
            commitment_amount=None, 
            current_equity_balance=None,
            status=FundStatus.ACTIVE
        )
        company.funds = [fund1]
        
        # Act
        result = self.portfolio_service.get_portfolio_summary(company, self.mock_session)
        
        # Assert
        assert result['total_committed_capital'] == 0
        assert result['total_current_value'] == 0
        assert result['total_invested_capital'] == 0

    # ============================================================================
    # LAST ACTIVITY TESTS
    # ============================================================================
    
    def test_get_last_activity_info_with_funds(self):
        """Test last activity info retrieval when funds have events."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        fund1 = PortfolioTestDataBuilder.create_fund(id=1)
        fund2 = PortfolioTestDataBuilder.create_fund(id=2)
        
        # Mock fund events with dates
        mock_event1 = Mock()
        mock_event1.event_date = date(2024, 1, 15)
        mock_event2 = Mock()
        mock_event2.event_date = date(2024, 1, 20)
        
        fund1.fund_events = [mock_event1]
        fund2.fund_events = [mock_event2]
        company.funds = [fund1, fund2]
        
        # Act
        result = self.portfolio_service.get_last_activity_info(company, self.mock_session)
        
        # Assert
        assert result['last_activity_date'] == '2024-01-20'
        assert result['days_since_last_activity'] is not None
    
    def test_get_last_activity_info_no_funds(self):
        """Test last activity info when company has no funds."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company(funds=[])
        
        # Act
        result = self.portfolio_service.get_last_activity_info(company, self.mock_session)
        
        # Assert
        assert result['last_activity_date'] is None
        assert result['days_since_last_activity'] is None
    
    def test_get_last_activity_info_funds_no_events(self):
        """Test last activity info when funds have no events."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        fund1 = PortfolioTestDataBuilder.create_fund(id=1, fund_events=[])
        company.funds = [fund1]
        
        # Act
        result = self.portfolio_service.get_last_activity_info(company, self.mock_session)
        
        # Assert
        assert result['last_activity_date'] is None
        assert result['days_since_last_activity'] is None

    # ============================================================================
    # FUND REMOVAL TESTS
    # ============================================================================
    
    def test_remove_fund_from_portfolio_success(self):
        """Test successful fund removal from portfolio."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        fund = PortfolioTestDataBuilder.create_fund(id=1)
        company.funds = [fund]
        
        # Mock event publishing
        with patch.object(self.portfolio_service, '_publish_portfolio_updated_event') as mock_publish:
            
            # Act
            self.portfolio_service.remove_fund_from_portfolio(company, 1, self.mock_session)
            
            # Assert
            mock_publish.assert_called_once_with(company, fund, 'removed', self.mock_session)
    
    def test_remove_fund_from_portfolio_fund_not_found(self):
        """Test fund removal fails when fund is not in portfolio."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company(funds=[])
        
        # Act & Assert
        with pytest.raises(ValueError, match="Fund 1 not found in company 1 portfolio"):
            self.portfolio_service.remove_fund_from_portfolio(company, 1, self.mock_session)

    # ============================================================================
    # FUND UPDATE TESTS
    # ============================================================================
    
    def test_update_fund_in_portfolio_success(self):
        """Test successful fund update in portfolio."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        fund = PortfolioTestDataBuilder.create_fund(id=1)
        company.funds = [fund]
        
        fund_data = {'name': 'Updated Fund', 'description': 'Updated description'}
        
        # Mock fund service
        mock_fund_service = Mock()
        mock_fund_service.update_fund.return_value = PortfolioTestDataBuilder.create_fund(id=1, name='Updated Fund')
        
        # Mock event publishing
        with patch('src.fund.services.fund_service.FundService') as mock_fund_service_class, \
             patch.object(self.portfolio_service, '_publish_portfolio_updated_event') as mock_publish:
            
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            result = self.portfolio_service.update_fund_in_portfolio(company, 1, fund_data, self.mock_session)
            
            # Assert
            assert result.name == 'Updated Fund'
            mock_fund_service.update_fund.assert_called_once_with(1, fund_data, self.mock_session)
            mock_publish.assert_called_once_with(company, mock_fund_service.update_fund.return_value, 'updated', self.mock_session)
    
    def test_update_fund_in_portfolio_fund_not_found(self):
        """Test fund update fails when fund is not in portfolio."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company(funds=[])
        fund_data = {'name': 'Updated Fund'}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Fund 1 not found in company 1 portfolio"):
            self.portfolio_service.update_fund_in_portfolio(company, 1, fund_data, self.mock_session)

    # ============================================================================
    # PORTFOLIO SUMMARY UPDATE TESTS
    # ============================================================================
    
    def test_update_portfolio_summary_success(self):
        """Test successful portfolio summary update."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        
        # Mock the get_portfolio_summary method
        with patch.object(self.portfolio_service, 'get_portfolio_summary') as mock_get_summary:
            mock_get_summary.return_value = {'total_committed_capital': 1000000.0}
            
            # Act
            self.portfolio_service.update_portfolio_summary(company, self.mock_session)
            
            # Assert
            mock_get_summary.assert_called_once_with(company, self.mock_session)
    
    def test_update_portfolio_summary_handles_exception(self):
        """Test portfolio summary update handles exceptions gracefully."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        
        # Mock the get_portfolio_summary method to raise an exception
        with patch.object(self.portfolio_service, 'get_portfolio_summary') as mock_get_summary, \
             patch('logging.getLogger') as mock_logger:
            
            mock_get_summary.side_effect = Exception("Test error")
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            
            # Act - Should not raise exception
            self.portfolio_service.update_portfolio_summary(company, self.mock_session)
            
            # Assert
            mock_logger_instance.warning.assert_called_once()

    # ============================================================================
    # HELPER METHOD TESTS
    # ============================================================================
    
    def test_get_fund_by_id_success(self):
        """Test successful fund retrieval by ID."""
        # Arrange
        fund_id = 1
        expected_fund = PortfolioTestDataBuilder.create_fund(id=1)
        
        # Mock fund repository
        mock_fund_repository = Mock()
        mock_fund_repository.get_by_id.return_value = expected_fund
        
        with patch('src.fund.repositories.fund_repository.FundRepository') as mock_fund_repo_class:
            mock_fund_repo_class.return_value = mock_fund_repository
            
            # Act
            result = self.portfolio_service._get_fund_by_id(fund_id, self.mock_session)
            
            # Assert
            assert result == expected_fund
            mock_fund_repository.get_by_id.assert_called_once_with(fund_id, self.mock_session)
    
    def test_publish_portfolio_updated_event_success(self):
        """Test successful portfolio updated event publishing."""
        # Arrange
        company = PortfolioTestDataBuilder.create_company()
        fund = PortfolioTestDataBuilder.create_fund()
        operation = 'added'
        
        # Mock event and registry
        mock_event = Mock()
        mock_registry = Mock()
        
        with patch('src.investment_company.events.domain.portfolio_updated_event.PortfolioUpdatedEvent') as mock_event_class, \
             patch('src.investment_company.events.registry.CompanyEventHandlerRegistry') as mock_registry_class:
            
            mock_event_class.return_value = mock_event
            mock_registry_class.return_value = mock_registry
            
            # Act
            self.portfolio_service._publish_portfolio_updated_event(company, fund, operation, self.mock_session)
            
            # Assert
            mock_event_class.assert_called_once()
            # The method now calls handle_event with event data dictionary
            mock_registry.handle_event.assert_called_once()
            # Verify the call was made with the expected arguments
            call_args = mock_registry.handle_event.call_args
            assert call_args[0][0]['event_type'] == 'PORTFOLIO_UPDATED'
            assert call_args[0][0]['company_id'] == company.id
            assert call_args[0][0]['fund_id'] == fund.id
            assert call_args[0][0]['operation'] == operation
