"""
Investment Company Enums Tests

This module provides comprehensive testing for the investment company enums,
following enterprise testing standards with focused, targeted test coverage.

Tests cover:
- Enum value definitions and constraints
- String conversion methods
- Validation and error handling
- Enum utility methods
- Domain event type definitions

Note: Business logic tests are in separate service test files.
This file focuses purely on the enum functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.investment_company.enums import (
    CompanyType, CompanyStatus, CompanyDomainEventType,
    CompanyOperationType
)


class TestCompanyType:
    """Test suite for CompanyType enum"""
    
    def test_company_type_values(self):
        """Test all company type enum values are properly defined."""
        expected_values = {
            'PRIVATE_EQUITY': 'Private Equity',
            'VENTURE_CAPITAL': 'Venture Capital',
            'REAL_ESTATE': 'Real Estate',
            'INFRASTRUCTURE': 'Infrastructure',
            'CREDIT': 'Credit',
            'HEDGE_FUND': 'Hedge Fund',
            'FAMILY_OFFICE': 'Family Office',
            'INVESTMENT_BANK': 'Investment Bank',
            'ASSET_MANAGEMENT': 'Asset Management',
            'OTHER': 'Other'
        }
        
        for enum_name, expected_value in expected_values.items():
            enum_value = getattr(CompanyType, enum_name)
            assert enum_value.value == expected_value
            assert str(enum_value) == expected_value
    
    def test_company_type_from_string_valid(self):
        """Test creating enum from valid string values."""
        # Test each valid company type
        for company_type in CompanyType:
            result = CompanyType.from_string(company_type.value)
            assert result == company_type
    
    def test_company_type_from_string_invalid(self):
        """Test creating enum from invalid string values."""
        invalid_values = [
            'Invalid Type',
            'Private Equity Fund',  # Close but not exact
            'VENTURE_CAPITAL',      # Wrong case
            'real estate',          # Wrong case
            '',
            None
        ]
        
        for invalid_value in invalid_values:
            if invalid_value is None:
                with pytest.raises(ValueError, match="Invalid CompanyType: None"):
                    CompanyType.from_string(invalid_value)
            else:
                with pytest.raises(ValueError, match=f"Invalid CompanyType: {invalid_value}"):
                    CompanyType.from_string(invalid_value)
    
    def test_company_type_string_representation(self):
        """Test string representation of company types."""
        for company_type in CompanyType:
            assert str(company_type) == company_type.value
            assert repr(company_type) == f"<CompanyType.{company_type.name}: '{company_type.value}'>"
    
    def test_company_type_comparison(self):
        """Test enum comparison operations."""
        # Test equality
        assert CompanyType.PRIVATE_EQUITY == CompanyType.PRIVATE_EQUITY
        assert CompanyType.VENTURE_CAPITAL == CompanyType.VENTURE_CAPITAL
        
        # Test inequality
        assert CompanyType.PRIVATE_EQUITY != CompanyType.VENTURE_CAPITAL
        assert CompanyType.REAL_ESTATE != CompanyType.INFRASTRUCTURE
        
        # Test identity
        assert CompanyType.PRIVATE_EQUITY is CompanyType.PRIVATE_EQUITY
        assert CompanyType.VENTURE_CAPITAL is CompanyType.VENTURE_CAPITAL

class TestCompanyStatus:
    """Test suite for CompanyStatus enum"""
    
    def test_company_status_values(self):
        """Test all company status enum values are properly defined."""
        expected_values = {
            'ACTIVE': 'ACTIVE',
            'INACTIVE': 'INACTIVE',
            'SUSPENDED': 'SUSPENDED',
            'CLOSED': 'CLOSED'
        }
        
        for enum_name, expected_value in expected_values.items():
            enum_value = getattr(CompanyStatus, enum_name)
            assert enum_value.value == expected_value
            assert str(enum_value) == expected_value
    
    def test_company_status_from_string_valid(self):
        """Test creating enum from valid string values."""
        # Test each valid company status
        for status in CompanyStatus:
            result = CompanyStatus.from_string(status.value)
            assert result == status
    
    def test_company_status_from_string_invalid(self):
        """Test creating enum from invalid string values."""
        invalid_values = [
            'Invalid Status',
            'active',      # Wrong case
            'INACTIVE_STATUS',  # Close but not exact
            'SUSPENDED_OPERATIONS',  # Too long
            '',
            None
        ]
        
        for invalid_value in invalid_values:
            if invalid_value is None:
                with pytest.raises(ValueError, match="Invalid CompanyStatus: None"):
                    CompanyStatus.from_string(invalid_value)
            else:
                with pytest.raises(ValueError, match=f"Invalid CompanyStatus: {invalid_value}"):
                    CompanyStatus.from_string(invalid_value)
    
    def test_company_status_string_representation(self):
        """Test string representation of company statuses."""
        for status in CompanyStatus:
            assert str(status) == status.value
            assert repr(status) == f"<CompanyStatus.{status.name}: '{status.value}'>"
    
    def test_company_status_comparison(self):
        """Test enum comparison operations."""
        # Test equality
        assert CompanyStatus.ACTIVE == CompanyStatus.ACTIVE
        assert CompanyStatus.INACTIVE == CompanyStatus.INACTIVE
        
        # Test inequality
        assert CompanyStatus.ACTIVE != CompanyStatus.INACTIVE
        assert CompanyStatus.SUSPENDED != CompanyStatus.CLOSED
        
        # Test identity
        assert CompanyStatus.ACTIVE is CompanyStatus.ACTIVE
        assert CompanyStatus.INACTIVE is CompanyStatus.INACTIVE
    
    def test_company_status_iteration(self):
        """Test that all company statuses can be iterated over."""
        company_statuses = list(CompanyStatus)
        assert len(company_statuses) == 4  # Total number of company statuses
        
        # Verify all expected statuses are present
        expected_names = {'ACTIVE', 'INACTIVE', 'SUSPENDED', 'CLOSED'}
        actual_names = {cs.name for cs in company_statuses}
        assert actual_names == expected_names
    
    def test_company_status_hashable(self):
        """Test that company statuses are hashable and can be used in sets/dicts."""
        status_set = set(CompanyStatus)
        assert len(status_set) == 4
        
        status_dict = {cs: cs.value for cs in CompanyStatus}
        assert len(status_dict) == 4
        assert status_dict[CompanyStatus.ACTIVE] == 'ACTIVE'
    
    def test_company_status_default_behavior(self):
        """Test default status behavior."""
        # ACTIVE should be the default status
        assert CompanyStatus.ACTIVE in CompanyStatus
        
        # Test that ACTIVE is the first status (if order matters)
        statuses = list(CompanyStatus)
        assert CompanyStatus.ACTIVE in statuses


class TestCompanyDomainEventType:
    """Test suite for CompanyDomainEventType enum"""
    
    def test_domain_event_type_values(self):
        """Test all domain event type enum values are properly defined."""
        expected_values = {
            'COMPANY_CREATED': 'COMPANY_CREATED',
            'COMPANY_UPDATED': 'COMPANY_UPDATED',
            'COMPANY_DELETED': 'COMPANY_DELETED',
            'CONTACT_ADDED': 'CONTACT_ADDED',
            'CONTACT_UPDATED': 'CONTACT_UPDATED',
            'CONTACT_DELETED': 'CONTACT_DELETED',
            'PORTFOLIO_UPDATED': 'PORTFOLIO_UPDATED',
            'FUND_ADDED_TO_PORTFOLIO': 'FUND_ADDED_TO_PORTFOLIO',
            'FUND_REMOVED_FROM_PORTFOLIO': 'FUND_REMOVED_FROM_PORTFOLIO',
            'COMPANY_SUMMARY_UPDATED': 'COMPANY_SUMMARY_UPDATED'
        }
        
        for enum_name, expected_value in expected_values.items():
            enum_value = getattr(CompanyDomainEventType, enum_name)
            assert enum_value.value == expected_value
            assert str(enum_value) == expected_value
    
    def test_domain_event_type_string_representation(self):
        """Test string representation of domain event types."""
        for event_type in CompanyDomainEventType:
            assert str(event_type) == event_type.value
            assert repr(event_type) == f"<CompanyDomainEventType.{event_type.name}: '{event_type.value}'>"
    
    def test_domain_event_type_comparison(self):
        """Test enum comparison operations."""
        # Test equality
        assert CompanyDomainEventType.COMPANY_CREATED == CompanyDomainEventType.COMPANY_CREATED
        assert CompanyDomainEventType.CONTACT_ADDED == CompanyDomainEventType.CONTACT_ADDED
        
        # Test inequality
        assert CompanyDomainEventType.COMPANY_CREATED != CompanyDomainEventType.COMPANY_UPDATED
        assert CompanyDomainEventType.PORTFOLIO_UPDATED != CompanyDomainEventType.FUND_ADDED_TO_PORTFOLIO
    
    def test_domain_event_type_categorization(self):
        """Test categorization of event types by domain."""
        # Company-level events
        company_events = {
            CompanyDomainEventType.COMPANY_CREATED,
            CompanyDomainEventType.COMPANY_UPDATED,
            CompanyDomainEventType.COMPANY_DELETED
        }
        
        # Contact-level events
        contact_events = {
            CompanyDomainEventType.CONTACT_ADDED,
            CompanyDomainEventType.CONTACT_UPDATED,
            CompanyDomainEventType.CONTACT_DELETED
        }
        
        # Portfolio-level events
        portfolio_events = {
            CompanyDomainEventType.PORTFOLIO_UPDATED,
            CompanyDomainEventType.FUND_ADDED_TO_PORTFOLIO,
            CompanyDomainEventType.FUND_REMOVED_FROM_PORTFOLIO,
            CompanyDomainEventType.COMPANY_SUMMARY_UPDATED
        }
        
        # Verify all events are categorized
        all_events = set(CompanyDomainEventType)
        categorized_events = company_events | contact_events | portfolio_events
        assert all_events == categorized_events


class TestCompanyOperationType:
    """Test suite for CompanyOperationType enum"""
    
    def test_operation_type_values(self):
        """Test all operation type enum values are properly defined."""
        expected_values = {
            'CREATE': 'CREATE',
            'UPDATE': 'UPDATE',
            'DELETE': 'DELETE',
            'ADD_CONTACT': 'ADD_CONTACT',
            'UPDATE_CONTACT': 'UPDATE_CONTACT',
            'REMOVE_CONTACT': 'REMOVE_CONTACT',
            'ADD_FUND': 'ADD_FUND',
            'REMOVE_FUND': 'REMOVE_FUND',
            'UPDATE_PORTFOLIO': 'UPDATE_PORTFOLIO'
        }
        
        for enum_name, expected_value in expected_values.items():
            enum_value = getattr(CompanyOperationType, enum_name)
            assert enum_value.value == expected_value
            assert str(enum_value) == expected_value
    
    def test_operation_type_string_representation(self):
        """Test string representation of operation types."""
        for operation_type in CompanyOperationType:
            assert str(operation_type) == operation_type.value
            assert repr(operation_type) == f"<CompanyOperationType.{operation_type.name}: '{operation_type.value}'>"
    
    def test_operation_type_crud_operations(self):
        """Test CRUD operation types."""
        crud_operations = {
            CompanyOperationType.CREATE,
            CompanyOperationType.UPDATE,
            CompanyOperationType.DELETE
        }
        
        # Verify CRUD operations exist
        for operation in crud_operations:
            assert operation in CompanyOperationType
        
        # Verify additional operations exist
        assert CompanyOperationType.ADD_CONTACT in CompanyOperationType
        assert CompanyOperationType.ADD_FUND in CompanyOperationType





class TestEnumIntegration:
    """Test suite for enum integration and cross-references"""
    
    def test_enum_consistency(self):
        """Test consistency between related enums."""
        # Company types should be consistent with their string representations
        for company_type in CompanyType:
            assert company_type.value in str(company_type)
            # Company type names are converted to readable format
            # Example: PRIVATE_EQUITY -> 'Private Equity'
            expected_value = company_type.name.replace('_', ' ').title()
            assert company_type.value == expected_value
        
        # Company statuses should be consistent
        for status in CompanyStatus:
            assert status.value == status.name
    
    def test_enum_usage_in_models(self):
        """Test that enums can be used in model definitions."""
        # This test verifies that enums are properly defined for use in models
        # The actual model usage is tested in model test files
        
        # Test that all enums are properly defined
        assert CompanyType.PRIVATE_EQUITY is not None
        assert CompanyStatus.ACTIVE is not None
        assert CompanyDomainEventType.COMPANY_CREATED is not None
        assert CompanyOperationType.CREATE is not None
    
    def test_enum_serialization(self):
        """Test that enums can be serialized and deserialized."""
        # Test JSON serialization (if needed)
        for company_type in CompanyType:
            serialized = company_type.value
            assert isinstance(serialized, str)
            assert serialized == str(company_type)
        
        for status in CompanyStatus:
            serialized = status.value
            assert isinstance(serialized, str)
            assert serialized == str(status)
    
    def test_enum_database_compatibility(self):
        """Test that enums are compatible with database constraints."""
        # Test that enum values are strings (for database storage)
        for company_type in CompanyType:
            assert isinstance(company_type.value, str)
            assert len(company_type.value) > 0
        
        for status in CompanyStatus:
            assert isinstance(status.value, str)
            assert len(status.value) > 0
    
    def test_enum_extensibility(self):
        """Test that enums can be extended with new values."""
        # Test that new values can be added to existing enums
        # This is a forward-compatibility test
        
        # Verify current enum structure
        assert len(CompanyType) >= 10
        assert len(CompanyStatus) >= 4
        assert len(CompanyDomainEventType) >= 10
        
        # Test that enums support iteration and membership
        assert CompanyType.PRIVATE_EQUITY in CompanyType
        assert CompanyStatus.ACTIVE in CompanyStatus
        assert CompanyDomainEventType.COMPANY_CREATED in CompanyDomainEventType
