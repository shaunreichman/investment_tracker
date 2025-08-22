"""
Investment Company Enums.

This module provides enums for investment company operations,
including domain event types and company-specific enums.

Key responsibilities:
- Domain event type definitions
- Company operation enums
- Validation enums
"""

from enum import Enum


class CompanyDomainEventType(Enum):
    """
    Company domain event type enum.
    
    Defines business domain events that are published when significant
    state changes occur in the investment company system.
    
    Values:
        COMPANY_CREATED: Investment company was created
        COMPANY_UPDATED: Company information was updated
        COMPANY_DELETED: Company was deleted
        CONTACT_ADDED: Contact was added to company
        CONTACT_UPDATED: Contact information was updated
        CONTACT_DELETED: Contact was removed from company
        PORTFOLIO_UPDATED: Company portfolio was updated
        FUND_ADDED_TO_PORTFOLIO: Fund was added to company portfolio
        FUND_REMOVED_FROM_PORTFOLIO: Fund was removed from company portfolio
        COMPANY_SUMMARY_UPDATED: Company summary fields were updated
    """
    COMPANY_CREATED = 'COMPANY_CREATED'
    COMPANY_UPDATED = 'COMPANY_UPDATED'
    COMPANY_DELETED = 'COMPANY_DELETED'
    CONTACT_ADDED = 'CONTACT_ADDED'
    CONTACT_UPDATED = 'CONTACT_UPDATED'
    CONTACT_DELETED = 'CONTACT_DELETED'
    PORTFOLIO_UPDATED = 'PORTFOLIO_UPDATED'
    FUND_ADDED_TO_PORTFOLIO = 'FUND_ADDED_TO_PORTFOLIO'
    FUND_REMOVED_FROM_PORTFOLIO = 'FUND_REMOVED_FROM_PORTFOLIO'
    COMPANY_SUMMARY_UPDATED = 'COMPANY_SUMMARY_UPDATED'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value


class CompanyOperationType(Enum):
    """
    Company operation type enum.
    
    Defines the types of operations that can be performed
    on investment companies.
    
    Values:
        CREATE: Create new company
        UPDATE: Update existing company
        DELETE: Delete company
        ADD_CONTACT: Add contact to company
        UPDATE_CONTACT: Update contact information
        REMOVE_CONTACT: Remove contact from company
        ADD_FUND: Add fund to portfolio
        REMOVE_FUND: Remove fund from portfolio
        UPDATE_PORTFOLIO: Update portfolio information
    """
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    ADD_CONTACT = 'ADD_CONTACT'
    UPDATE_CONTACT = 'UPDATE_CONTACT'
    REMOVE_CONTACT = 'REMOVE_CONTACT'
    ADD_FUND = 'ADD_FUND'
    REMOVE_FUND = 'REMOVE_FUND'
    UPDATE_PORTFOLIO = 'UPDATE_PORTFOLIO'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value


class CompanyStatus(Enum):
    """
    Company status enum.
    
    Defines the possible statuses for investment companies.
    
    Values:
        ACTIVE: Company is active and operational
        INACTIVE: Company is inactive
        SUSPENDED: Company operations are suspended
        CLOSED: Company has closed operations
    """
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    SUSPENDED = 'SUSPENDED'
    CLOSED = 'CLOSED'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value


# Convenience functions for common enum operations
def get_all_enum_values(enum_class: type) -> list:
    """Get all values from an enum class."""
    return [e.value for e in enum_class]


def validate_enum_value(enum_class: type, value: str) -> bool:
    """Validate if a string value is valid for an enum class."""
    try:
        enum_class(value)
        return True
    except ValueError:
        return False
