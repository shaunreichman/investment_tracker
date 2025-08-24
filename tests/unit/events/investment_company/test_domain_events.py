"""
Test Investment Company Domain Events.

This module tests all domain event classes to ensure they properly
implement the event contract and maintain data integrity.

Key testing areas:
- Event creation and initialization
- Event type classification
- Event serialization and representation
- Event equality and comparison
- Event metadata handling
- Event validation and constraints

Testing Approach: Unit Tests with Mock Data
Reasoning: Domain events should be tested in isolation for fast execution and focused validation
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime
from decimal import Decimal

from src.investment_company.events.domain import (
    CompanyDomainEvent,
    CompanyCreatedEvent,
    CompanyUpdatedEvent,
    CompanyDeletedEvent,
    ContactAddedEvent,
    ContactUpdatedEvent,
    PortfolioUpdatedEvent
)
from src.investment_company.enums import CompanyDomainEventType, CompanyType


class TestCompanyDomainEvent:
    """Test the base CompanyDomainEvent class functionality."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.company_id = 1
        self.event_date = date(2024, 1, 15)
        self.metadata = {'source': 'test', 'version': '1.0'}
    
    def test_base_event_abstract_class(self):
        """Test that CompanyDomainEvent is properly abstract."""
        # Cannot instantiate abstract base class directly
        # This test verifies the class is properly abstract
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            CompanyDomainEvent(self.company_id, self.event_date)


class TestCompanyCreatedEvent:
    """Test the CompanyCreatedEvent class."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.company_id = 1
        self.event_date = date(2024, 1, 15)
        self.company_name = "Test Investment Company"
        self.company_type = CompanyType.PRIVATE_EQUITY
        self.metadata = {'source': 'test'}
    
    def test_company_created_event_creation(self):
        """Test company created event creation."""
        event = CompanyCreatedEvent(
            self.company_id,
            self.event_date,
            self.company_name,
            self.company_type,
            self.metadata
        )
        
        assert event.company_id == 1
        assert event.event_date == date(2024, 1, 15)
        assert event.company_name == "Test Investment Company"
        assert event.company_type == CompanyType.PRIVATE_EQUITY
        assert event.metadata['source'] == 'test'
        assert event.metadata['company_name'] == "Test Investment Company"
        assert event.metadata['company_type'] == CompanyType.PRIVATE_EQUITY
    
    def test_company_created_event_no_company_type(self):
        """Test company created event without company type."""
        event = CompanyCreatedEvent(
            self.company_id,
            self.event_date,
            self.company_name,
            metadata=self.metadata
        )
        
        assert event.company_type is None
        assert 'company_type' not in event.metadata
    
    def test_company_created_event_no_metadata(self):
        """Test company created event without metadata."""
        event = CompanyCreatedEvent(
            self.company_id,
            self.event_date,
            self.company_name,
            self.company_type
        )
        
        assert event.metadata == {
            'company_name': "Test Investment Company",
            'company_type': CompanyType.PRIVATE_EQUITY
        }
    
    def test_company_created_event_type(self):
        """Test company created event type property."""
        event = CompanyCreatedEvent(
            self.company_id,
            self.event_date,
            self.company_name,
            self.company_type
        )
        
        assert event.event_type == CompanyDomainEventType.COMPANY_CREATED
    
    def test_company_created_event_repr(self):
        """Test company created event string representation."""
        event = CompanyCreatedEvent(
            self.company_id,
            self.event_date,
            self.company_name,
            self.company_type
        )
        
        result = repr(event)
        
        assert 'CompanyCreatedEvent' in result
        assert 'company_id=1' in result
        assert "company_name='Test Investment Company'" in result
        assert 'event_date=2024-01-15' in result


class TestCompanyUpdatedEvent:
    """Test the CompanyUpdatedEvent class."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.company_id = 1
        self.event_date = date(2024, 1, 15)
        self.updated_fields = ['name', 'description']
        self.metadata = {'source': 'test'}
    
    def test_company_updated_event_creation(self):
        """Test company updated event creation."""
        event = CompanyUpdatedEvent(
            self.company_id,
            self.event_date,
            self.updated_fields,
            self.metadata
        )
        
        assert event.company_id == 1
        assert event.event_date == date(2024, 1, 15)
        assert event.updated_fields == ['name', 'description']
        assert event.metadata['source'] == 'test'
        assert event.metadata['updated_fields'] == ['name', 'description']
    
    def test_company_updated_event_type(self):
        """Test company updated event type property."""
        event = CompanyUpdatedEvent(
            self.company_id,
            self.event_date,
            self.updated_fields
        )
        
        assert event.event_type == CompanyDomainEventType.COMPANY_UPDATED


class TestCompanyDeletedEvent:
    """Test the CompanyDeletedEvent class."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.company_id = 1
        self.event_date = date(2024, 1, 15)
        self.company_name = "Test Company"
        self.metadata = {'source': 'test'}
    
    def test_company_deleted_event_creation(self):
        """Test company deleted event creation."""
        event = CompanyDeletedEvent(
            self.company_id,
            self.event_date,
            self.company_name,
            self.metadata
        )
        
        assert event.company_id == 1
        assert event.event_date == date(2024, 1, 15)
        assert event.company_name == "Test Company"
        assert event.metadata['source'] == 'test'
        assert event.metadata['company_name'] == "Test Company"
    
    def test_company_deleted_event_type(self):
        """Test company deleted event type property."""
        event = CompanyDeletedEvent(
            self.company_id,
            self.event_date,
            self.company_name
        )
        
        assert event.event_type == CompanyDomainEventType.COMPANY_DELETED


class TestContactAddedEvent:
    """Test the ContactAddedEvent class."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.company_id = 1
        self.event_date = date(2024, 1, 15)
        self.contact_id = 100
        self.contact_name = "John Doe"
        self.contact_title = "Manager"
        self.metadata = {'source': 'test'}
    
    def test_contact_added_event_creation(self):
        """Test contact added event creation."""
        event = ContactAddedEvent(
            self.company_id,
            self.event_date,
            self.contact_id,
            self.contact_name,
            self.contact_title,
            self.metadata
        )
        
        assert event.company_id == 1
        assert event.event_date == date(2024, 1, 15)
        assert event.contact_id == 100
        assert event.contact_name == "John Doe"
        assert event.contact_title == "Manager"
        assert event.metadata['source'] == 'test'
        assert event.metadata['contact_id'] == 100
        assert event.metadata['contact_name'] == "John Doe"
        assert event.metadata['contact_title'] == "Manager"
    
    def test_contact_added_event_type(self):
        """Test contact added event type property."""
        event = ContactAddedEvent(
            self.company_id,
            self.event_date,
            self.contact_id,
            self.contact_name,
            self.contact_title
        )
        
        assert event.event_type == CompanyDomainEventType.CONTACT_ADDED


class TestContactUpdatedEvent:
    """Test the ContactUpdatedEvent class."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.company_id = 1
        self.event_date = date(2024, 1, 15)
        self.contact_id = 100
        self.new_values = {'email': 'new@test.com', 'phone': '098-765-4321'}
        self.updated_fields = ['email', 'phone']
        self.metadata = {'source': 'test'}

    def test_contact_updated_event_creation(self):
        """Test contact updated event creation."""
        event = ContactUpdatedEvent(
            self.company_id,
            self.contact_id,
            self.event_date,
            self.updated_fields,
            self.new_values
        )
        
        assert event.company_id == 1
        assert event.event_date == date(2024, 1, 15)
        assert event.contact_id == 100
        assert event.new_values == {'email': 'new@test.com', 'phone': '098-765-4321'}
        assert event.updated_fields == ['email', 'phone']
        assert event.audit_trail['contact_id'] == 100
        assert event.audit_trail['updated_fields'] == ['email', 'phone']

    def test_contact_updated_event_type(self):
        """Test contact updated event type property."""
        event = ContactUpdatedEvent(
            self.company_id,
            self.contact_id,
            self.event_date,
            self.updated_fields,
            self.new_values
        )
        
        assert event.event_type == CompanyDomainEventType.CONTACT_UPDATED


class TestPortfolioUpdatedEvent:
    """Test the PortfolioUpdatedEvent class."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.company_id = 1
        self.event_date = date(2024, 1, 15)
        self.fund_id = 200
        self.operation = "fund_added"
        self.metadata = {'source': 'test'}
    
    def test_portfolio_updated_event_creation(self):
        """Test portfolio updated event creation."""
        event = PortfolioUpdatedEvent(
            self.company_id,
            self.event_date,
            self.fund_id,
            self.operation,
            self.metadata
        )
        
        assert event.company_id == 1
        assert event.event_date == date(2024, 1, 15)
        assert event.fund_id == 200
        assert event.operation == "fund_added"
        assert event.metadata['source'] == 'test'
        assert event.metadata['fund_id'] == 200
        assert event.metadata['operation'] == "fund_added"
    
    def test_portfolio_updated_event_type(self):
        """Test portfolio updated event type property."""
        event = PortfolioUpdatedEvent(
            self.company_id,
            self.event_date,
            self.fund_id,
            self.operation
        )
        
        assert event.event_type == CompanyDomainEventType.PORTFOLIO_UPDATED


class TestDomainEventIntegration:
    """Test integration between different domain events."""
    
    def test_event_metadata_consistency(self):
        """Test that event metadata is consistent across different event types."""
        company_id = 1
        event_date = date(2024, 1, 15)
        
        # Create different types of events
        created_event = CompanyCreatedEvent(
            company_id, event_date, "Test Company", CompanyType.PRIVATE_EQUITY
        )
        
        updated_event = CompanyUpdatedEvent(
            company_id, event_date, ['name']
        )
        
        deleted_event = CompanyDeletedEvent(
            company_id, event_date, "Test Company"
        )
        
        # Verify all events have consistent base structure
        for event in [created_event, updated_event, deleted_event]:
            assert event.company_id == company_id
            assert event.event_date == event_date
            assert event.timestamp is not None
            assert event.event_id is not None
            assert isinstance(event.metadata, dict)
    
    def test_event_serialization_consistency(self):
        """Test that all events can be serialized consistently."""
        company_id = 1
        event_date = date(2024, 1, 15)
        
        events = [
            CompanyCreatedEvent(company_id, event_date, "Test Company"),
            CompanyUpdatedEvent(company_id, event_date, ['name']),
            CompanyDeletedEvent(company_id, event_date, "Test Company"),
            ContactAddedEvent(company_id, event_date, 100, "John Doe", "Manager"),
            PortfolioUpdatedEvent(company_id, event_date, 200, "fund_added")
        ]
        
        for event in events:
            # All events should be serializable
            event_dict = event.to_dict()
            
            assert isinstance(event_dict, dict)
            assert 'event_id' in event_dict
            assert 'event_type' in event_dict
            assert 'company_id' in event_dict
            assert 'event_date' in event_dict
            assert 'timestamp' in event_dict
            assert 'metadata' in event_dict
            
            # Event type should be a string value
            assert isinstance(event_dict['event_type'], str)
            
            # Company ID should be an integer
            assert isinstance(event_dict['company_id'], int)
            
            # Event date should be an ISO string
            assert isinstance(event_dict['event_date'], str)
            assert len(event_dict['event_date']) == 10  # YYYY-MM-DD format
