"""
Fund Status Service Tests

This module tests the FundStatusService's core functionality for managing fund status transitions.

What we test here:
- Status transition logic after equity events
- Status transition logic after tax statement events
- Final tax statement determination logic
- Business rule enforcement for status changes

What we DON'T test here (tested elsewhere):
- Repository data access (test_fund_repository.py)
- Model validation (test_fund_model.py)
- Event processing (test_fund_event_service.py)
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch

from src.fund.services.fund_status_service import FundStatusService
from src.fund.enums import FundStatus
from src.fund.models.fund import Fund
from src.fund.models.domain_event import FundFieldChange


class TestFundStatusService:
    """Test suite for FundStatusService core functionality"""
    
    @pytest.fixture
    def service(self):
        """Create a FundStatusService instance for testing."""
        return FundStatusService()
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def active_fund(self):
        """Create a fund in ACTIVE status with equity balance."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Test Fund"
        fund.status = FundStatus.ACTIVE
        fund.current_equity_balance = 1000.0
        fund.end_date = None
        return fund
    
    @pytest.fixture
    def realized_fund(self):
        """Create a fund in REALIZED status with zero equity balance."""
        fund = Mock(spec=Fund)
        fund.id = 2
        fund.name = "Realized Fund"
        fund.status = FundStatus.REALIZED
        fund.current_equity_balance = 0.0
        fund.end_date = date(2020, 12, 31)
        return fund
    
    @pytest.fixture
    def completed_fund(self):
        """Create a fund in COMPLETED status."""
        fund = Mock(spec=Fund)
        fund.id = 3
        fund.name = "Completed Fund"
        fund.status = FundStatus.COMPLETED
        fund.current_equity_balance = 0.0
        fund.end_date = date(2020, 12, 31)
        return fund

    # ============================================================================
    # TESTS FOR update_status_after_equity_event
    # ============================================================================
    
    def test_update_status_after_equity_event_active_to_realized(self, service, active_fund, mock_session):
        """Test status transition from ACTIVE to REALIZED when equity balance becomes zero."""
        # Arrange
        active_fund.current_equity_balance = 0.0
        
        # Mock the final tax statement check to return False (no final tax statement)
        with patch.object(service, '_is_final_tax_statement_received', return_value=False):
            # Act
            result = service.update_status_after_equity_event(active_fund, mock_session)
            
            # Assert
            assert active_fund.status == FundStatus.REALIZED
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], FundFieldChange)
            assert result[0].field_name == 'status'
            assert result[0].old_value == FundStatus.ACTIVE
            assert result[0].new_value == FundStatus.REALIZED
    
    def test_update_status_after_equity_event_active_to_completed(self, service, active_fund, mock_session):
        """Test status transition from ACTIVE to COMPLETED when equity balance becomes zero and final tax statement exists."""
        # Arrange
        active_fund.current_equity_balance = 0.0
        
        # Mock the final tax statement check to return True (final tax statement exists)
        with patch.object(service, '_is_final_tax_statement_received', return_value=True):
            # Act
            result = service.update_status_after_equity_event(active_fund, mock_session)
            
            # Assert
            assert active_fund.status == FundStatus.COMPLETED
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], FundFieldChange)
            assert result[0].field_name == 'status'
            assert result[0].old_value == FundStatus.ACTIVE
            assert result[0].new_value == FundStatus.COMPLETED
    
    def test_update_status_after_equity_event_realized_to_active(self, service, realized_fund, mock_session):
        """Test status transition from REALIZED to ACTIVE when equity balance becomes positive."""
        # Arrange
        realized_fund.current_equity_balance = 1000.0
        
        # Act
        result = service.update_status_after_equity_event(realized_fund, mock_session)
        
        # Assert
        assert realized_fund.status == FundStatus.ACTIVE
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], FundFieldChange)
        assert result[0].field_name == 'status'
        assert result[0].old_value == FundStatus.REALIZED
        assert result[0].new_value == FundStatus.ACTIVE
    
    def test_update_status_after_equity_event_no_change_needed(self, service, active_fund, mock_session):
        """Test that no status change occurs when fund should remain ACTIVE."""
        # Arrange
        active_fund.current_equity_balance = 500.0  # Positive balance, should stay ACTIVE
        
        # Act
        result = service.update_status_after_equity_event(active_fund, mock_session)
        
        # Assert
        assert active_fund.status == FundStatus.ACTIVE
        assert result is None
    
    def test_update_status_after_equity_event_realized_remains_realized(self, service, realized_fund, mock_session):
        """Test that REALIZED fund remains REALIZED when equity balance is zero."""
        # Arrange
        realized_fund.current_equity_balance = 0.0
        
        # Mock the final tax statement check to return False
        with patch.object(service, '_is_final_tax_statement_received', return_value=False):
            # Act
            result = service.update_status_after_equity_event(realized_fund, mock_session)
            
            # Assert
            assert realized_fund.status == FundStatus.REALIZED
            assert result is None

    # ============================================================================
    # TESTS FOR update_status_after_tax_statement
    # ============================================================================
    
    def test_update_status_after_tax_statement_realized_to_completed(self, service, realized_fund, mock_session):
        """Test status transition from REALIZED to COMPLETED when final tax statement is received."""
        # Arrange
        realized_fund.status = FundStatus.REALIZED
        
        # Mock the final tax statement check to return True
        with patch.object(service, '_is_final_tax_statement_received', return_value=True):
            # Act
            result = service.update_status_after_tax_statement(realized_fund, mock_session)
            
            # Assert
            assert realized_fund.status == FundStatus.COMPLETED
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], FundFieldChange)
            assert result[0].field_name == 'status'
            assert result[0].old_value == FundStatus.REALIZED
            assert result[0].new_value == FundStatus.COMPLETED
    
    def test_update_status_after_tax_statement_completed_reverts_to_realized(self, service, completed_fund, mock_session):
        """Test status reversion from COMPLETED to REALIZED when final tax statement is removed."""
        # Arrange
        completed_fund.status = FundStatus.COMPLETED
        
        # Mock the final tax statement check to return False (tax statement removed)
        with patch.object(service, '_is_final_tax_statement_received', return_value=False):
            # Act
            result = service.update_status_after_tax_statement(completed_fund, mock_session)
            
            # Assert
            assert completed_fund.status == FundStatus.REALIZED
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], FundFieldChange)
            assert result[0].field_name == 'status'
            assert result[0].old_value == FundStatus.COMPLETED
            assert result[0].new_value == FundStatus.REALIZED
    
    def test_update_status_after_tax_statement_active_fund_no_change(self, service, active_fund, mock_session):
        """Test that ACTIVE fund status is not affected by tax statement events."""
        # Arrange
        active_fund.status = FundStatus.ACTIVE
        
        # Act
        result = service.update_status_after_tax_statement(active_fund, mock_session)
        
        # Assert
        assert active_fund.status == FundStatus.ACTIVE
        assert result is None
    
    def test_update_status_after_tax_statement_realized_remains_realized(self, service, realized_fund, mock_session):
        """Test that REALIZED fund remains REALIZED when no final tax statement exists."""
        # Arrange
        realized_fund.status = FundStatus.REALIZED
        
        # Mock the final tax statement check to return False
        with patch.object(service, '_is_final_tax_statement_received', return_value=False):
            # Act
            result = service.update_status_after_tax_statement(realized_fund, mock_session)
            
            # Assert
            assert realized_fund.status == FundStatus.REALIZED
            assert result is None

    # ============================================================================
    # TESTS FOR _is_final_tax_statement_received
    # ============================================================================
    
    def test_is_final_tax_statement_received_active_fund_returns_false(self, service, active_fund, mock_session):
        """Test that ACTIVE funds always return False for final tax statement check."""
        # Arrange
        active_fund.status = FundStatus.ACTIVE
        
        # Act
        result = service._is_final_tax_statement_received(active_fund, mock_session)
        
        # Assert
        assert result is False
    
    def test_is_final_tax_statement_received_no_end_date_returns_false(self, service, realized_fund, mock_session):
        """Test that funds without end date return False for final tax statement check."""
        # Arrange
        realized_fund.status = FundStatus.REALIZED
        realized_fund.end_date = None
        
        # Act
        result = service._is_final_tax_statement_received(realized_fund, mock_session)
        
        # Assert
        assert result is False
    
    def test_is_final_tax_statement_received_with_tax_statements_after_end_date(self, service, realized_fund, mock_session):
        """Test that funds with tax statements after end date return True."""
        # Arrange
        realized_fund.status = FundStatus.REALIZED
        realized_fund.end_date = date(2020, 12, 31)
        
        # Mock tax statements after end date
        mock_tax_statement = Mock()
        mock_tax_statement.tax_payment_date = date(2021, 5, 15)  # After end date
        
        with patch('src.fund.repositories.TaxStatementRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_by_fund_after_date.return_value = [mock_tax_statement]
            
            # Act
            result = service._is_final_tax_statement_received(realized_fund, mock_session)
            
            # Assert
            assert result is True
            mock_repo.get_by_fund_after_date.assert_called_once_with(realized_fund.id, realized_fund.end_date, mock_session)
    
    def test_is_final_tax_statement_received_with_no_tax_statements_after_end_date(self, service, realized_fund, mock_session):
        """Test that funds with no tax statements after end date return False."""
        # Arrange
        realized_fund.status = FundStatus.REALIZED
        realized_fund.end_date = date(2020, 12, 31)
        
        with patch('src.fund.repositories.TaxStatementRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_by_fund_after_date.return_value = []  # No tax statements after end date
            
            # Act
            result = service._is_final_tax_statement_received(realized_fund, mock_session)
            
            # Assert
            assert result is False
            mock_repo.get_by_fund_after_date.assert_called_once_with(realized_fund.id, realized_fund.end_date, mock_session)
    
    def test_is_final_tax_statement_received_with_tax_statements_before_end_date(self, service, realized_fund, mock_session):
        """Test that funds with tax statements before end date return False."""
        # Arrange
        realized_fund.status = FundStatus.REALIZED
        realized_fund.end_date = date(2020, 12, 31)
        
        # Mock tax statements before end date
        mock_tax_statement = Mock()
        mock_tax_statement.tax_payment_date = date(2020, 5, 15)  # Before end date
        
        with patch('src.fund.repositories.TaxStatementRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_by_fund_after_date.return_value = []  # Repository filters correctly, returns empty
            
            # Act
            result = service._is_final_tax_statement_received(realized_fund, mock_session)
            
            # Assert
            assert result is False
            mock_repo.get_by_fund_after_date.assert_called_once_with(realized_fund.id, realized_fund.end_date, mock_session)
