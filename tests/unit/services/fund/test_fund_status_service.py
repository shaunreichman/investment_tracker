"""
Fund Status Service Unit Tests.

This module tests the FundStatusService class, focusing on business logic,
status transitions, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Status transitions after equity events (ACTIVE/REALIZED/COMPLETED)
- Status transitions after tax statement events
- Final tax statement detection logic
- Service layer orchestration
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import date

from src.fund.services.fund_status_service import FundStatusService
from src.fund.models import Fund, FundTaxStatement
from src.shared.models.domain_update_event import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.fund.enums.fund_enums import FundStatus
from tests.factories.fund_factories import FundFactory, FundTaxStatementFactory


class TestFundStatusService:
    """Test suite for FundStatusService."""

    @pytest.fixture
    def service(self):
        """Create a FundStatusService instance for testing."""
        return FundStatusService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_fund_active(self):
        """Mock fund with ACTIVE status and positive equity balance."""
        return FundFactory.build(
            id=1,
            status=FundStatus.ACTIVE,
            current_equity_balance=1000.0,
            end_date=date(2023, 12, 31)
        )

    @pytest.fixture
    def mock_fund_realized(self):
        """Mock fund with REALIZED status and zero equity balance."""
        return FundFactory.build(
            id=2,
            status=FundStatus.REALIZED,
            current_equity_balance=0.0,
            end_date=date(2023, 12, 31)
        )

    @pytest.fixture
    def mock_fund_completed(self):
        """Mock fund with COMPLETED status and zero equity balance."""
        return FundFactory.build(
            id=3,
            status=FundStatus.COMPLETED,
            current_equity_balance=0.0,
            end_date=date(2023, 12, 31)
        )

    @pytest.fixture
    def mock_fund_suspended(self):
        """Mock fund with SUSPENDED status and positive equity balance."""
        return FundFactory.build(
            id=4,
            status=FundStatus.SUSPENDED,
            current_equity_balance=500.0,
            end_date=date(2023, 12, 31)
        )

    ################################################################################
    # Test update_status_after_equity_event method
    ################################################################################

    def test_update_status_after_equity_event_positive_balance_suspended_to_active(self, service, mock_session, mock_fund_suspended):
        """Test that fund transitions from SUSPENDED to ACTIVE when equity balance > 0."""
        # Act
        result = service.update_status_after_equity_event(mock_fund_suspended, mock_session)

        # Assert
        assert result is not None
        assert len(result) == 1
        assert mock_fund_suspended.status == FundStatus.ACTIVE
        
        change = result[0]
        assert change.domain_object_type == DomainObjectType.FUND
        assert change.domain_object_id == mock_fund_suspended.id
        assert change.field_name == 'status'
        assert change.old_value == FundStatus.SUSPENDED
        assert change.new_value == FundStatus.ACTIVE

    def test_update_status_after_equity_event_positive_balance_already_active_no_change(self, service, mock_session, mock_fund_active):
        """Test that fund remains ACTIVE when equity balance > 0 and already ACTIVE."""
        # Act
        result = service.update_status_after_equity_event(mock_fund_active, mock_session)

        # Assert
        assert result is None
        assert mock_fund_active.status == FundStatus.ACTIVE

    def test_update_status_after_equity_event_zero_balance_active_to_realized(self, service, mock_session, mock_fund_active):
        """Test that fund transitions from ACTIVE to REALIZED when equity balance <= 0."""
        # Arrange
        mock_fund_active.current_equity_balance = 0.0
        
        with patch.object(service, '_is_final_tax_statement_received', return_value=False):
            # Act
            result = service.update_status_after_equity_event(mock_fund_active, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 1
            assert mock_fund_active.status == FundStatus.REALIZED
            
            change = result[0]
            assert change.domain_object_type == DomainObjectType.FUND
            assert change.domain_object_id == mock_fund_active.id
            assert change.field_name == 'status'
            assert change.old_value == FundStatus.ACTIVE
            assert change.new_value == FundStatus.REALIZED

    def test_update_status_after_equity_event_zero_balance_with_final_tax_statement_active_to_completed(self, service, mock_session, mock_fund_active):
        """Test that fund transitions from ACTIVE to COMPLETED when equity balance <= 0 and final tax statement received."""
        # Arrange
        mock_fund_active.current_equity_balance = 0.0
        
        with patch.object(service, '_is_final_tax_statement_received', return_value=True):
            # Act
            result = service.update_status_after_equity_event(mock_fund_active, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 1
            assert mock_fund_active.status == FundStatus.COMPLETED
            
            change = result[0]
            assert change.domain_object_type == DomainObjectType.FUND
            assert change.domain_object_id == mock_fund_active.id
            assert change.field_name == 'status'
            assert change.old_value == FundStatus.ACTIVE
            assert change.new_value == FundStatus.COMPLETED

    def test_update_status_after_equity_event_non_active_status_no_change(self, service, mock_session, mock_fund_realized):
        """Test that non-ACTIVE funds don't change status based on equity balance."""
        # Act
        result = service.update_status_after_equity_event(mock_fund_realized, mock_session)

        # Assert
        assert result is None
        assert mock_fund_realized.status == FundStatus.REALIZED

    ################################################################################
    # Test update_status_after_tax_statement method
    ################################################################################

    def test_update_status_after_tax_statement_realized_to_completed(self, service, mock_session, mock_fund_realized):
        """Test that fund transitions from REALIZED to COMPLETED when final tax statement received."""
        with patch.object(service, '_is_final_tax_statement_received', return_value=True):
            # Act
            result = service.update_status_after_tax_statement(mock_fund_realized, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 1
            assert mock_fund_realized.status == FundStatus.COMPLETED
            
            change = result[0]
            assert change.domain_object_type == DomainObjectType.FUND
            assert change.domain_object_id == mock_fund_realized.id
            assert change.field_name == 'status'
            assert change.old_value == FundStatus.REALIZED
            assert change.new_value == FundStatus.COMPLETED

    def test_update_status_after_tax_statement_completed_to_realized_when_tax_statement_removed(self, service, mock_session, mock_fund_completed):
        """Test that fund transitions from COMPLETED to REALIZED when tax statement removed."""
        with patch.object(service, '_is_final_tax_statement_received', return_value=False):
            # Act
            result = service.update_status_after_tax_statement(mock_fund_completed, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 1
            assert mock_fund_completed.status == FundStatus.REALIZED
            
            change = result[0]
            assert change.domain_object_type == DomainObjectType.FUND
            assert change.domain_object_id == mock_fund_completed.id
            assert change.field_name == 'status'
            assert change.old_value == FundStatus.COMPLETED
            assert change.new_value == FundStatus.REALIZED

    def test_update_status_after_tax_statement_active_status_no_change(self, service, mock_session, mock_fund_active):
        """Test that ACTIVE funds don't change status based on tax statements."""
        # Act
        result = service.update_status_after_tax_statement(mock_fund_active, mock_session)

        # Assert
        assert result is None
        assert mock_fund_active.status == FundStatus.ACTIVE

    def test_update_status_after_tax_statement_no_final_tax_statement_no_change(self, service, mock_session, mock_fund_realized):
        """Test that fund remains REALIZED when no final tax statement received."""
        with patch.object(service, '_is_final_tax_statement_received', return_value=False):
            # Act
            result = service.update_status_after_tax_statement(mock_fund_realized, mock_session)

            # Assert
            assert result is None
            assert mock_fund_realized.status == FundStatus.REALIZED

    ################################################################################
    # Test _is_final_tax_statement_received method
    ################################################################################

    def test_is_final_tax_statement_received_active_fund_returns_false(self, service, mock_session, mock_fund_active):
        """Test that ACTIVE funds always return False for final tax statement check."""
        # Act
        result = service._is_final_tax_statement_received(mock_fund_active, mock_session)

        # Assert
        assert result is False

    def test_is_final_tax_statement_received_no_end_date_returns_false(self, service, mock_session, mock_fund_realized):
        """Test that funds without end_date return False for final tax statement check."""
        # Arrange
        mock_fund_realized.end_date = None

        # Act
        result = service._is_final_tax_statement_received(mock_fund_realized, mock_session)

        # Assert
        assert result is False

    def test_is_final_tax_statement_received_with_tax_statements_after_end_date_returns_true(self, service, mock_session, mock_fund_realized):
        """Test that funds with tax statements after end_date return True."""
        # Arrange
        mock_tax_statements = [
            FundTaxStatementFactory.build(
                fund_id=mock_fund_realized.id,
                tax_payment_date=date(2024, 1, 15)  # After end_date of 2023-12-31
            )
        ]
        
        with patch('src.fund.services.fund_status_service.FundTaxStatementRepository') as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.get_fund_tax_statements.return_value = mock_tax_statements

            # Act
            result = service._is_final_tax_statement_received(mock_fund_realized, mock_session)

            # Assert
            assert result is True
            mock_repo.get_fund_tax_statements.assert_called_once_with(
                fund_ids=[mock_fund_realized.id],
                start_tax_payment_date=mock_fund_realized.end_date,
                session=mock_session
            )

    def test_is_final_tax_statement_received_without_tax_statements_after_end_date_returns_false(self, service, mock_session, mock_fund_realized):
        """Test that funds without tax statements after end_date return False."""
        # Arrange
        with patch('src.fund.services.fund_status_service.FundTaxStatementRepository') as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.get_fund_tax_statements.return_value = []

            # Act
            result = service._is_final_tax_statement_received(mock_fund_realized, mock_session)

            # Assert
            assert result is False
            mock_repo.get_fund_tax_statements.assert_called_once_with(
                fund_ids=[mock_fund_realized.id],
                start_tax_payment_date=mock_fund_realized.end_date,
                session=mock_session
            )

    def test_is_final_tax_statement_received_with_tax_statements_before_end_date_returns_false(self, service, mock_session, mock_fund_realized):
        """Test that funds with tax statements before end_date return False."""
        # Arrange
        # The repository should return empty list when no tax statements match the criteria
        with patch('src.fund.services.fund_status_service.FundTaxStatementRepository') as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.get_fund_tax_statements.return_value = []  # No tax statements after end_date

            # Act
            result = service._is_final_tax_statement_received(mock_fund_realized, mock_session)

            # Assert
            assert result is False

    ################################################################################
    # Test edge cases and error handling
    ################################################################################

    def test_update_status_after_equity_event_negative_equity_balance(self, service, mock_session, mock_fund_active):
        """Test that fund transitions from ACTIVE to REALIZED when equity balance < 0."""
        # Arrange
        mock_fund_active.current_equity_balance = -100.0
        
        with patch.object(service, '_is_final_tax_statement_received', return_value=False):
            # Act
            result = service.update_status_after_equity_event(mock_fund_active, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 1
            assert mock_fund_active.status == FundStatus.REALIZED

    def test_update_status_after_equity_event_without_session(self, service, mock_fund_active):
        """Test that methods work without session parameter."""
        # Arrange
        mock_fund_active.current_equity_balance = 0.0
        
        with patch.object(service, '_is_final_tax_statement_received', return_value=False):
            # Act
            result = service.update_status_after_equity_event(mock_fund_active)

            # Assert
            assert result is not None
            assert len(result) == 1
            assert mock_fund_active.status == FundStatus.REALIZED

    def test_update_status_after_tax_statement_without_session(self, service, mock_fund_realized):
        """Test that tax statement method works without session parameter."""
        with patch.object(service, '_is_final_tax_statement_received', return_value=True):
            # Act
            result = service.update_status_after_tax_statement(mock_fund_realized)

            # Assert
            assert result is not None
            assert len(result) == 1
            assert mock_fund_realized.status == FundStatus.COMPLETED
