"""
Fund Tax Statement Service Unit Tests.

This module tests the FundTaxStatementService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Fund tax statement retrieval operations
- Fund tax statement creation with business rules and event generation
- Fund tax statement deletion with dependency validation
- Tax payment event creation logic
- Service layer orchestration
- Error handling and validation integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import date

from src.fund.services.fund_tax_statement_service import FundTaxStatementService
from src.fund.models import FundTaxStatement, FundEvent, Fund
from src.fund.enums.fund_tax_statement_enums import SortFieldFundTaxStatement
from src.fund.enums.fund_enums import FundTrackingType
from src.fund.enums.fund_event_enums import EventType, DistributionType, TaxPaymentType, GroupType
from src.shared.enums.shared_enums import SortOrder, EventOperation
from tests.factories.fund_factories import FundTaxStatementFactory, FundFactory, FundEventFactory


class TestFundTaxStatementService:
    """Test suite for FundTaxStatementService."""

    @pytest.fixture
    def service(self):
        """Create a FundTaxStatementService instance for testing."""
        return FundTaxStatementService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_tax_statement_data(self):
        """Sample tax statement data for testing."""
        return {
            'entity_id': 1,
            'financial_year': '2023-2024',
            'tax_payment_date': date(2024, 6, 30),
            'interest_income_amount': 10000.0,
            'interest_income_tax_rate': 30.0,
            'dividend_franked_income_amount': 5000.0,
            'dividend_franked_income_tax_rate': 15.0,
            'dividend_unfranked_income_amount': 3000.0,
            'dividend_unfranked_income_tax_rate': 30.0,
            'capital_gain_income_amount': 2000.0,
            'eofy_debt_interest_deduction_rate': 30.0
        }

    @pytest.fixture
    def mock_tax_statement(self):
        """Mock tax statement instance."""
        return FundTaxStatementFactory.build(
            id=1,
            fund_id=1,
            entity_id=1,
            financial_year='2023-2024',
            interest_income_amount=10000.0,
            interest_income_tax_rate=30.0
        )

    @pytest.fixture
    def mock_fund(self):
        """Mock fund instance."""
        return FundFactory.build(
            id=1,
            tracking_type=FundTrackingType.NAV_BASED,
            currency='AUD'
        )

    @pytest.fixture
    def mock_entity(self):
        """Mock entity instance."""
        entity = Mock()
        entity.id = 1
        entity.name = 'Test Entity'
        return entity

    ################################################################################
    # Test get_fund_tax_statements method
    ################################################################################

    def test_get_fund_tax_statements_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that get_fund_tax_statements calls repository with correct parameters."""
        # Arrange
        expected_statements = [FundTaxStatementFactory.build() for _ in range(2)]
        with patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=expected_statements) as mock_repo:
            # Act
            result = service.get_fund_tax_statements(mock_session)

            # Assert
            assert result == expected_statements
            mock_repo.assert_called_once_with(
                None, None, None, None, None,
                SortFieldFundTaxStatement.FINANCIAL_YEAR,
                SortOrder.ASC,
                mock_session
            )

    def test_get_fund_tax_statements_passes_filters_to_repository(self, service, mock_session):
        """Test that get_fund_tax_statements passes all filters to repository."""
        # Arrange
        fund_id = 1
        entity_id = 2
        financial_year = '2023-2024'
        start_date = date(2023, 7, 1)
        end_date = date(2024, 6, 30)
        sort_by = SortFieldFundTaxStatement.TAX_PAYMENT_DATE
        sort_order = SortOrder.DESC
        expected_statements = [FundTaxStatementFactory.build()]
        
        with patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=expected_statements) as mock_repo:
            # Act
            result = service.get_fund_tax_statements(
                mock_session,
                fund_id=fund_id,
                entity_id=entity_id,
                financial_year=financial_year,
                start_tax_payment_date=start_date,
                end_tax_payment_date=end_date,
                sort_by=sort_by,
                sort_order=sort_order
            )

            # Assert
            assert result == expected_statements
            mock_repo.assert_called_once_with(
                fund_id, entity_id, financial_year, start_date, end_date,
                sort_by, sort_order, mock_session
            )

    ################################################################################
    # Test get_fund_tax_statement_by_id method
    ################################################################################

    def test_get_fund_tax_statement_by_id_calls_repository_with_correct_id(self, service, mock_session, mock_tax_statement):
        """Test that get_fund_tax_statement_by_id calls repository with correct ID."""
        # Arrange
        statement_id = 1
        with patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statement_by_id', return_value=mock_tax_statement) as mock_repo:
            # Act
            result = service.get_fund_tax_statement_by_id(statement_id, mock_session)

            # Assert
            assert result == mock_tax_statement
            mock_repo.assert_called_once_with(statement_id, mock_session)

    def test_get_fund_tax_statement_by_id_returns_none_when_not_found(self, service, mock_session):
        """Test that get_fund_tax_statement_by_id returns None when statement not found."""
        # Arrange
        statement_id = 999
        with patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statement_by_id', return_value=None) as mock_repo:
            # Act
            result = service.get_fund_tax_statement_by_id(statement_id, mock_session)

            # Assert
            assert result is None
            mock_repo.assert_called_once_with(statement_id, mock_session)

    ################################################################################
    # Test create_fund_tax_statement method
    ################################################################################

    def test_create_fund_tax_statement_successfully_creates_statement_and_events(self, service, mock_session, sample_tax_statement_data, mock_tax_statement, mock_entity):
        """Test successful tax statement creation with event generation."""
        # Arrange
        fund_id = 1
        with patch('src.entity.repositories.entity_repository.EntityRepository') as mock_entity_repo_class, \
             patch.object(mock_entity_repo_class.return_value, 'get_entity_by_id', return_value=mock_entity) as mock_get_entity, \
             patch('src.fund.calculators.financial_year_calculator.FinancialYearCalculator.calculate_financial_year_dates', return_value=(date(2023, 7, 1), date(2024, 6, 30))) as mock_fy_calc, \
             patch.object(service.fund_tax_statement_repository, 'create_fund_tax_statement', return_value=mock_tax_statement) as mock_create_repo, \
             patch.object(service, '_create_daily_debt_cost_events', return_value=[]) as mock_daily_events, \
             patch.object(service, '_create_tax_payment_events', return_value=[]) as mock_tax_events, \
             patch.object(service.fund_event_repository, 'generate_group_id', return_value=1) as mock_group_id, \
             patch('src.fund.services.fund_event_secondary_service.FundEventSecondaryService') as mock_secondary_service_class:
            
            # Act
            result = service.create_fund_tax_statement(fund_id, sample_tax_statement_data, mock_session)

            # Assert
            assert result == mock_tax_statement
            mock_get_entity.assert_called_once_with(1, mock_session)
            mock_fy_calc.assert_called_once_with('2023-2024')
            mock_create_repo.assert_called_once()
            mock_daily_events.assert_called_once_with(mock_tax_statement, mock_session)
            mock_tax_events.assert_called_once_with(mock_tax_statement, mock_session)

    def test_create_fund_tax_statement_raises_error_when_entity_not_found(self, service, mock_session, sample_tax_statement_data):
        """Test that create_fund_tax_statement raises ValueError when entity not found."""
        # Arrange
        fund_id = 1
        with patch('src.entity.repositories.entity_repository.EntityRepository') as mock_entity_repo_class, \
             patch.object(mock_entity_repo_class.return_value, 'get_entity_by_id', return_value=None) as mock_get_entity:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Entity not found"):
                service.create_fund_tax_statement(fund_id, sample_tax_statement_data, mock_session)

    def test_create_fund_tax_statement_raises_error_when_repository_fails(self, service, mock_session, sample_tax_statement_data, mock_entity):
        """Test that create_fund_tax_statement raises ValueError when repository fails."""
        # Arrange
        fund_id = 1
        with patch('src.entity.repositories.entity_repository.EntityRepository') as mock_entity_repo_class, \
             patch.object(mock_entity_repo_class.return_value, 'get_entity_by_id', return_value=mock_entity) as mock_get_entity, \
             patch('src.fund.calculators.financial_year_calculator.FinancialYearCalculator.calculate_financial_year_dates', return_value=(date(2023, 7, 1), date(2024, 6, 30))), \
             patch.object(service.fund_tax_statement_repository, 'create_fund_tax_statement', return_value=None) as mock_create_repo:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to create fund tax statement"):
                service.create_fund_tax_statement(fund_id, sample_tax_statement_data, mock_session)

    def test_create_fund_tax_statement_processes_data_correctly(self, service, mock_session, sample_tax_statement_data, mock_entity, mock_tax_statement):
        """Test that create_fund_tax_statement processes data correctly before repository call."""
        # Arrange
        fund_id = 1
        with patch('src.entity.repositories.entity_repository.EntityRepository') as mock_entity_repo_class, \
             patch.object(mock_entity_repo_class.return_value, 'get_entity_by_id', return_value=mock_entity), \
             patch('src.fund.calculators.financial_year_calculator.FinancialYearCalculator.calculate_financial_year_dates', return_value=(date(2023, 7, 1), date(2024, 6, 30))), \
             patch.object(service.fund_tax_statement_repository, 'create_fund_tax_statement', return_value=mock_tax_statement) as mock_create_repo, \
             patch.object(service, '_create_daily_debt_cost_events', return_value=[]), \
             patch.object(service, '_create_tax_payment_events', return_value=[]), \
             patch.object(service.fund_event_repository, 'generate_group_id', return_value=1), \
             patch('src.fund.services.fund_event_secondary_service.FundEventSecondaryService'):
            
            # Act
            service.create_fund_tax_statement(fund_id, sample_tax_statement_data, mock_session)

            # Assert
            expected_data = sample_tax_statement_data.copy()
            expected_data['fund_id'] = fund_id
            expected_data['financial_year_start_date'] = date(2023, 7, 1)
            expected_data['financial_year_end_date'] = date(2024, 6, 30)
            mock_create_repo.assert_called_once()
            call_args = mock_create_repo.call_args[0][0]
            assert call_args['fund_id'] == fund_id
            assert call_args['financial_year_start_date'] == date(2023, 7, 1)
            assert call_args['financial_year_end_date'] == date(2024, 6, 30)

    ################################################################################
    # Test delete_fund_tax_statement method
    ################################################################################

    def test_delete_fund_tax_statement_successfully_deletes_statement(self, service, mock_session, mock_tax_statement):
        """Test successful tax statement deletion."""
        # Arrange
        statement_id = 1
        with patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statement_by_id', return_value=mock_tax_statement) as mock_get_statement, \
             patch.object(service.fund_validation_service, 'validate_fund_tax_statement_deletion', return_value={}) as mock_validate, \
             patch.object(service.fund_tax_statement_repository, 'delete_fund_tax_statement', return_value=True) as mock_delete:
            
            # Act
            result = service.delete_fund_tax_statement(statement_id, mock_session)

            # Assert
            assert result is True
            mock_get_statement.assert_called_once_with(statement_id, mock_session)
            mock_validate.assert_called_once_with(statement_id, mock_session)
            mock_delete.assert_called_once_with(statement_id, mock_session)

    def test_delete_fund_tax_statement_raises_error_when_statement_not_found(self, service, mock_session):
        """Test that delete_fund_tax_statement raises ValueError when statement not found."""
        # Arrange
        statement_id = 999
        with patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statement_by_id', return_value=None) as mock_get_statement:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Fund tax statement not found"):
                service.delete_fund_tax_statement(statement_id, mock_session)

    def test_delete_fund_tax_statement_raises_error_when_validation_fails(self, service, mock_session, mock_tax_statement):
        """Test that delete_fund_tax_statement raises ValueError when validation fails."""
        # Arrange
        statement_id = 1
        validation_errors = {'fund_events': ['Cannot delete with dependent events']}
        with patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statement_by_id', return_value=mock_tax_statement) as mock_get_statement, \
             patch.object(service.fund_validation_service, 'validate_fund_tax_statement_deletion', return_value=validation_errors) as mock_validate:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Deletion validation failed"):
                service.delete_fund_tax_statement(statement_id, mock_session)

    def test_delete_fund_tax_statement_raises_error_when_repository_fails(self, service, mock_session, mock_tax_statement):
        """Test that delete_fund_tax_statement raises ValueError when repository deletion fails."""
        # Arrange
        statement_id = 1
        with patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statement_by_id', return_value=mock_tax_statement) as mock_get_statement, \
             patch.object(service.fund_validation_service, 'validate_fund_tax_statement_deletion', return_value={}) as mock_validate, \
             patch.object(service.fund_tax_statement_repository, 'delete_fund_tax_statement', return_value=False) as mock_delete:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to delete fund tax statement"):
                service.delete_fund_tax_statement(statement_id, mock_session)

    ################################################################################
    # Test _create_interest_tax_payment method
    ################################################################################

    def test_create_interest_tax_payment_creates_event_when_conditions_met(self, service, mock_tax_statement):
        """Test that _create_interest_tax_payment creates event when conditions are met."""
        # Arrange
        mock_tax_statement.interest_income_tax_rate = 30.0
        mock_tax_statement.interest_income_amount = 10000.0
        mock_tax_statement.interest_non_resident_withholding_tax_from_statement = 1000.0
        mock_tax_statement.tax_payment_date = date(2024, 6, 30)
        mock_tax_statement.financial_year = '2023-2024'
        mock_tax_statement.id = 1

        # Act
        result = service._create_interest_tax_payment(mock_tax_statement)

        # Assert
        assert result is not None
        assert result['event_type'] == EventType.TAX_PAYMENT
        assert result['tax_payment_type'] == TaxPaymentType.EOFY_INTEREST_TAX
        assert result['amount'] == 2000.0  # (10000 * 0.3) - 1000
        assert result['fund_id'] == mock_tax_statement.fund_id
        assert result['tax_statement_id'] == 1

    def test_create_interest_tax_payment_returns_none_when_no_income(self, service, mock_tax_statement):
        """Test that _create_interest_tax_payment returns None when no income."""
        # Arrange
        mock_tax_statement.interest_income_tax_rate = 30.0
        mock_tax_statement.interest_income_amount = 0.0

        # Act
        result = service._create_interest_tax_payment(mock_tax_statement)

        # Assert
        assert result is None
        assert mock_tax_statement.interest_tax_amount == 0.0

    def test_create_interest_tax_payment_returns_none_when_no_tax_rate(self, service, mock_tax_statement):
        """Test that _create_interest_tax_payment returns None when no tax rate."""
        # Arrange
        mock_tax_statement.interest_income_tax_rate = 0.0
        mock_tax_statement.interest_income_amount = 10000.0

        # Act
        result = service._create_interest_tax_payment(mock_tax_statement)

        # Assert
        assert result is None
        assert mock_tax_statement.interest_tax_amount == 0.0

    ################################################################################
    # Test _create_franked_dividend_tax_payment method
    ################################################################################

    def test_create_franked_dividend_tax_payment_creates_event_when_conditions_met(self, service, mock_session, mock_tax_statement):
        """Test that _create_franked_dividend_tax_payment creates event when conditions are met."""
        # Arrange
        mock_tax_statement.dividend_franked_income_tax_rate = 15.0
        mock_tax_statement.dividend_franked_income_amount = 5000.0
        mock_tax_statement.tax_payment_date = date(2024, 6, 30)
        mock_tax_statement.financial_year = '2023-2024'
        mock_tax_statement.id = 1

        # Act
        result = service._create_franked_dividend_tax_payment(mock_tax_statement, mock_session)

        # Assert
        assert result is not None
        assert result['event_type'] == EventType.TAX_PAYMENT
        assert result['tax_payment_type'] == TaxPaymentType.DIVIDENDS_FRANKED_TAX
        assert result['amount'] == 750.0  # 5000 * 0.15
        assert result['fund_id'] == mock_tax_statement.fund_id
        assert result['tax_statement_id'] == 1

    def test_create_franked_dividend_tax_payment_calculates_from_events_when_amount_none(self, service, mock_session, mock_tax_statement):
        """Test that _create_franked_dividend_tax_payment calculates amount from events when amount is None."""
        # Arrange
        mock_tax_statement.dividend_franked_income_amount = None
        mock_tax_statement.dividend_franked_income_tax_rate = 15.0
        mock_tax_statement.tax_payment_date = date(2024, 6, 30)
        mock_tax_statement.financial_year = '2023-2024'
        mock_tax_statement.id = 1
        mock_tax_statement.financial_year_start_date = date(2023, 7, 1)
        mock_tax_statement.financial_year_end_date = date(2024, 6, 30)

        # Mock fund events
        mock_events = [
            FundEventFactory.build(amount=2000.0),
            FundEventFactory.build(amount=3000.0)
        ]
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_events) as mock_get_events:
            # Act
            result = service._create_franked_dividend_tax_payment(mock_tax_statement, mock_session)

            # Assert
            assert result is not None
            assert result['amount'] == 750.0  # (2000 + 3000) * 0.15
            assert mock_tax_statement.dividend_franked_income_amount == 5000.0
            assert mock_tax_statement.dividend_franked_income_amount_from_tax_statement_flag is False
            mock_get_events.assert_called_once_with(
                fund_ids=[mock_tax_statement.fund_id],
                distribution_types=[DistributionType.DIVIDEND_FRANKED],
                start_event_date=date(2023, 7, 1),
                end_event_date=date(2024, 6, 30),
                session=mock_session
            )

    ################################################################################
    # Test _create_unfranked_dividend_tax_payment method
    ################################################################################

    def test_create_unfranked_dividend_tax_payment_creates_event_when_conditions_met(self, service, mock_session, mock_tax_statement):
        """Test that _create_unfranked_dividend_tax_payment creates event when conditions are met."""
        # Arrange
        mock_tax_statement.dividend_unfranked_income_tax_rate = 30.0
        mock_tax_statement.dividend_unfranked_income_amount = 3000.0
        mock_tax_statement.tax_payment_date = date(2024, 6, 30)
        mock_tax_statement.financial_year = '2023-2024'
        mock_tax_statement.id = 1

        # Act
        result = service._create_unfranked_dividend_tax_payment(mock_tax_statement, mock_session)

        # Assert
        assert result is not None
        assert result['event_type'] == EventType.TAX_PAYMENT
        assert result['tax_payment_type'] == TaxPaymentType.DIVIDENDS_UNFRANKED_TAX
        assert result['amount'] == 900.0  # 3000 * 0.30
        assert result['fund_id'] == mock_tax_statement.fund_id
        assert result['tax_statement_id'] == 1

    ################################################################################
    # Test _create_capital_gain_tax_payment method
    ################################################################################

    def test_create_capital_gain_tax_payment_creates_event_for_nav_based_fund(self, service, mock_session, mock_tax_statement, mock_fund):
        """Test that _create_capital_gain_tax_payment creates event for NAV-based fund."""
        # Arrange
        mock_tax_statement.capital_gain_income_amount = None
        mock_tax_statement.financial_year_start_date = date(2023, 7, 1)
        mock_tax_statement.financial_year_end_date = date(2024, 6, 30)
        mock_tax_statement.tax_payment_date = date(2024, 6, 30)
        mock_tax_statement.financial_year = '2023-2024'
        mock_tax_statement.id = 1
        mock_fund.tracking_type = FundTrackingType.NAV_BASED

        # Mock fund events and capital gains calculation
        mock_events = [FundEventFactory.build()]
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund), \
             patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_events), \
             patch('src.fund.calculators.fifo_capital_gains_calculator.FifoCapitalGainsCalculator') as mock_calc_class, \
             patch.object(mock_calc_class.return_value, 'calculate_capital_gains', return_value=Mock(total_capital_gains=1000.0)):
            
            # Act
            result = service._create_capital_gain_tax_payment(mock_tax_statement, mock_session)

            # Assert
            assert result is not None
            assert result['event_type'] == EventType.TAX_PAYMENT
            assert result['tax_payment_type'] == TaxPaymentType.CAPITAL_GAINS_TAX
            assert result['amount'] == 1000.0
            assert mock_tax_statement.capital_gain_income_amount == 1000.0
            assert mock_tax_statement.capital_gain_income_amount_from_tax_statement_flag is False

    def test_create_capital_gain_tax_payment_returns_none_for_cost_based_fund(self, service, mock_session, mock_tax_statement, mock_fund):
        """Test that _create_capital_gain_tax_payment returns None for cost-based fund."""
        # Arrange
        mock_tax_statement.capital_gain_income_amount = None
        mock_fund.tracking_type = FundTrackingType.COST_BASED

        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund):
            
            # Act
            result = service._create_capital_gain_tax_payment(mock_tax_statement, mock_session)

            # Assert
            assert result is None

    def test_create_capital_gain_tax_payment_uses_provided_amount(self, service, mock_session, mock_tax_statement):
        """Test that _create_capital_gain_tax_payment uses provided amount when available."""
        # Arrange
        mock_tax_statement.capital_gain_income_amount = 2000.0
        mock_tax_statement.tax_payment_date = date(2024, 6, 30)
        mock_tax_statement.financial_year = '2023-2024'
        mock_tax_statement.id = 1

        # Act
        result = service._create_capital_gain_tax_payment(mock_tax_statement, mock_session)

        # Assert
        assert result is not None
        assert result['amount'] == 2000.0
        assert mock_tax_statement.capital_gain_income_amount_from_tax_statement_flag is True

    ################################################################################
    # Test _create_eofy_debt_cost_event method
    ################################################################################

    def test_create_eofy_debt_cost_event_creates_event_when_benefit_positive(self, service, mock_session, mock_tax_statement):
        """Test that _create_eofy_debt_cost_event creates event when tax benefit is positive."""
        # Arrange
        mock_tax_statement.financial_year_start_date = date(2023, 7, 1)
        mock_tax_statement.financial_year_end_date = date(2024, 6, 30)
        mock_tax_statement.tax_payment_date = date(2024, 6, 30)
        mock_tax_statement.financial_year = '2023-2024'
        mock_tax_statement.id = 1
        mock_tax_statement.eofy_debt_interest_deduction_rate = 30.0

        # Mock daily debt cost events
        mock_events = [
            FundEventFactory.build(amount=1000.0),
            FundEventFactory.build(amount=2000.0)
        ]
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_events) as mock_get_events:
            # Act
            result = service._create_eofy_debt_cost_event(mock_tax_statement, mock_session)

            # Assert
            assert result is not None
            assert result['event_type'] == EventType.TAX_PAYMENT
            assert result['tax_payment_type'] == TaxPaymentType.EOFY_INTEREST_TAX
            assert result['amount'] == 900.0  # (1000 + 2000) * 0.30
            assert mock_tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest == 3000.0
            assert mock_tax_statement.eofy_debt_interest_deduction_total_deduction == 900.0

    def test_create_eofy_debt_cost_event_returns_none_when_no_benefit(self, service, mock_session, mock_tax_statement):
        """Test that _create_eofy_debt_cost_event returns None when no tax benefit."""
        # Arrange
        mock_tax_statement.financial_year_start_date = date(2023, 7, 1)
        mock_tax_statement.financial_year_end_date = date(2024, 6, 30)
        mock_tax_statement.eofy_debt_interest_deduction_rate = 30.0

        # Mock no daily debt cost events
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_get_events:
            # Act
            result = service._create_eofy_debt_cost_event(mock_tax_statement, mock_session)

            # Assert
            assert result is None
            assert mock_tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest == 0.0
            assert mock_tax_statement.eofy_debt_interest_deduction_total_deduction == 0.0


    ################################################################################
    # Test _create_tax_payment_events method
    ################################################################################

    def test_create_tax_payment_events_creates_all_event_types(self, service, mock_session, mock_tax_statement):
        """Test that _create_tax_payment_events creates all applicable event types."""
        # Arrange
        mock_tax_statement.interest_income_tax_rate = 30.0
        mock_tax_statement.interest_income_amount = 1000.0
        mock_tax_statement.dividend_franked_income_tax_rate = 15.0
        mock_tax_statement.dividend_franked_income_amount = 500.0
        mock_tax_statement.dividend_unfranked_income_tax_rate = 30.0
        mock_tax_statement.dividend_unfranked_income_amount = 300.0
        mock_tax_statement.capital_gain_income_amount = 200.0
        mock_tax_statement.eofy_debt_interest_deduction_rate = 30.0
        mock_tax_statement.tax_payment_date = date(2024, 6, 30)
        mock_tax_statement.financial_year = '2023-2024'
        mock_tax_statement.id = 1

        # Mock all private methods to return event data
        with patch.object(service, '_create_interest_tax_payment', return_value={'event': 'interest'}) as mock_interest, \
             patch.object(service, '_create_franked_dividend_tax_payment', return_value={'event': 'franked'}) as mock_franked, \
             patch.object(service, '_create_unfranked_dividend_tax_payment', return_value={'event': 'unfranked'}) as mock_unfranked, \
             patch.object(service, '_create_capital_gain_tax_payment', return_value={'event': 'capital_gain'}) as mock_capital_gain, \
             patch.object(service, '_create_eofy_debt_cost_event', return_value={'event': 'debt_cost'}) as mock_debt_cost:
            
            # Act
            result = service._create_tax_payment_events(mock_tax_statement, mock_session)

            # Assert
            assert len(result) == 5
            assert {'event': 'interest'} in result
            assert {'event': 'franked'} in result
            assert {'event': 'unfranked'} in result
            assert {'event': 'capital_gain'} in result
            assert {'event': 'debt_cost'} in result

    def test_create_tax_payment_events_skips_none_events(self, service, mock_session, mock_tax_statement):
        """Test that _create_tax_payment_events skips None events."""
        # Arrange
        mock_tax_statement.interest_income_tax_rate = 0.0  # No interest tax
        mock_tax_statement.dividend_franked_income_tax_rate = 15.0
        mock_tax_statement.dividend_franked_income_amount = 500.0
        mock_tax_statement.dividend_unfranked_income_tax_rate = 0.0  # No unfranked tax
        mock_tax_statement.capital_gain_income_amount = 0.0  # No capital gains
        mock_tax_statement.eofy_debt_interest_deduction_rate = 0.0  # No debt cost

        # Mock private methods to return None for most
        with patch.object(service, '_create_interest_tax_payment', return_value=None) as mock_interest, \
             patch.object(service, '_create_franked_dividend_tax_payment', return_value={'event': 'franked'}) as mock_franked, \
             patch.object(service, '_create_unfranked_dividend_tax_payment', return_value=None) as mock_unfranked, \
             patch.object(service, '_create_capital_gain_tax_payment', return_value=None) as mock_capital_gain, \
             patch.object(service, '_create_eofy_debt_cost_event', return_value=None) as mock_debt_cost:
            
            # Act
            result = service._create_tax_payment_events(mock_tax_statement, mock_session)

            # Assert
            assert len(result) == 1
            assert {'event': 'franked'} in result

    ################################################################################
    # Test edge cases and error conditions
    ################################################################################

    def test_create_franked_dividend_tax_payment_handles_zero_amount(self, service, mock_session, mock_tax_statement):
        """Test that _create_franked_dividend_tax_payment handles zero amount correctly."""
        # Arrange
        mock_tax_statement.dividend_franked_income_amount = 0.0
        mock_tax_statement.dividend_franked_income_tax_rate = 15.0
        mock_tax_statement.financial_year_start_date = date(2023, 7, 1)
        mock_tax_statement.financial_year_end_date = date(2024, 6, 30)

        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]):
            # Act
            result = service._create_franked_dividend_tax_payment(mock_tax_statement, mock_session)

            # Assert
            assert result is None
            assert mock_tax_statement.dividend_franked_tax_amount == 0.0

    def test_create_unfranked_dividend_tax_payment_handles_zero_amount(self, service, mock_session, mock_tax_statement):
        """Test that _create_unfranked_dividend_tax_payment handles zero amount correctly."""
        # Arrange
        mock_tax_statement.dividend_unfranked_income_amount = 0.0
        mock_tax_statement.dividend_unfranked_income_tax_rate = 30.0
        mock_tax_statement.financial_year_start_date = date(2023, 7, 1)
        mock_tax_statement.financial_year_end_date = date(2024, 6, 30)

        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]):
            # Act
            result = service._create_unfranked_dividend_tax_payment(mock_tax_statement, mock_session)

            # Assert
            assert result is None
            assert mock_tax_statement.dividend_unfranked_tax_amount == 0.0

    def test_create_capital_gain_tax_payment_handles_zero_gains(self, service, mock_session, mock_tax_statement):
        """Test that _create_capital_gain_tax_payment handles zero capital gains."""
        # Arrange
        mock_tax_statement.capital_gain_income_amount = 0.0

        # Act
        result = service._create_capital_gain_tax_payment(mock_tax_statement, mock_session)

        # Assert
        assert result is None

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.fund_tax_statement_repository is not None
        assert service.fund_event_repository is not None
        assert service.fund_validation_service is not None
        assert hasattr(service, 'fund_tax_statement_repository')
        assert hasattr(service, 'fund_event_repository')
        assert hasattr(service, 'fund_validation_service')
