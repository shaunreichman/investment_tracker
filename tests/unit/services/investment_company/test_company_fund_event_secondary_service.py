"""
Company Fund Event Secondary Service Unit Tests.

This module tests the CompanyFundEventSecondaryService class, focusing on business logic,
secondary impact handling, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or calculator logic directly.

Test Coverage:
- Secondary impact handling for fund events
- Company field updates based on fund changes
- Status management and IRR updates
- Service layer orchestration
- Error handling
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import date

from src.investment_company.services.company_fund_event_secondary_service import CompanyFundEventSecondaryService
from src.investment_company.models import InvestmentCompany
from src.fund.models.domain_fund_event import FundFieldChange
from src.investment_company.enums.company_enums import CompanyStatus
from src.fund.enums.fund_enums import FundStatus
from tests.factories.investment_company_factories import InvestmentCompanyFactory
from tests.factories.fund_factories import FundFactory


class TestCompanyFundEventSecondaryService:
    """Test suite for CompanyFundEventSecondaryService."""

    @pytest.fixture
    def service(self):
        """Create a CompanyFundEventSecondaryService instance for testing."""
        return CompanyFundEventSecondaryService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_company(self):
        """Mock company instance."""
        return InvestmentCompanyFactory.build(
            id=1, 
            name='Test Company',
            start_date=date(2023, 1, 1),
            pnl=100000,
            realized_pnl=80000,
            unrealized_pnl=20000,
            realized_pnl_capital_gain=50000,
            unrealized_pnl_capital_gain=10000,
            realized_pnl_dividend=20000,
            realized_pnl_interest=5000,
            realized_pnl_distribution=5000,
            total_funds_active=2,
            total_funds_realized=1,
            total_funds_completed=0,
            status=CompanyStatus.ACTIVE
        )

    @pytest.fixture
    def mock_funds(self):
        """Mock funds for the company."""
        return [
            FundFactory.build(id=1, company_id=1),
            FundFactory.build(id=2, company_id=1),
            FundFactory.build(id=3, company_id=1)
        ]

    @pytest.fixture
    def sample_fund_changes(self):
        """Sample fund field changes."""
        return [
            FundFieldChange(fund_or_company='FUND', object_id=1, field_name='pnl', old_value=50000, new_value=60000),
            FundFieldChange(fund_or_company='FUND', object_id=1, field_name='start_date', old_value=date(2023, 2, 1), new_value=date(2023, 1, 15))
        ]

    ################################################################################
    # Test handle_event_secondary_impact method
    ################################################################################

    def test_handle_event_secondary_impact_raises_error_when_company_not_found(self, service, mock_session, sample_fund_changes):
        """Test that handle_event_secondary_impact raises ValueError when company not found."""
        # Arrange
        company_id = 999
        with patch.object(service.company_repository, 'get_company_by_id', return_value=None) as mock_get_company:
            # Act & Assert
            with pytest.raises(ValueError, match="Company not found"):
                service.handle_event_secondary_impact(company_id, sample_fund_changes, mock_session)
            
            mock_get_company.assert_called_once_with(company_id, mock_session)

    def test_handle_event_secondary_impact_handles_start_date_changes(self, service, mock_session, mock_company, sample_fund_changes):
        """Test that handle_event_secondary_impact handles start date changes correctly."""
        # Arrange
        company_id = 1
        start_date_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='start_date', 
            old_value=date(2023, 2, 1), 
            new_value=date(2022, 12, 15)  # Earlier than company's start date
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class, \
             patch('src.shared.calculators.duration_months_calculator.DurationMonthsCalculator.calculate_duration_months', return_value=24) as mock_duration_calc:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            service.handle_event_secondary_impact(company_id, [start_date_change], mock_session)

            # Assert
            assert mock_company.start_date == date(2022, 12, 15)
            assert mock_company.current_duration == 24
            mock_duration_calc.assert_called_once_with(mock_company.start_date, date(2022, 12, 15))

    def test_handle_event_secondary_impact_handles_pnl_changes(self, service, mock_session, mock_company):
        """Test that handle_event_secondary_impact handles PnL changes correctly."""
        # Arrange
        company_id = 1
        pnl_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='pnl', 
            old_value=50000, 
            new_value=60000
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            service.handle_event_secondary_impact(company_id, [pnl_change], mock_session)

            # Assert
            assert mock_company.pnl == 160000  # 100000 + 60000

    def test_handle_event_secondary_impact_handles_realized_pnl_changes(self, service, mock_session, mock_company):
        """Test that handle_event_secondary_impact handles realized PnL changes correctly."""
        # Arrange
        company_id = 1
        realized_pnl_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='realized_pnl', 
            old_value=30000, 
            new_value=40000
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            service.handle_event_secondary_impact(company_id, [realized_pnl_change], mock_session)

            # Assert
            assert mock_company.realized_pnl == 120000  # 80000 + 40000

    def test_handle_event_secondary_impact_handles_unrealized_pnl_changes(self, service, mock_session, mock_company):
        """Test that handle_event_secondary_impact handles unrealized PnL changes correctly."""
        # Arrange
        company_id = 1
        unrealized_pnl_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='unrealized_pnl', 
            old_value=10000, 
            new_value=15000
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            service.handle_event_secondary_impact(company_id, [unrealized_pnl_change], mock_session)

            # Assert
            assert mock_company.unrealized_pnl == 35000  # 20000 + 15000

    def test_handle_event_secondary_impact_handles_capital_gain_changes(self, service, mock_session, mock_company):
        """Test that handle_event_secondary_impact handles capital gain changes correctly."""
        # Arrange
        company_id = 1
        realized_capital_gain_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='realized_pnl_capital_gain', 
            old_value=20000, 
            new_value=25000
        )
        unrealized_capital_gain_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='unrealized_pnl_capital_gain', 
            old_value=5000, 
            new_value=8000
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            service.handle_event_secondary_impact(company_id, [realized_capital_gain_change, unrealized_capital_gain_change], mock_session)

            # Assert
            assert mock_company.realized_pnl_capital_gain == 75000  # 50000 + 25000
            assert mock_company.unrealized_pnl_capital_gain == 18000  # 10000 + 8000

    def test_handle_event_secondary_impact_handles_dividend_changes(self, service, mock_session, mock_company):
        """Test that handle_event_secondary_impact handles dividend changes correctly."""
        # Arrange
        company_id = 1
        dividend_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='realized_pnl_dividend', 
            old_value=5000, 
            new_value=8000
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            service.handle_event_secondary_impact(company_id, [dividend_change], mock_session)

            # Assert
            assert mock_company.realized_pnl_dividend == 28000  # 20000 + 8000

    def test_handle_event_secondary_impact_handles_interest_changes(self, service, mock_session, mock_company):
        """Test that handle_event_secondary_impact handles interest changes correctly."""
        # Arrange
        company_id = 1
        interest_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='realized_pnl_interest', 
            old_value=2000, 
            new_value=3500
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            service.handle_event_secondary_impact(company_id, [interest_change], mock_session)

            # Assert
            assert mock_company.realized_pnl_interest == 8500  # 5000 + 3500

    def test_handle_event_secondary_impact_handles_distribution_changes(self, service, mock_session, mock_company):
        """Test that handle_event_secondary_impact handles distribution changes correctly."""
        # Arrange
        company_id = 1
        distribution_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='realized_pnl_distribution', 
            old_value=1000, 
            new_value=2000
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            service.handle_event_secondary_impact(company_id, [distribution_change], mock_session)

            # Assert
            assert mock_company.realized_pnl_distribution == 7000  # 5000 + 2000

    def test_handle_event_secondary_impact_handles_status_changes(self, service, mock_session, mock_company):
        """Test that handle_event_secondary_impact handles fund status changes correctly."""
        # Arrange
        company_id = 1
        status_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='status', 
            old_value=FundStatus.ACTIVE, 
            new_value=FundStatus.REALIZED
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class, \
             patch.object(service.company_irr_service, 'update_irrs') as mock_update_irrs:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            service.handle_event_secondary_impact(company_id, [status_change], mock_session)

            # Assert
            assert mock_company.total_funds_active == 1  # 2 - 1
            assert mock_company.total_funds_realized == 2  # 1 + 1

    def test_handle_event_secondary_impact_sets_company_status_to_completed_when_no_active_funds(self, service, mock_session, mock_company):
        """Test that handle_event_secondary_impact sets company status to COMPLETED when no active funds."""
        # Arrange
        company_id = 1
        # Set company to have only 1 active fund
        mock_company.total_funds_active = 1
        status_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='status', 
            old_value=FundStatus.ACTIVE, 
            new_value=FundStatus.REALIZED
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class, \
             patch.object(service.company_irr_service, 'update_irrs') as mock_update_irrs:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Act
            service.handle_event_secondary_impact(company_id, [status_change], mock_session)

            # Assert
            assert mock_company.status == CompanyStatus.COMPLETED
            assert mock_company.total_funds_active == 0  # 1 - 1

    def test_handle_event_secondary_impact_calls_equity_service_for_equity_changes(self, service, mock_session, mock_company):
        """Test that handle_event_secondary_impact calls equity service for equity-related changes."""
        # Arrange
        company_id = 1
        equity_change = FundFieldChange(
            fund_or_company='FUND', 
            object_id=1, 
            field_name='average_equity_balance', 
            old_value=50000, 
            new_value=60000
        )
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch('src.fund.services.fund_service.FundService') as mock_fund_service_class, \
             patch.object(service.company_equity_service, 'update_company_equity_fields') as mock_equity_update:
            
            # Setup fund service mock
            mock_fund_service = Mock()
            mock_fund_service.get_funds.return_value = []
            mock_fund_service_class.return_value = mock_fund_service
            
            # Setup equity service mock
            mock_equity_update.return_value = [FundFieldChange(fund_or_company='COMPANY', object_id=1, field_name='average_equity_balance', old_value=100000, new_value=110000)]
            
            # Act
            service.handle_event_secondary_impact(company_id, [equity_change], mock_session)

            # Assert
            mock_equity_update.assert_called_once_with(company_id, [], mock_session)

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.company_repository is not None
        assert service.company_irr_service is not None
        assert service.company_equity_service is not None
        assert hasattr(service, 'company_repository')
        assert hasattr(service, 'company_irr_service')
        assert hasattr(service, 'company_equity_service')
