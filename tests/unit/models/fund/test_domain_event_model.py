"""
Domain Event Model Tests

This module tests the DomainEvent model validation and business rules.
Focus: Model constraints, validation, and basic business logic only.

Other aspects covered elsewhere:
- Persistence: test_domain_event_repository.py
- Event processing: test_event_handlers.py  
- Event orchestration: test_orchestrator.py
- Event routing: test_event_registry.py
"""

import pytest
from datetime import datetime, timezone

# NEW ARCHITECTURE IMPORTS - NOT legacy monolithic models
from src.fund.models.domain_event import DomainEvent


class TestDomainEventModel:
    """Test suite for DomainEvent model - Core model validation only"""
    
    @pytest.fixture
    def domain_event_data(self):
        """Sample domain event data for testing."""
        return {
            'fund_id': 1,
            'event_type': 'NAV_UPDATED',
            'event_data': {'nav': 10.50, 'units': 1000},
            'source': 'fund_model',
            'processed': 'PENDING'
        }
    
    def test_domain_event_creation(self, domain_event_data):
        """Test domain event creation with valid data."""
        event = DomainEvent(**domain_event_data)
        
        assert event.fund_id == 1
        assert event.event_type == 'NAV_UPDATED'
        assert event.event_data == {'nav': 10.50, 'units': 1000}
        assert event.source == 'fund_model'
        assert event.processed == 'PENDING'
        # Note: SQLAlchemy defaults are only set on database insert, not object creation
        # assert event.timestamp is not None  # Will be None until database insert
        assert event.error_message is None
        assert event.processed_at is None
    
    def test_domain_event_required_fields(self, domain_event_data):
        """Test domain event required field validation."""
        # Note: SQLAlchemy models don't enforce nullable=False at Python level
        # These constraints are enforced at the database level
        
        # Test missing fund_id - SQLAlchemy will allow this at Python level
        invalid_data = domain_event_data.copy()
        del invalid_data['fund_id']
        
        # SQLAlchemy allows creation, but database insert would fail
        event = DomainEvent(**invalid_data)
        assert event.fund_id is None
        
        # Test missing event_type
        invalid_data = domain_event_data.copy()
        del invalid_data['event_type']
        
        event = DomainEvent(**invalid_data)
        assert event.event_type is None
        
        # Test missing source
        invalid_data = domain_event_data.copy()
        del invalid_data['source']
        
        event = DomainEvent(**invalid_data)
        assert event.source is None
    
    def test_domain_event_optional_fields(self, domain_event_data):
        """Test domain event optional field handling."""
        # Test without event_data
        minimal_data = {
            'fund_id': domain_event_data['fund_id'],
            'event_type': domain_event_data['event_type'],
            'source': domain_event_data['source']
        }
        
        event = DomainEvent(**minimal_data)
        assert event.event_data is None
        # Note: SQLAlchemy defaults are only set on database insert
        # assert event.processed == 'PENDING'  # Will be None until database insert
        assert event.error_message is None
        assert event.processed_at is None
    
    def test_domain_event_timestamp_default(self, domain_event_data):
        """Test domain event timestamp default behavior."""
        event = DomainEvent(**domain_event_data)
        
        # Note: SQLAlchemy defaults are only set on database insert, not object creation
        # Timestamp will be None until database insert
        assert event.timestamp is None
        
        # Test that we can set timestamp manually
        test_timestamp = datetime.now(timezone.utc)
        event.timestamp = test_timestamp
        assert event.timestamp == test_timestamp
        assert isinstance(event.timestamp, datetime)
    
    def test_domain_event_validation_method(self, domain_event_data):
        """Test domain event validation method."""
        event = DomainEvent(**domain_event_data)
        
        # Should pass validation
        assert event.validate_basic_constraints() is True
        
        # Test validation failure - missing event_type
        event.event_type = None
        with pytest.raises(ValueError, match="Event type is required"):
            event.validate_basic_constraints()
        
        # Test validation failure - missing source
        event.event_type = 'NAV_UPDATED'  # Restore valid value
        event.source = None
        with pytest.raises(ValueError, match="Event source is required"):
            event.validate_basic_constraints()
        
        # Test validation failure - invalid status
        event.source = 'fund_model'  # Restore valid value
        event.processed = 'INVALID_STATUS'
        with pytest.raises(ValueError, match="Invalid processing status"):
            event.validate_basic_constraints()




class TestDomainEventDataHandling:
    """Test suite for domain event data handling - Model level only"""
    
    def test_domain_event_data_persistence(self):
        """Test domain event data persistence and retrieval."""
        event_data = {
            'nav': 10.50,
            'units': 1000,
            'calculation_method': 'weighted_average'
        }
        
        event = DomainEvent(
            fund_id=1,
            event_type='NAV_UPDATED',
            event_data=event_data,
            source='fund_model',
            processed='PENDING'
        )
        
        # Verify data persistence
        assert event.event_data == event_data
        assert event.event_data['nav'] == 10.50
        assert event.event_data['units'] == 1000
        assert event.event_data['calculation_method'] == 'weighted_average'
    
    def test_domain_event_field_access(self):
        """Test domain event field access and assignment."""
        event = DomainEvent(
            fund_id=1,
            event_type='NAV_UPDATED',
            source='fund_model',
            processed='PENDING'
        )
        
        # Test field assignment
        event.fund_id = 2
        assert event.fund_id == 2
        
        event.event_type = 'UNITS_CHANGED'
        assert event.event_type == 'UNITS_CHANGED'
        
        event.source = 'calculation_service'
        assert event.source == 'calculation_service'


class TestDomainEventBusinessRules:
    """Test suite for domain event business rules - Model level only"""
    
    def test_event_data_integrity(self):
        """Test event data integrity at model level."""
        # Test with complex nested data
        complex_event_data = {
            'nav_calculation': {
                'method': 'weighted_average',
                'parameters': {
                    'lookback_period': 30,
                    'smoothing_factor': 0.1
                },
                'results': {
                    'nav': 10.50,
                    'confidence_interval': 0.95
                }
            }
        }
        
        event = DomainEvent(
            fund_id=1,
            event_type='NAV_UPDATED',
            event_data=complex_event_data,
            source='fund_model',
            processed='PENDING'
        )
        
        # Verify complex data is preserved
        assert event.event_data == complex_event_data
        assert event.event_data['nav_calculation']['method'] == 'weighted_average'
        assert event.event_data['nav_calculation']['parameters']['lookback_period'] == 30


class TestDomainEventEdgeCases:
    """Test suite for domain event edge cases - Model level only"""
    
    def test_empty_event_data(self):
        """Test domain event with empty event data."""
        event = DomainEvent(
            fund_id=1,
            event_type='SYSTEM_HEARTBEAT',
            event_data={},
            source='system_monitor',
            processed='PENDING'
        )
        
        assert event.event_data == {}
        assert event.validate_basic_constraints() is True
    
    def test_none_values_in_event_data(self):
        """Test domain event with None values in event data."""
        none_data = {
            'string_value': None,
            'number_value': None,
            'boolean_value': None
        }
        
        event = DomainEvent(
            fund_id=1,
            event_type='NULL_VALUE_TEST',
            event_data=none_data,
            source='test_service',
            processed='PENDING'
        )
        
        # Verify None values are preserved
        assert event.event_data == none_data
        assert event.event_data['string_value'] is None
        assert event.event_data['number_value'] is None
        assert event.event_data['boolean_value'] is None


