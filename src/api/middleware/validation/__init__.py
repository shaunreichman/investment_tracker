"""
Validation Middleware Module.

This module provides domain-specific validation decorators and utilities
for API request validation.

Structure:
- base_validation.py: Common validation utilities and base validator
"""

# Import base validation utilities
from src.api.middleware.validation.base_validation import (
    ValidationError,
    BaseValidator,
    validate_request,
    validate_required_string,
    validate_optional_string,
    validate_required_integer,
    validate_required_float,
    validate_required_enum,
    validate_optional_enum
)

# Import fund event validation functions
from src.api.middleware.validation.fund_event_distribution_validation import validate_distribution_data

__all__ = [
    # Base validation utilities
    'ValidationError',
    'BaseValidator',
    'validate_request',
    'validate_required_string',
    'validate_optional_string',
    'validate_required_integer',
    'validate_required_float',
    'validate_required_enum',
    'validate_optional_enum',
    # Fund event validation functions
    'validate_distribution_data',
]
