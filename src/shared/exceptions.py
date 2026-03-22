"""
Shared exception classes for enterprise error handling.

These exceptions allow services to raise errors with structured details
that can be properly formatted in API responses.
"""

from typing import Dict, Any, Optional


class ValidationException(Exception):
    """
    Exception for validation errors with structured details.
    
    This exception allows services to raise validation errors with both
    a user-friendly message and structured details for programmatic handling.
    
    Example:
        raise ValidationException(
            "Cannot delete entity with existing dependencies",
            details={
                "funds": {"count": 2, "message": "..."}
            }
        )
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize validation exception.
        
        Args:
            message: User-friendly error message
            details: Structured error details for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        return self.message

