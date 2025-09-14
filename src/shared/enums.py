"""
Shared Enums Module.

This module contains all enum definitions for the shared system.
Following enterprise best practices for clean separation of concerns.
"""

from enum import Enum

class SortOrder(Enum):
    """
    Sort order enum.
    
    Defines the order for sorting operations in APIs and queries.
    
    Values:
        ASC: Ascending order (A-Z, 1-9, oldest to newest)
        DESC: Descending order (Z-A, 9-1, newest to oldest)
    """
    ASC = 'ASC'
    DESC = 'DESC'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortOrder':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortOrder: {value}. Must be one of: {[o.value for o in cls]}")
    
    @classmethod
    def is_reverse(cls, order: 'SortOrder') -> bool:
        """Check if sort order is reverse/descending."""
        return order == cls.DESC

class EventOperation(Enum):
    """
    Event operation enum.
    
    Defines all possible operations that can occur on an event.
    
    Values:
        CREATE: Event creation operation
        DELETE: Event deletion operation
        UPDATE: Event update operation
    """
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'EventOperation':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid EventOperation: {value}. Must be one of: {[e.value for e in cls]}")