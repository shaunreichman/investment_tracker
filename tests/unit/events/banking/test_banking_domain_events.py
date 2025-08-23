"""
Test Banking Domain Events.

This module tests all 8 banking domain event classes:
- BankCreatedEvent
- BankUpdatedEvent  
- BankDeletedEvent
- BankAccountCreatedEvent
- BankAccountUpdatedEvent
- BankAccountDeletedEvent
- CurrencyChangedEvent
- AccountStatusChangedEvent

Each event is tested for:
- Proper initialization and validation
- Event type classification
- Metadata handling
- Serialization to dictionary
- Equality and comparison
- Business rule validation
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock

from src.banking.events.domain.base_event import BankingDomainEvent
from src.banking.events.domain.bank_created_event import BankCreatedEvent
from src.banking.events.domain.bank_updated_event import BankUpdatedEvent
from src.banking.events.domain.bank_deleted_event import BankDeletedEvent
from src.banking.events.domain.bank_account_created_event import BankAccountCreatedEvent
from src.banking.events.domain.bank_account_updated_event import BankAccountUpdatedEvent
from src.banking.events.domain.bank_account_deleted_event import BankAccountDeletedEvent
from src.banking.events.domain.currency_changed_event import CurrencyChangedEvent
from src.banking.events.domain.account_status_changed_event import AccountStatusChangedEvent


class TestBankingDomainEventBase:
    """Test base functionality for all banking domain events."""
    
    def test_base_event_initialization(self):
        """Test base event initialization with required parameters."""
        # Arrange
        entity_id = 123
        entity_type = "bank"
        event_date = date(2025, 1, 15)
        metadata = {"name": "Test Bank", "country": "US"}
        
        # Act - Create a concrete event class for testing
        class TestEvent(BankingDomainEvent):
            @property
            def event_type(self) -> str:
                return "test_event"
        
        event = TestEvent(entity_id, entity_type, event_date, metadata)
        
        # Assert
        assert event.banking_entity_id == entity_id
        assert event.entity_type == entity_type
        assert event.event_date == event_date
        assert event.metadata == metadata
        assert event.event_type == "test_event"
        assert isinstance(event.event_id, str)
        assert isinstance(event.timestamp, datetime)
    
    def test_base_event_initialization_without_metadata(self):
        """Test base event initialization without optional metadata."""
        # Arrange
        entity_id = 456
        entity_type = "bank_account"
        event_date = date(2025, 1, 16)
        
        # Act
        class TestEvent(BankingDomainEvent):
            @property
            def event_type(self) -> str:
                return "test_event"
        
        event = TestEvent(entity_id, entity_type, event_date)
        
        # Assert
        assert event.banking_entity_id == entity_id
        assert event.entity_type == entity_type
        assert event.event_date == event_date
        assert event.metadata == {}
    
    def test_base_event_serialization(self):
        """Test event serialization to dictionary format."""
        # Arrange
        entity_id = 789
        entity_type = "bank"
        event_date = date(2025, 1, 17)
        metadata = {"swift_bic": "TESTUS33"}
        
        class TestEvent(BankingDomainEvent):
            @property
            def event_type(self) -> str:
                return "test_event"
        
        event = TestEvent(entity_id, entity_type, event_date, metadata)
        
        # Act
        event_dict = event.to_dict()
        
        # Assert
        assert event_dict['event_id'] == event.event_id
        assert event_dict['event_type'] == "test_event"
        assert event_dict['banking_entity_id'] == entity_id
        assert event_dict['entity_type'] == entity_type
        assert event_dict['event_date'] == event_date.isoformat()
        assert event_dict['timestamp'] == event.timestamp.isoformat()
        assert event_dict['metadata'] == metadata
    
    def test_base_event_equality(self):
        """Test event equality based on event_id."""
        # Arrange
        entity_id = 100
        entity_type = "bank"
        event_date = date(2025, 1, 18)
        
        class TestEvent(BankingDomainEvent):
            @property
            def event_type(self) -> str:
                return "test_event"
        
        event1 = TestEvent(entity_id, entity_type, event_date)
        event2 = TestEvent(entity_id, entity_type, event_date)
        
        # Act & Assert
        # Events with different IDs should not be equal
        assert event1 != event2
        
        # Events should equal themselves
        assert event1 == event1
        assert event2 == event2
    
    def test_base_event_repr(self):
        """Test event string representation."""
        # Arrange
        entity_id = 200
        entity_type = "bank_account"
        event_date = date(2025, 1, 19)
        
        class TestEvent(BankingDomainEvent):
            @property
            def event_type(self) -> str:
                return "test_event"
        
        event = TestEvent(entity_id, entity_type, event_date)
        
        # Act
        repr_str = repr(event)
        
        # Assert
        assert "TestEvent" in repr_str
        assert str(entity_id) in repr_str
        assert entity_type in repr_str
        assert str(event_date) in repr_str
        assert "test_event" in repr_str


class TestBankCreatedEvent:
    """Test BankCreatedEvent functionality."""
    
    def test_bank_created_event_initialization(self):
        """Test bank created event initialization."""
        # Arrange
        bank_id = 300
        event_date = date(2025, 1, 20)
        metadata = {"name": "New Bank", "country": "CA"}
        
        # Act
        event = BankCreatedEvent(bank_id, event_date, metadata)
        
        # Assert
        assert event.banking_entity_id == bank_id
        assert event.entity_type == "bank"
        assert event.event_date == event_date
        assert event.metadata == metadata
        assert event.event_type == "bank_created"
    
    def test_bank_created_event_default_metadata(self):
        """Test bank created event with default metadata."""
        # Arrange
        bank_id = 301
        event_date = date(2025, 1, 21)
        
        # Act
        event = BankCreatedEvent(bank_id, event_date)
        
        # Assert
        assert event.banking_entity_id == bank_id
        assert event.entity_type == "bank"
        assert event.event_date == event_date
        assert event.metadata == {}
        assert event.event_type == "bank_created"


class TestBankUpdatedEvent:
    """Test BankUpdatedEvent functionality."""
    
    def test_bank_updated_event_initialization(self):
        """Test bank updated event initialization."""
        # Arrange
        bank_id = 400
        event_date = date(2025, 1, 22)
        metadata = {"updated_fields": ["name", "swift_bic"], "old_values": {"name": "Old Bank"}}
        
        # Act
        event = BankUpdatedEvent(bank_id, event_date, metadata)
        
        # Assert
        assert event.banking_entity_id == bank_id
        assert event.entity_type == "bank"
        assert event.event_date == event_date
        assert event.metadata == metadata
        assert event.event_type == "bank_updated"


class TestBankDeletedEvent:
    """Test BankDeletedEvent functionality."""
    
    def test_bank_deleted_event_initialization(self):
        """Test bank deleted event initialization."""
        # Arrange
        bank_id = 500
        event_date = date(2025, 1, 23)
        metadata = {"deletion_reason": "Merger", "deleted_by": "admin"}
        
        # Act
        event = BankDeletedEvent(bank_id, event_date, metadata)
        
        # Assert
        assert event.banking_entity_id == bank_id
        assert event.entity_type == "bank"
        assert event.event_date == event_date
        assert event.metadata == metadata
        assert event.event_type == "bank_deleted"


class TestBankAccountCreatedEvent:
    """Test BankAccountCreatedEvent functionality."""
    
    def test_bank_account_created_event_initialization(self):
        """Test bank account created event initialization."""
        # Arrange
        account_id = 600
        event_date = date(2025, 1, 24)
        metadata = {"account_number": "1234567890", "currency": "USD", "bank_id": 100}
        
        # Act
        event = BankAccountCreatedEvent(account_id, event_date, metadata)
        
        # Assert
        assert event.banking_entity_id == account_id
        assert event.entity_type == "bank_account"
        assert event.event_date == event_date
        assert event.metadata == metadata
        assert event.event_type == "bank_account_created"


class TestBankAccountUpdatedEvent:
    """Test BankAccountUpdatedEvent functionality."""
    
    def test_bank_account_updated_event_initialization(self):
        """Test bank account updated event initialization."""
        # Arrange
        account_id = 700
        event_date = date(2025, 1, 25)
        metadata = {"updated_fields": ["balance", "status"], "old_balance": 10000.00}
        
        # Act
        event = BankAccountUpdatedEvent(account_id, event_date, metadata)
        
        # Assert
        assert event.banking_entity_id == account_id
        assert event.entity_type == "bank_account"
        assert event.event_date == event_date
        assert event.metadata == metadata
        assert event.event_type == "bank_account_updated"


class TestBankAccountDeletedEvent:
    """Test BankAccountDeletedEvent functionality."""
    
    def test_bank_account_deleted_event_initialization(self):
        """Test bank account deleted event initialization."""
        # Arrange
        account_id = 800
        event_date = date(2025, 1, 26)
        metadata = {"deletion_reason": "Account closed", "final_balance": 0.00}
        
        # Act
        event = BankAccountDeletedEvent(account_id, event_date, metadata)
        
        # Assert
        assert event.banking_entity_id == account_id
        assert event.entity_type == "bank_account"
        assert event.event_date == event_date
        assert event.metadata == metadata
        assert event.event_type == "bank_account_deleted"


class TestCurrencyChangedEvent:
    """Test CurrencyChangedEvent functionality."""
    
    def test_currency_changed_event_initialization(self):
        """Test currency changed event initialization."""
        # Arrange
        account_id = 900
        event_date = date(2025, 1, 27)
        old_currency = "USD"
        new_currency = "EUR"
        metadata = {"exchange_rate": 0.85}
        
        # Act
        event = CurrencyChangedEvent(account_id, event_date, old_currency, new_currency, metadata)
        
        # Assert
        assert event.banking_entity_id == account_id
        assert event.entity_type == "bank_account"
        assert event.event_date == event_date
        assert event.old_currency == old_currency
        assert event.new_currency == new_currency
        assert event.metadata["exchange_rate"] == 0.85
        assert event.event_type == "currency_changed"
    
    def test_currency_changed_event_required_metadata(self):
        """Test currency changed event with required metadata fields."""
        # Arrange
        account_id = 901
        event_date = date(2025, 1, 28)
        old_currency = "GBP"
        new_currency = "USD"
        
        # Act
        event = CurrencyChangedEvent(account_id, event_date, old_currency, new_currency)
        
        # Assert
        assert event.old_currency == old_currency
        assert event.new_currency == new_currency
        assert "exchange_rate" not in event.metadata  # Optional field


class TestAccountStatusChangedEvent:
    """Test AccountStatusChangedEvent functionality."""
    
    def test_account_status_changed_event_initialization(self):
        """Test account status changed event initialization."""
        # Arrange
        account_id = 1000
        event_date = date(2025, 1, 29)
        old_status = True
        new_status = False
        metadata = {"reason": "Compliance review"}
        
        # Act
        event = AccountStatusChangedEvent(account_id, event_date, old_status, new_status, metadata)
        
        # Assert
        assert event.banking_entity_id == account_id
        assert event.entity_type == "bank_account"
        assert event.event_date == event_date
        assert event.old_status == old_status
        assert event.new_status == new_status
        assert event.metadata["reason"] == "Compliance review"
        assert event.event_type == "account_status_changed"
    
    def test_account_status_changed_event_status_transitions(self):
        """Test account status changed event with different status transitions."""
        # Arrange
        account_id = 1001
        event_date = date(2025, 1, 30)
        
        # Test various status transitions (True = active, False = inactive)
        status_transitions = [
            (True, False),   # active -> suspended
            (False, True),   # suspended -> active
            (True, False),   # active -> closed
            (False, True)    # pending -> active
        ]
        
        for old_status, new_status in status_transitions:
            # Act
            event = AccountStatusChangedEvent(account_id, event_date, old_status, new_status)
            
            # Assert
            assert event.old_status == old_status
            assert event.new_status == new_status


class TestBankingDomainEventIntegration:
    """Test integration between different banking domain events."""
    
    def test_event_sequence_ordering(self):
        """Test that events can be properly ordered by timestamp."""
        # Arrange
        base_date = date(2025, 1, 15)
        events = []
        
        # Create events in sequence
        events.append(BankCreatedEvent(1, base_date, {"name": "Bank 1"}))
        events.append(BankAccountCreatedEvent(1, base_date, {"account_number": "123"}))
        events.append(BankAccountUpdatedEvent(1, base_date, {"balance": 1000}))
        
        # Act - Sort by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        # Assert
        assert len(sorted_events) == 3
        assert sorted_events[0].event_type == "bank_created"
        assert sorted_events[1].event_type == "bank_account_created"
        assert sorted_events[2].event_type == "bank_account_updated"
    
    def test_event_metadata_consistency(self):
        """Test that event metadata maintains consistency across related events."""
        # Arrange
        bank_id = 2000
        account_id = 2001
        event_date = date(2025, 1, 31)
        
        # Create related events
        bank_event = BankCreatedEvent(bank_id, event_date, {"name": "Test Bank", "country": "US"})
        account_event = BankAccountCreatedEvent(account_id, event_date, {"bank_id": bank_id, "currency": "USD"})
        
        # Act & Assert
        # Bank event should contain bank details
        assert bank_event.metadata["name"] == "Test Bank"
        assert bank_event.metadata["country"] == "US"
        
        # Account event should reference the bank
        assert account_event.metadata["bank_id"] == bank_id
        assert account_event.metadata["currency"] == "USD"
    
    def test_event_type_uniqueness(self):
        """Test that all event types are unique and properly identified."""
        # Arrange
        event_date = date(2025, 2, 1)
        entity_id = 3000
        
        # Create all event types
        event_types = [
            BankCreatedEvent(entity_id, event_date),
            BankUpdatedEvent(entity_id, event_date),
            BankDeletedEvent(entity_id, event_date),
            BankAccountCreatedEvent(entity_id, event_date),
            BankAccountUpdatedEvent(entity_id, event_date),
            BankAccountDeletedEvent(entity_id, event_date),
            CurrencyChangedEvent(entity_id, event_date, "USD", "EUR"),
            AccountStatusChangedEvent(entity_id, event_date, True, False)
        ]
        
        # Act
        unique_types = set(event.event_type for event in event_types)
        
        # Assert
        assert len(unique_types) == 8  # All 8 event types should be unique
        assert "bank_created" in unique_types
        assert "bank_updated" in unique_types
        assert "bank_deleted" in unique_types
        assert "bank_account_created" in unique_types
        assert "bank_account_updated" in unique_types
        assert "bank_account_deleted" in unique_types
        assert "currency_changed" in unique_types
        assert "account_status_changed" in unique_types
