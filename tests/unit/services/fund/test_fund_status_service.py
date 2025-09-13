"""
Fund Status Service Orchestration Tests

This module tests the FundStatusService's orchestration of business workflows.
Focus: Testing how the service coordinates between different components to achieve business outcomes.

What we test here:
- Status transition workflows
- Service coordination
- Business rule enforcement
- End-to-end business scenarios

What we DON'T test here (tested elsewhere):
- Individual IRR calculation logic (test_fund_irr_service.py)
- Repository data access (test_fund_repository.py)
- Model validation (test_fund_model.py)
- Event processing (test_fund_event_service.py)
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from src.fund.services.fund_status_service import FundStatusService
from src.fund.enums import FundStatus, FundType, EventType
from src.fund.models.fund import Fund
from src.fund.models.fund_event import FundEvent


class TestFundStatusServiceOrchestration:
    """Test suite for FundStatusService orchestration and business workflows"""
    
    @pytest.fixture
    def mock_event_repository(self):
        """Create a mock event repository for testing."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_event_repository):
        """Create a FundStatusService instance for testing with injected dependencies."""
        return FundStatusService(event_repository=mock_event_repository)
    
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
        fund.start_date = date(2020, 1, 1)
        fund.end_date = None
        fund.completed_irr_gross = None
        fund.completed_irr_after_tax = None
        fund.completed_irr_real = None
        return fund
    
    @pytest.fixture
    def realized_fund(self):
        """Create a fund in REALIZED status with zero equity balance."""
        fund = Mock(spec=Fund)
        fund.id = 2
        fund.name = "Realized Fund"
        fund.status = FundStatus.REALIZED
        fund.current_equity_balance = 0.0
        fund.start_date = date(2020, 1, 1)
        fund.end_date = date(2020, 12, 31)
        fund.completed_irr_gross = 0.15
        fund.completed_irr_after_tax = None
        fund.completed_irr_real = None
        return fund

    def test_orchestrates_active_to_realized_transition_workflow(self, service, active_fund, mock_session):
        """Test that the service orchestrates the complete ACTIVE to REALIZED workflow."""
        # Arrange
        active_fund.current_equity_balance = 0.0  # Trigger REALIZED transition
        
        # Mock the dependencies that the service orchestrates
        with patch('src.fund.services.fund_status_service.FundIrRService') as mock_irr_service_class, \
             patch.object(service, 'calculate_end_date') as mock_calculate_end_date:
            
            # Setup mocked IRR service
            mock_irr_service = Mock()
            mock_irr_service_class.return_value = mock_irr_service
            mock_irr_service.calculate_completed_irr.return_value = 0.15
            
            # Setup mocked end date calculation
            mock_calculate_end_date.return_value = date(2020, 12, 31)
            
            # Act - Orchestrate the REALIZED workflow
            service.update_status(active_fund, mock_session)
            
            # Assert - Verify the orchestration worked
            assert active_fund.status == FundStatus.REALIZED
            assert active_fund.completed_irr_gross == 0.15
            assert active_fund.completed_irr_after_tax is None
            assert active_fund.completed_irr_real is None
            
            # Verify the service coordinated the right components
            mock_irr_service_class.assert_called_once_with(mock_session)
            mock_irr_service.calculate_completed_irr.assert_called_once_with(active_fund)
            mock_calculate_end_date.assert_called_once_with(active_fund, mock_session)

    def test_orchestrates_realized_to_active_transition_workflow(self, service, realized_fund, mock_session):
        """Test that the service orchestrates the complete REALIZED to ACTIVE workflow."""
        # Arrange
        realized_fund.current_equity_balance = 500.0  # Trigger ACTIVE transition
        
        # Act - Orchestrate the ACTIVE workflow
        service.update_status(realized_fund, mock_session)
        
        # Assert - Verify the orchestration worked
        assert realized_fund.status == FundStatus.ACTIVE
        assert realized_fund.completed_irr_gross is None
        assert realized_fund.completed_irr_after_tax is None
        assert realized_fund.completed_irr_real is None

    def test_orchestrates_tax_statement_completion_workflow(self, service, realized_fund, mock_session):
        """Test that the service orchestrates the complete tax statement completion workflow."""
        # Arrange
        mock_tax_statement = Mock()
        mock_tax_statement.tax_payment_date = date(2021, 5, 15)  # After fund end date
        realized_fund.tax_statements = [mock_tax_statement]
        
        # Mock the dependencies
        with patch('src.fund.services.fund_status_service.FundIrRService') as mock_irr_service_class, \
             patch.object(service, 'calculate_end_date') as mock_calculate_end_date, \
             patch('src.fund.repositories.TaxStatementRepository') as mock_tax_repo_class:
            
            # Setup mocked IRR service for COMPLETED status
            mock_irr_service = Mock()
            mock_irr_service_class.return_value = mock_irr_service
            mock_irr_service.calculate_completed_irr.return_value = 0.18
            mock_irr_service.calculate_completed_after_tax_irr.return_value = 0.15
            mock_irr_service.calculate_completed_real_irr.return_value = 0.13
            
            # Setup mocked end date calculation
            mock_calculate_end_date.return_value = date(2020, 12, 31)
            
            # Setup mocked tax statement repository
            mock_tax_repo = Mock()
            mock_tax_repo_class.return_value = mock_tax_repo
            mock_tax_repo.get_by_fund_after_date.return_value = [mock_tax_statement]  # Return list, not Mock
            
            # Act - Orchestrate the tax statement completion workflow
            service.update_status_after_tax_statement(realized_fund, mock_session)
            
            # Assert - Verify the orchestration worked
            assert realized_fund.status == FundStatus.COMPLETED
            assert realized_fund.completed_irr_gross == 0.18
            assert realized_fund.completed_irr_after_tax == 0.15
            assert realized_fund.completed_irr_real == 0.13
            
            # Verify the service coordinated the right components
            mock_irr_service_class.assert_called_once_with(mock_session)
            mock_irr_service.calculate_completed_irr.assert_called_once_with(realized_fund)
            mock_irr_service.calculate_completed_after_tax_irr.assert_called_once_with(realized_fund)
            mock_irr_service.calculate_completed_real_irr.assert_called_once_with(realized_fund)

    def test_orchestrates_end_date_calculation_workflow(self, service, active_fund, mock_session, mock_event_repository):
        """Test that the service orchestrates the end date calculation workflow."""
        # Arrange
        mock_events = [
            self._create_mock_event(EventType.CAPITAL_CALL, date(2020, 1, 1), 1000.0),
            self._create_mock_event(EventType.RETURN_OF_CAPITAL, date(2020, 12, 31), 0.0),
        ]
        mock_event_repository.get_by_fund.return_value = mock_events
        
        # Act - Orchestrate the end date calculation
        result = service.calculate_end_date(active_fund, mock_session)
        
        # Assert - Verify the orchestration worked
        assert result == date(2020, 12, 31)
        
        # Verify the service coordinated the repository
        mock_event_repository.get_by_fund.assert_called_once_with(active_fund.id, mock_session)

    def test_orchestrates_status_summary_workflow(self, service, active_fund, mock_session):
        """Test that the service orchestrates the status summary workflow."""
        # Arrange
        active_fund.current_equity_balance = 1000.0
        active_fund.tax_statements = []
        
        # Mock the dependencies
        with patch.object(service, 'calculate_end_date') as mock_calculate_end_date:
            mock_calculate_end_date.return_value = None
            
            # Act - Orchestrate the status summary workflow
            summary = service.get_status_summary(active_fund, mock_session)
            
            # Assert - Verify the orchestration worked
            assert summary['current_status'] == FundStatus.ACTIVE
            assert summary['start_date'] == date(2020, 1, 1)
            assert summary['end_date'] is None
            assert 'is_final_tax_statement_received' in summary
            assert 'status_transition_allowed' in summary
            
            # Verify the service coordinated the right components
            mock_calculate_end_date.assert_called_once_with(active_fund, mock_session)

    def test_enforces_business_rules_for_status_transitions(self, service, active_fund, mock_session):
        """Test that the service enforces business rules for status transitions."""
        # Test: ACTIVE fund with positive equity should remain ACTIVE
        active_fund.current_equity_balance = 500.0
        service.update_status(active_fund, mock_session)
        assert active_fund.status == FundStatus.ACTIVE
        
        # Test: ACTIVE fund with zero equity should transition to REALIZED
        active_fund.current_equity_balance = 0.0
        with patch('src.fund.services.fund_status_service.FundIrRService'), \
             patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)):
            service.update_status(active_fund, mock_session)
        assert active_fund.status == FundStatus.REALIZED

    def test_handles_missing_session_gracefully(self, service, active_fund):
        """Test that the service handles missing session gracefully in orchestration."""
        # Act - Call without session
        service.update_status(active_fund)
        
        # Assert - Should not crash and should handle gracefully
        # The exact behavior depends on implementation, but it shouldn't raise exceptions
        assert active_fund.status in [FundStatus.ACTIVE, FundStatus.REALIZED]

    def test_orchestrates_duration_updates_during_status_changes(self, service, active_fund, mock_session):
        """Test that the service orchestrates duration updates during status changes."""
        # Arrange
        active_fund.current_equity_balance = 0.0
        active_fund.calculate_and_update_current_duration = Mock()
        
        # Mock dependencies
        with patch('src.fund.services.fund_status_service.FundIrRService'), \
             patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)):
            
            # Act - Orchestrate status change
            service.update_status(active_fund, mock_session)
            
            # Assert - Verify duration update was orchestrated
            # Note: It's called twice - once in calculate_and_store_irrs_for_status and once in update_status
            assert active_fund.calculate_and_update_current_duration.call_count >= 1

    def _create_mock_event(self, event_type: EventType, event_date: date, equity_balance: float):
        """Helper method to create mock fund events."""
        event = Mock(spec=FundEvent)
        event.event_type = event_type
        event.event_date = event_date
        event.current_equity_balance = equity_balance
        return event

    def test_orchestrates_complex_business_scenario(self, service, mock_session):
        """Test orchestration of a complex business scenario."""
        # Arrange - Create a fund that goes through multiple status changes
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Complex Fund"
        fund.status = FundStatus.ACTIVE
        fund.start_date = date(2020, 1, 1)
        fund.completed_irr_gross = None
        fund.completed_irr_after_tax = None
        fund.completed_irr_real = None
        
        # Mock dependencies for the complex scenario
        with patch('src.fund.services.fund_status_service.FundIrRService') as mock_irr_service_class, \
             patch.object(service, 'calculate_end_date') as mock_calculate_end_date:
            
            mock_irr_service = Mock()
            mock_irr_service_class.return_value = mock_irr_service
            mock_irr_service.calculate_completed_irr.return_value = 0.15
            mock_calculate_end_date.return_value = date(2020, 12, 31)
            
            # Act - Orchestrate complex scenario
            # 1. Fund starts ACTIVE with equity
            fund.current_equity_balance = 1000.0
            service.update_status(fund, mock_session)
            assert fund.status == FundStatus.ACTIVE
            
            # 2. Fund transitions to REALIZED when equity goes to zero
            fund.current_equity_balance = 0.0
            service.update_status(fund, mock_session)
            assert fund.status == FundStatus.REALIZED
            assert fund.completed_irr_gross == 0.15
            
            # 3. Fund transitions back to ACTIVE when equity increases
            fund.current_equity_balance = 500.0
            service.update_status(fund, mock_session)
            assert fund.status == FundStatus.ACTIVE
            assert fund.completed_irr_gross is None

    def test_orchestrates_edge_case_transitions(self, service, mock_session):
        """Test orchestration of edge case status transitions."""
        # Test transition when equity balance is exactly zero
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Edge Case Fund"
        fund.status = FundStatus.ACTIVE
        fund.start_date = date(2020, 1, 1)
        fund.completed_irr_gross = None
        fund.completed_irr_after_tax = None
        fund.completed_irr_real = None
        
        with patch('src.fund.services.fund_status_service.FundIrRService') as mock_irr_service_class, \
             patch.object(service, 'calculate_end_date') as mock_calculate_end_date:
            
            mock_irr_service = Mock()
            mock_irr_service_class.return_value = mock_irr_service
            mock_irr_service.calculate_completed_irr.return_value = 0.15
            mock_calculate_end_date.return_value = date(2020, 12, 31)
            
            # Test exactly zero balance
            fund.current_equity_balance = 0.0
            service.update_status(fund, mock_session)
            assert fund.status == FundStatus.REALIZED
            
            # Test very small positive balance
            fund.current_equity_balance = 0.01
            service.update_status(fund, mock_session)
            assert fund.status == FundStatus.ACTIVE

    def test_orchestrates_irr_calculation_for_different_statuses(self, service, mock_session, mock_event_repository):
        """Test orchestration of IRR calculations for different fund statuses."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "IRR Test Fund"
        fund.start_date = date(2020, 1, 1)
        fund.completed_irr_gross = None
        fund.completed_irr_after_tax = None
        fund.completed_irr_real = None
        
        # Mock the repository to return empty events for end date calculation
        mock_event_repository.get_by_fund.return_value = []
        
        # Test ACTIVE status - should reset IRRs
        fund.status = FundStatus.ACTIVE
        service.calculate_and_store_irrs_for_status(fund, FundStatus.ACTIVE, mock_session)
        assert fund.completed_irr_gross is None
        assert fund.completed_irr_after_tax is None
        assert fund.completed_irr_real is None
        
        # Test REALIZED status - should calculate gross IRR only
        with patch('src.fund.services.fund_status_service.FundIrRService') as mock_irr_service_class:
            mock_irr_service = Mock()
            mock_irr_service_class.return_value = mock_irr_service
            mock_irr_service.calculate_completed_irr.return_value = 0.15
            
            service.calculate_and_store_irrs_for_status(fund, FundStatus.REALIZED, mock_session)
            assert fund.completed_irr_gross == 0.15
            assert fund.completed_irr_after_tax is None
            assert fund.completed_irr_real is None
        
        # Test COMPLETED status - should calculate all IRRs
        with patch('src.fund.services.fund_status_service.FundIrRService') as mock_irr_service_class:
            mock_irr_service = Mock()
            mock_irr_service_class.return_value = mock_irr_service
            mock_irr_service.calculate_completed_irr.return_value = 0.18
            mock_irr_service.calculate_completed_after_tax_irr.return_value = 0.15
            mock_irr_service.calculate_completed_real_irr.return_value = 0.13
            
            service.calculate_and_store_irrs_for_status(fund, FundStatus.COMPLETED, mock_session)
            assert fund.completed_irr_gross == 0.18
            assert fund.completed_irr_after_tax == 0.15
            assert fund.completed_irr_real == 0.13

    def test_orchestrates_unknown_status_gracefully(self, service, mock_session):
        """Test orchestration handles unknown status gracefully."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Unknown Status Fund"
        fund.completed_irr_gross = None
        fund.completed_irr_after_tax = None
        fund.completed_irr_real = None
        
        # Should not raise an error for unknown status
        service.calculate_and_store_irrs_for_status(fund, "UNKNOWN_STATUS", mock_session)
        
        # IRRs should remain None
        assert fund.completed_irr_gross is None
        assert fund.completed_irr_after_tax is None
        assert fund.completed_irr_real is None

    def test_orchestrates_tax_statement_scenarios(self, service, realized_fund, mock_session):
        """Test orchestration of various tax statement scenarios."""
        # Test tax statement before fund end date
        mock_tax_statement_before = Mock()
        mock_tax_statement_before.tax_payment_date = date(2020, 5, 15)  # Before end date
        realized_fund.tax_statements = [mock_tax_statement_before]
        
        with patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)), \
             patch('src.fund.repositories.TaxStatementRepository') as mock_tax_repo_class:
            # Setup mocked tax statement repository
            mock_tax_repo = Mock()
            mock_tax_repo_class.return_value = mock_tax_repo
            mock_tax_repo.get_by_fund_after_date.return_value = []  # No tax statements after end date
            
            result = service._is_final_tax_statement_received(realized_fund, mock_session)
            assert result is False
        
        # Test tax statement after fund end date
        mock_tax_statement_after = Mock()
        mock_tax_statement_after.tax_payment_date = date(2021, 5, 15)  # After end date
        realized_fund.tax_statements = [mock_tax_statement_after]
        
        with patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)), \
             patch('src.fund.repositories.TaxStatementRepository') as mock_tax_repo_class:
            # Setup mocked tax statement repository
            mock_tax_repo = Mock()
            mock_tax_repo_class.return_value = mock_tax_repo
            mock_tax_repo.get_by_fund_after_date.return_value = [mock_tax_statement_after]  # Tax statement after end date
            
            result = service._is_final_tax_statement_received(realized_fund, mock_session)
            assert result is True
        
        # Test no tax statements
        realized_fund.tax_statements = []
        with patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)), \
             patch('src.fund.repositories.TaxStatementRepository') as mock_tax_repo_class:
            # Setup mocked tax statement repository
            mock_tax_repo = Mock()
            mock_tax_repo_class.return_value = mock_tax_repo
            mock_tax_repo.get_by_fund_after_date.return_value = []  # No tax statements
            
            result = service._is_final_tax_statement_received(realized_fund, mock_session)
            assert result is False
