"""
Company IRR Service Unit Tests.

This module tests the CompanyIrRService class, focusing on business logic,
IRR calculations, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or calculator logic directly.

Test Coverage:
- IRR updates for active companies
- IRR updates for completed companies
- IRR field changes tracking
- Service layer orchestration
- Error handling
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.investment_company.services.company_irr_service import CompanyIrRService
from src.investment_company.models import InvestmentCompany
from src.investment_company.enums.company_enums import CompanyStatus
from src.fund.models.domain_fund_event import FundFieldChange
from tests.factories.investment_company_factories import InvestmentCompanyFactory
from tests.factories.fund_factories import FundEventFactory


class TestCompanyIrRService:
    """Test suite for CompanyIrRService."""

    @pytest.fixture
    def service(self):
        """Create a CompanyIrRService instance for testing."""
        return CompanyIrRService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_active_company(self):
        """Mock active company instance."""
        return InvestmentCompanyFactory.build(
            id=1, 
            name='Active Company',
            status=CompanyStatus.ACTIVE,
            completed_irr_gross=0.15,
            completed_irr_after_tax=0.12,
            completed_irr_real=0.10
        )

    @pytest.fixture
    def mock_completed_company(self):
        """Mock completed company instance."""
        return InvestmentCompanyFactory.build(
            id=2, 
            name='Completed Company',
            status=CompanyStatus.COMPLETED,
            completed_irr_gross=0.18,
            completed_irr_after_tax=0.15,
            completed_irr_real=0.13
        )

    @pytest.fixture
    def mock_fund_events(self):
        """Mock fund events."""
        return [FundEventFactory.build() for _ in range(3)]

    @pytest.fixture
    def fund_ids(self):
        """Sample fund IDs."""
        return [1, 2, 3]

    ################################################################################
    # Test update_irrs method for ACTIVE companies
    ################################################################################

    def test_update_irrs_sets_irrs_to_none_for_active_company(self, service, mock_session, mock_active_company, fund_ids):
        """Test that update_irrs sets all IRRs to None for active companies."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base') as mock_calculate:
            
            # Act
            result = service.update_irrs(mock_active_company, fund_ids, mock_session)

            # Assert
            assert mock_active_company.completed_irr_gross is None
            assert mock_active_company.completed_irr_after_tax is None
            assert mock_active_company.completed_irr_real is None
            
            # Verify fund events are not fetched for active companies
            mock_get_events.assert_not_called()
            mock_calculate.assert_not_called()

    def test_update_irrs_returns_changes_for_active_company(self, service, mock_session, mock_active_company, fund_ids):
        """Test that update_irrs returns changes when setting IRRs to None for active companies."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_get_events:
            # Act
            result = service.update_irrs(mock_active_company, fund_ids, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 3  # All three IRR fields changed
            
            # Verify field changes
            field_names = [change.field_name for change in result]
            assert 'completed_irr_gross' in field_names
            assert 'completed_irr_after_tax' in field_names
            assert 'completed_irr_real' in field_names

    def test_update_irrs_creates_correct_field_changes_for_active_company(self, service, mock_session, mock_active_company, fund_ids):
        """Test that update_irrs creates correct FundFieldChange objects for active companies."""
        # Arrange
        old_gross = mock_active_company.completed_irr_gross
        old_after_tax = mock_active_company.completed_irr_after_tax
        old_real = mock_active_company.completed_irr_real
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_get_events:
            # Act
            result = service.update_irrs(mock_active_company, fund_ids, mock_session)

            # Assert
            assert result is not None
            
            # Find specific field changes
            gross_change = next((change for change in result if change.field_name == 'completed_irr_gross'), None)
            after_tax_change = next((change for change in result if change.field_name == 'completed_irr_after_tax'), None)
            real_change = next((change for change in result if change.field_name == 'completed_irr_real'), None)
            
            # Verify field change properties
            assert gross_change.object == 'COMPANY'
            assert gross_change.object_id == mock_active_company.id
            assert gross_change.old_value == old_gross
            assert gross_change.new_value is None
            
            assert after_tax_change.object == 'COMPANY'
            assert after_tax_change.object_id == mock_active_company.id
            assert after_tax_change.old_value == old_after_tax
            assert after_tax_change.new_value is None
            
            assert real_change.object == 'COMPANY'
            assert real_change.object_id == mock_active_company.id
            assert real_change.old_value == old_real
            assert real_change.new_value is None

    ################################################################################
    # Test update_irrs method for COMPLETED companies
    ################################################################################

    def test_update_irrs_calculates_irrs_for_completed_company(self, service, mock_session, mock_completed_company, mock_fund_events, fund_ids):
        """Test that update_irrs calculates IRRs for completed companies."""
        # Arrange
        expected_gross = 0.20
        expected_after_tax = 0.17
        expected_real = 0.15
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base') as mock_calculate:
            
            # Setup calculator mock to return different values for each call
            mock_calculate.side_effect = [expected_gross, expected_after_tax, expected_real]
            
            # Act
            result = service.update_irrs(mock_completed_company, fund_ids, mock_session)

            # Assert
            assert mock_completed_company.completed_irr_gross == expected_gross
            assert mock_completed_company.completed_irr_after_tax == expected_after_tax
            assert mock_completed_company.completed_irr_real == expected_real
            
            # Verify fund events are fetched
            mock_get_events.assert_called_once_with(mock_session, fund_ids=fund_ids)
            
            # Verify IRR calculations are called with correct parameters
            assert mock_calculate.call_count == 3
            mock_calculate.assert_any_call(mock_fund_events, include_tax_payments=False, include_risk_free_charges=False, include_eofy_debt_cost=False)
            mock_calculate.assert_any_call(mock_fund_events, include_tax_payments=True, include_risk_free_charges=False, include_eofy_debt_cost=False)
            mock_calculate.assert_any_call(mock_fund_events, include_tax_payments=True, include_risk_free_charges=True, include_eofy_debt_cost=True)

    def test_update_irrs_returns_changes_for_completed_company(self, service, mock_session, mock_completed_company, mock_fund_events, fund_ids):
        """Test that update_irrs returns changes when calculating IRRs for completed companies."""
        # Arrange
        expected_gross = 0.20
        expected_after_tax = 0.17
        expected_real = 0.15
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base') as mock_calculate:
            
            # Setup calculator mock
            mock_calculate.side_effect = [expected_gross, expected_after_tax, expected_real]
            
            # Act
            result = service.update_irrs(mock_completed_company, fund_ids, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 3  # All three IRR fields changed
            
            # Verify field changes
            field_names = [change.field_name for change in result]
            assert 'completed_irr_gross' in field_names
            assert 'completed_irr_after_tax' in field_names
            assert 'completed_irr_real' in field_names

    def test_update_irrs_returns_none_when_no_changes(self, service, mock_session, mock_completed_company, mock_fund_events, fund_ids):
        """Test that update_irrs returns None when IRR values don't change."""
        # Arrange
        # Use same values as company already has
        same_gross = mock_completed_company.completed_irr_gross
        same_after_tax = mock_completed_company.completed_irr_after_tax
        same_real = mock_completed_company.completed_irr_real
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base') as mock_calculate:
            
            # Setup calculator mock to return same values
            mock_calculate.side_effect = [same_gross, same_after_tax, same_real]
            
            # Act
            result = service.update_irrs(mock_completed_company, fund_ids, mock_session)

            # Assert
            assert result is None

    def test_update_irrs_creates_correct_field_changes_for_completed_company(self, service, mock_session, mock_completed_company, mock_fund_events, fund_ids):
        """Test that update_irrs creates correct FundFieldChange objects for completed companies."""
        # Arrange
        old_gross = mock_completed_company.completed_irr_gross
        old_after_tax = mock_completed_company.completed_irr_after_tax
        old_real = mock_completed_company.completed_irr_real
        
        expected_gross = 0.20
        expected_after_tax = 0.17
        expected_real = 0.15
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base') as mock_calculate:
            
            # Setup calculator mock
            mock_calculate.side_effect = [expected_gross, expected_after_tax, expected_real]
            
            # Act
            result = service.update_irrs(mock_completed_company, fund_ids, mock_session)

            # Assert
            assert result is not None
            
            # Find specific field changes
            gross_change = next((change for change in result if change.field_name == 'completed_irr_gross'), None)
            after_tax_change = next((change for change in result if change.field_name == 'completed_irr_after_tax'), None)
            real_change = next((change for change in result if change.field_name == 'completed_irr_real'), None)
            
            # Verify field change properties
            assert gross_change.object == 'COMPANY'
            assert gross_change.object_id == mock_completed_company.id
            assert gross_change.old_value == old_gross
            assert gross_change.new_value == expected_gross
            
            assert after_tax_change.object == 'COMPANY'
            assert after_tax_change.object_id == mock_completed_company.id
            assert after_tax_change.old_value == old_after_tax
            assert after_tax_change.new_value == expected_after_tax
            
            assert real_change.object == 'COMPANY'
            assert real_change.object_id == mock_completed_company.id
            assert real_change.old_value == old_real
            assert real_change.new_value == expected_real

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.shared_irr_service is not None
        assert service.fund_event_repository is not None
        assert hasattr(service, 'shared_irr_service')
        assert hasattr(service, 'fund_event_repository')
