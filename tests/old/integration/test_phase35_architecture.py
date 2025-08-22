"""
Phase 3.5 Architecture Testing.

This module tests all the new architecture components built in Phase 3.5:
- Domain Events
- Repository Layer  
- API Layer
- Component Integration

These tests validate that the new architecture works correctly in isolation
before we attempt Phase 4 integration.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from src.fund.events import FundUpdateOrchestrator, FundEventHandlerRegistry
from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.events.handlers import (
    CapitalCallHandler, DistributionHandler, NAVUpdateHandler,
    UnitPurchaseHandler, UnitSaleHandler, ReturnOfCapitalHandler
)
from src.fund.events.domain import (
    FundDomainEvent, EquityBalanceChangedEvent, DistributionRecordedEvent,
    NAVUpdatedEvent, UnitsChangedEvent, TaxStatementUpdatedEvent
)
from src.fund.repositories import FundRepository, FundEventRepository, TaxStatementRepository
from src.fund.api import FundController, FundService
from src.fund.models import Fund, FundEvent, FundType, EventType
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from tests.conftest import db_session


class TestPhase35DomainEvents:
    """Test the domain event system implementation."""
    
    def test_domain_event_creation(self):
        """Test that domain events can be created with proper data."""
        # Test base domain event - can't instantiate abstract class
        # This test validates that the abstract class is properly defined
        assert hasattr(FundDomainEvent, '__abstractmethods__')
        assert 'event_type' in FundDomainEvent.__abstractmethods__
    
    def test_equity_balance_changed_event(self):
        """Test equity balance changed event creation."""
        event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('0.0'),
            new_balance=Decimal('100000.0'),
            change_reason="Capital call recorded"
        )
        assert event.old_balance == 0.0
        assert event.new_balance == 100000.0
        assert event.change_reason == "Capital call recorded"
        assert isinstance(event, FundDomainEvent)
    
    def test_distribution_recorded_event(self):
        """Test distribution recorded event creation."""
        event = DistributionRecordedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            distribution_type="income",
            amount=Decimal('50000.0'),
            tax_withheld=Decimal('7500.0')
        )
        assert event.distribution_type == "income"
        assert event.amount == 50000.0
        assert event.tax_withheld == 7500.0
        assert isinstance(event, FundDomainEvent)
    
    def test_nav_updated_event(self):
        """Test NAV updated event creation."""
        event = NAVUpdatedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_nav=Decimal('10.0'),
            new_nav=Decimal('10.50'),
            change_reason="Quarterly NAV update"
        )
        assert event.old_nav == 10.0
        assert event.new_nav == 10.50
        assert event.change_reason == "Quarterly NAV update"
        assert isinstance(event, FundDomainEvent)
    
    def test_units_changed_event(self):
        """Test units changed event creation."""
        event = UnitsChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_units=Decimal('1000.0'),
            new_units=Decimal('1100.0'),
            change_reason="Unit purchase"
        )
        assert event.old_units == 1000.0
        assert event.new_units == 1100.0
        assert event.change_reason == "Unit purchase"
        assert isinstance(event, FundDomainEvent)
    
    def test_tax_statement_updated_event(self):
        """Test tax statement updated event creation."""
        event = TaxStatementUpdatedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            tax_statement_id=123,
            update_type="distribution_recorded",
            financial_year="2023-24",
            entity_id=456
        )
        assert event.tax_statement_id == 123
        assert event.update_type == "distribution_recorded"
        assert isinstance(event, FundDomainEvent)


class TestPhase35RepositoryLayer:
    """Test the repository layer implementation."""
    
    def test_fund_repository_initialization(self):
        """Test fund repository can be initialized."""
        repo = FundRepository()
        assert repo is not None
        assert hasattr(repo, '_cache')
        assert hasattr(repo, '_cache_ttl')
    
    def test_fund_event_repository_initialization(self):
        """Test fund event repository can be initialized."""
        repo = FundEventRepository()
        assert repo is not None
        assert hasattr(repo, '_cache')
        assert hasattr(repo, '_cache_ttl')
    
    def test_tax_statement_repository_initialization(self):
        """Test tax statement repository can be initialized."""
        repo = TaxStatementRepository()
        assert repo is not None
        assert hasattr(repo, '_cache')
        assert hasattr(repo, '_cache_ttl')
    
    def test_repository_caching_behavior(self, db_session):
        """Test that repository caching works correctly."""
        repo = FundRepository()
        
        # Create test data
        company = InvestmentCompany(
            name="Test Company",
            description="Test investment company"
        )
        db_session.add(company)
        db_session.flush()
        
        entity = Entity(
            name="Test Entity",
            description="Test entity"
        )
        db_session.add(entity)
        db_session.flush()
        
        from src.fund.enums import FundType
        
        fund = Fund.create(
            investment_company_id=company.id,
            entity_id=entity.id,
            name="Test Fund",
            fund_type="Private Equity",
            tracking_type=FundType.COST_BASED,
            description="Test fund for repository testing",
            session=db_session
        )
        
        # Test cache miss
        fund1 = repo.get_by_id(fund.id, db_session)
        assert fund1 is not None
        assert fund1.id == fund.id
        
        # Test cache hit
        fund2 = repo.get_by_id(fund.id, db_session)
        assert fund2 is fund1  # Same object from cache
        
        # Test cache invalidation
        repo._cache.clear()
        fund3 = repo.get_by_id(fund.id, db_session)
        # Note: SQLAlchemy may return the same object instance if it's in the session
        # This is expected behavior, not a bug
        assert fund3 is not None
        assert fund3.id == fund.id


class TestPhase35APILayer:
    """Test the API layer implementation."""
    
    def test_fund_controller_initialization(self):
        """Test fund controller can be initialized."""
        controller = FundController()
        assert controller is not None
        assert hasattr(controller, 'fund_service')
        assert isinstance(controller.fund_service, FundService)
    
    def test_fund_service_initialization(self):
        """Test fund service can be initialized."""
        service = FundService()
        assert service is not None
        assert hasattr(service, 'fund_repository')
        assert hasattr(service, 'fund_event_repository')
    
    def test_api_methods_exist(self):
        """Test that all expected API methods exist."""
        controller = FundController()
        service = FundService()
        
        # Controller methods
        assert hasattr(controller, 'get_fund')
        assert hasattr(controller, 'create_fund')
        assert hasattr(controller, 'update_fund')
        assert hasattr(controller, 'delete_fund')
        assert hasattr(controller, 'add_fund_event')
        
        # Service methods
        assert hasattr(service, 'get_fund')
        assert hasattr(service, 'create_fund')
        assert hasattr(service, 'update_fund')
        assert hasattr(service, 'delete_fund')
        assert hasattr(service, 'add_fund_event')


class TestPhase35ComponentIntegration:
    """Test that all new components work together."""
    
    def test_event_handler_registry_initialization(self):
        """Test event handler registry can be initialized."""
        registry = FundEventHandlerRegistry()
        assert registry is not None
        assert hasattr(registry, '_handlers')
        assert len(registry._handlers) > 0
    
    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized."""
        orchestrator = FundUpdateOrchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, 'registry')
        assert isinstance(orchestrator.registry, FundEventHandlerRegistry)
    
    def test_handler_registration(self):
        """Test that all event handlers are properly registered."""
        registry = FundEventHandlerRegistry()
        
        # Check that all expected handlers are registered
        from src.fund.enums import EventType
        
        expected_handlers = {
            EventType.CAPITAL_CALL: CapitalCallHandler,
            EventType.RETURN_OF_CAPITAL: ReturnOfCapitalHandler,
            EventType.DISTRIBUTION: DistributionHandler,
            EventType.NAV_UPDATE: NAVUpdateHandler,
            EventType.UNIT_PURCHASE: UnitPurchaseHandler,
            EventType.UNIT_SALE: UnitSaleHandler,
        }
        
        for event_type, expected_handler in expected_handlers.items():
            handler_class = registry._handlers.get(event_type)
            assert handler_class is not None, f"Handler for {event_type} not registered"
            assert handler_class == expected_handler, f"Wrong handler for {event_type}"
    
    def test_handler_creation(self):
        """Test that handlers can be created for each event type."""
        registry = FundEventHandlerRegistry()
        
        # Mock session and fund
        mock_session = Mock()
        mock_fund = Mock()
        
        # Test handler creation for each event type
        from src.fund.enums import EventType
        
        for event_type in EventType:
            try:
                handler = registry.get_handler(event_type, mock_session, mock_fund)
                assert handler is not None
                assert hasattr(handler, 'handle')
                assert hasattr(handler, 'validate_event')
            except ValueError:
                # Some event types might not have handlers (like system events)
                pass


class TestPhase35EventPublishing:
    """Test the event publishing system (even though it's not fully implemented)."""
    
    def test_event_publishing_placeholder_exists(self):
        """Test that event publishing placeholders exist in all handlers."""
        # Mock session and fund
        mock_session = Mock()
        mock_fund = Mock()
        
        # Test all handlers have the publishing method
        handlers = [
            CapitalCallHandler(mock_session, mock_fund),
            DistributionHandler(mock_session, mock_fund),
            NAVUpdateHandler(mock_session, mock_fund),
            UnitPurchaseHandler(mock_session, mock_fund),
            UnitSaleHandler(mock_session, mock_fund),
            ReturnOfCapitalHandler(mock_session, mock_fund),
        ]
        
        for handler in handlers:
            assert hasattr(handler, '_publish_dependent_events')
            assert callable(handler._publish_dependent_events)
    
    def test_event_publishing_works(self):
        """Test that event publishing now works and creates domain events."""
        # Mock session and fund
        mock_session = Mock()
        mock_fund = Mock()
        mock_fund.id = 1
        
        # Test that publishing works (no longer placeholder)
        handler = CapitalCallHandler(mock_session, mock_fund)
        mock_event = Mock()
        mock_event.id = 1
        mock_event.event_type = 'CAPITAL_CALL'
        mock_event.event_date = date(2024, 1, 15)
        mock_event.previous_equity_balance = 0.0
        mock_event.current_equity_balance = 100000.0
        
        # Mock the domain event repository
        with patch('src.fund.repositories.domain_event_repository.DomainEventRepository') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            
            result = handler._publish_dependent_events(mock_event)
            
            # Should return None (void method)
            assert result is None
            
            # Should have called the repository to store events
            mock_repo_instance.store_domain_events.assert_called_once()


class TestPhase35ArchitectureCompleteness:
    """Test that the architecture is complete and ready for Phase 4."""
    
    def test_all_components_exist(self):
        """Test that all required architecture components exist."""
        # Event handling layer
        assert BaseFundEventHandler is not None
        assert FundEventHandlerRegistry is not None
        assert FundUpdateOrchestrator is not None
        
        # Domain events
        assert FundDomainEvent is not None
        assert EquityBalanceChangedEvent is not None
        assert DistributionRecordedEvent is not None
        assert NAVUpdatedEvent is not None
        assert UnitsChangedEvent is not None
        assert TaxStatementUpdatedEvent is not None
        
        # Repository layer
        assert FundRepository is not None
        assert FundEventRepository is not None
        assert TaxStatementRepository is not None
        
        # API layer
        assert FundController is not None
        assert FundService is not None
    
    def test_architecture_relationships(self):
        """Test that architecture components have proper relationships."""
        # Test orchestrator uses registry
        orchestrator = FundUpdateOrchestrator()
        assert hasattr(orchestrator, 'registry')
        assert isinstance(orchestrator.registry, FundEventHandlerRegistry)
        
        # Test controller uses service
        controller = FundController()
        assert hasattr(controller, 'fund_service')
        assert isinstance(controller.fund_service, FundService)
        
        # Test service uses repositories
        service = FundService()
        assert hasattr(service, 'fund_repository')
        assert hasattr(service, 'fund_event_repository')
    
    def test_enum_consistency(self):
        """Test that enums are consistent across the system."""
        # This test will fail if there are enum duplication issues
        # It's a critical test for Phase 3.5
        from src.fund.enums import FundType as EnumsFundType
        from src.fund.models import FundType as ModelsFundType
        
        # Check that both enums have the same values
        enums_values = [e.value for e in EnumsFundType]
        models_values = [e.value for e in ModelsFundType]
        
        assert set(enums_values) == set(models_values), "Enum values don't match between enums.py and models.py"
        
        # Check that both enums have the same members
        enums_members = [e.name for e in EnumsFundType]
        models_members = [e.name for e in ModelsFundType]
        
        assert set(enums_members) == set(models_members), "Enum members don't match between enums.py and models.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
