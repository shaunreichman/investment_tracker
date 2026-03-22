"""
Entity Enums Module.

This module contains all enum definitions for the entity system.
Following enterprise best practices for clean separation of concerns.
"""

from enum import Enum

class EntityType(Enum):
    """
    Entity type enum.
    """
    PERSON = 'PERSON'
    COMPANY = 'COMPANY'
    TRUST = 'TRUST'
    FUND = 'FUND'
    OTHER = 'OTHER'

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'EntityType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid EntityType: {value}. Must be one of: {[t.value for t in cls]}")


class SortFieldEntity(Enum):
    """
    Sort field enum for entities.
    """
    NAME = 'NAME'
    TYPE = 'TYPE'
    TAX_JURISDICTION = 'TAX_JURISDICTION'
    CREATED_AT = 'CREATED_AT'
    UPDATED_AT = 'UPDATED_AT'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldEntity':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldEntity: {value}. Must be one of: {[t.value for t in cls]}")