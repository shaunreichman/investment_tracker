"""
Base Validation Utilities.

This module provides common validation utilities and patterns that can be
shared across all domain-specific validation modules.

Key features:
- Common validation patterns and regex
- Type conversion and validation
- Field validation utilities
- Security sanitization
- Generic validation decorator
"""

import re
from typing import Dict, Any, List, Optional, Union, Callable
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, date


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, status_code: int = 400):
        self.message = message
        self.field = field
        self.status_code = status_code
        super().__init__(self.message)


class BaseValidator:
    """
    Base validator with common validation methods.
    
    This class provides reusable validation utilities that can be used
    across all domain-specific validation modules.
    """
    
    # Common validation patterns
    VALIDATION_PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?1?\d{9,15}$',
        'date': r'^\d{4}-\d{2}-\d{2}$',
        'routing_number': r'^\d{9}$',
        'currency': r'^[A-Z]{3}$',
        'country_code': r'^[A-Z]{2}$',  # 2-letter ISO country code
        'postal_code': r'^\d{5}(-\d{4})?$',
        'ssn': r'^\d{3}-\d{2}-\d{4}$',
        'financial_year': r'^\d{4}-\d{2}$',  # e.g., "2023-24"
        'non_empty_string': r'^.+$',  # At least one character
        'alphanumeric': r'^[a-zA-Z0-9]+$',
        'alphanumeric_with_spaces': r'^[a-zA-Z0-9\s]+$',
        'url': r'^https?://[^\s/$.?#].[^\s]*$'
    }
    
    # Type conversion functions
    TYPE_CONVERTERS = {
        'int': int,
        'float': float,
        'bool': lambda x: str(x).lower() in ('true', '1', 'yes', 'on') if isinstance(x, str) else bool(x),
        'date': lambda x: datetime.strptime(x, '%Y-%m-%d').date() if isinstance(x, str) else x,
        'datetime': lambda x: datetime.fromisoformat(x) if isinstance(x, str) else x
    }
    
    def __init__(self):
        """Initialize the validator."""
        pass
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that all required fields are present and non-empty.
        
        Args:
            data: Request data dictionary
            required_fields: List of required field names
            
        Raises:
            ValidationError: If any required field is missing or empty
        """
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                empty_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        if empty_fields:
            raise ValidationError(f"Required fields cannot be empty: {', '.join(empty_fields)}")
    
    def validate_forbidden_fields(self, data: Dict[str, Any], forbidden_fields: List[str]) -> None:
        """
        Validate that forbidden fields are not present in the request data.
        
        Args:
            data: Request data dictionary
            forbidden_fields: List of field names that must not be present
            
        Raises:
            ValidationError: If any forbidden field is present
        """
        present_forbidden_fields = []
        
        for field in forbidden_fields:
            if field in data:
                present_forbidden_fields.append(field)
        
        if present_forbidden_fields:
            raise ValidationError(f"Forbidden fields must not be included: {', '.join(present_forbidden_fields)}")
    
    def validate_field_types(self, data: Dict[str, Any], field_types: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate and convert field types.
        
        Args:
            data: Request data dictionary
            field_types: Dictionary mapping field names to expected types
            
        Returns:
            Dictionary with converted values
            
        Raises:
            ValidationError: If type conversion fails
        """
        converted_data = data.copy()
        
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                value = data[field]
                
                try:
                    if expected_type in self.TYPE_CONVERTERS:
                        converted_data[field] = self.TYPE_CONVERTERS[expected_type](value)
                    elif expected_type == 'string':
                        if not isinstance(value, str):
                            raise ValueError(f"Expected string, got {type(value).__name__}")
                        converted_data[field] = str(value).strip()
                    else:
                        # For custom types, just validate they exist
                        if not hasattr(value, expected_type):
                            raise ValidationError(f"Invalid type for {field}: expected {expected_type}", field)
                except (ValueError, TypeError) as e:
                    raise ValidationError(f"Invalid {expected_type} value for '{field}': {str(e)}", field)
        
        return converted_data
    
    def validate_field_patterns(self, data: Dict[str, Any], field_patterns: Dict[str, str]) -> None:
        """
        Validate field values against regex patterns.
        
        Args:
            data: Request data dictionary
            field_patterns: Dictionary mapping field names to pattern names
            
        Raises:
            ValidationError: If pattern validation fails
        """
        for field, pattern_name in field_patterns.items():
            if field in data and data[field] is not None:
                value = str(data[field])
                pattern = self.VALIDATION_PATTERNS.get(pattern_name)
                
                if pattern and not re.match(pattern, value):
                    raise ValidationError(f"Invalid {pattern_name} format for {field}", field)
    
    def validate_field_ranges(self, data: Dict[str, Any], field_ranges: Dict[str, Dict[str, Union[int, float]]]) -> None:
        """
        Validate numeric field values within specified ranges.
        
        Args:
            data: Request data dictionary
            field_ranges: Dictionary mapping field names to range constraints
            
        Raises:
            ValidationError: If range validation fails
        """
        for field, constraints in field_ranges.items():
            if field in data and data[field] is not None:
                value = data[field]
                
                if 'min' in constraints and value < constraints['min']:
                    raise ValidationError(f"{field} must be at least {constraints['min']}", field)
                
                if 'max' in constraints and value > constraints['max']:
                    raise ValidationError(f"{field} must be at most {constraints['max']}", field)
    
    def validate_field_choices(self, data: Dict[str, Any], field_choices: Dict[str, List[Any]]) -> None:
        """
        Validate field values against allowed choices.
        
        Args:
            data: Request data dictionary
            field_choices: Dictionary mapping field names to allowed values
            
        Raises:
            ValidationError: If choice validation fails
        """
        for field, allowed_values in field_choices.items():
            if field in data and data[field] is not None:
                value = data[field]
                if value not in allowed_values:
                    raise ValidationError(f"Invalid value for {field}. Must be one of: {', '.join(map(str, allowed_values))}", field)
    
    def validate_enum_values(self, data: Dict[str, Any], enum_fields: Dict[str, type]) -> Dict[str, Any]:
        """
        Validate and convert enum field values using actual enum classes.
        
        Args:
            data: Request data dictionary
            enum_fields: Dictionary mapping field names to enum classes
            
        Returns:
            Dictionary with converted enum values
            
        Raises:
            ValidationError: If enum validation fails
        """
        converted_data = data.copy()
        
        for field, enum_class in enum_fields.items():
            if field in data and data[field] is not None:
                value = data[field]
                try:
                    # Convert string to enum if needed
                    if isinstance(value, str):
                        converted_data[field] = enum_class(value)
                    else:
                        converted_data[field] = enum_class(value)
                except ValueError:
                    valid_values = [e.value for e in enum_class]
                    raise ValidationError(f"Invalid {field}. Must be one of: {', '.join(valid_values)}", field)
        
        return converted_data
    
    def sanitize_strings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize string fields to prevent injection attacks.
        
        Args:
            data: Request data dictionary
            
        Returns:
            Dictionary with sanitized string values
        """
        sanitized_data = data.copy()
        
        for field, value in sanitized_data.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters but be less aggressive
                sanitized_data[field] = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', '', value).strip()
        
        return sanitized_data
    
    def validate_json_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """
        Validate data against a JSON schema.
        
        Args:
            data: Request data dictionary
            schema: JSON schema definition
            
        Raises:
            ValidationError: If schema validation fails
        """
        # Basic schema validation - can be extended with jsonschema library
        if 'type' in schema:
            expected_type = schema['type']
            if expected_type == 'object' and not isinstance(data, dict):
                raise ValidationError(f"Expected object, got {type(data).__name__}")
            elif expected_type == 'array' and not isinstance(data, list):
                raise ValidationError(f"Expected array, got {type(data).__name__}")
            elif expected_type == 'string' and not isinstance(data, str):
                raise ValidationError(f"Expected string, got {type(data).__name__}")
            elif expected_type == 'number' and not isinstance(data, (int, float)):
                raise ValidationError(f"Expected number, got {type(data).__name__}")
            elif expected_type == 'boolean' and not isinstance(data, bool):
                raise ValidationError(f"Expected boolean, got {type(data).__name__}")
        
        if 'required' in schema:
            self.validate_required_fields(data, schema['required'])
        
        if 'properties' in schema and isinstance(data, dict):
            for field, field_schema in schema['properties'].items():
                if field in data:
                    self.validate_json_schema(data[field], field_schema)
    
    def validate_string_length(self, data: Dict[str, Any], field_lengths: Dict[str, Dict[str, int]]) -> None:
        """
        Validate string field lengths.
        
        Args:
            data: Request data dictionary
            field_lengths: Dictionary mapping field names to length constraints
                          e.g., {'name': {'min': 2, 'max': 255}}
            
        Raises:
            ValidationError: If length validation fails
        """
        for field, constraints in field_lengths.items():
            if field in data and data[field] is not None:
                value = str(data[field])
                
                if 'min' in constraints and len(value) < constraints['min']:
                    raise ValidationError(f"{field} must be at least {constraints['min']} characters", field)
                
                if 'max' in constraints and len(value) > constraints['max']:
                    raise ValidationError(f"{field} must be at most {constraints['max']} characters", field)
    
    def validate_positive_numbers(self, data: Dict[str, Any], fields: List[str]) -> None:
        """
        Validate that specified fields contain positive numbers.
        
        Args:
            data: Request data dictionary
            fields: List of field names to validate
            
        Raises:
            ValidationError: If any field contains non-positive numbers
        """
        for field in fields:
            if field in data and data[field] is not None:
                value = data[field]
                if not isinstance(value, (int, float)) or value <= 0:
                    raise ValidationError(f"{field} must be a positive number", field)
    
    def validate_non_negative_numbers(self, data: Dict[str, Any], fields: List[str]) -> None:
        """
        Validate that specified fields contain non-negative numbers.
        
        Args:
            data: Request data dictionary
            fields: List of field names to validate
            
        Raises:
            ValidationError: If any field contains negative numbers
        """
        for field in fields:
            if field in data and data[field] is not None:
                value = data[field]
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValidationError(f"{field} must be a non-negative number", field)


def validate_request(
    required_fields: Optional[List[str]] = None,
    forbidden_fields: Optional[List[str]] = None,
    field_types: Optional[Dict[str, str]] = None,
    field_patterns: Optional[Dict[str, str]] = None,
    field_ranges: Optional[Dict[str, Dict[str, Union[int, float]]]] = None,
    field_choices: Optional[Dict[str, List[Any]]] = None,
    field_lengths: Optional[Dict[str, Dict[str, int]]] = None,
    positive_numbers: Optional[List[str]] = None,
    non_negative_numbers: Optional[List[str]] = None,
    enum_fields: Optional[Dict[str, type]] = None,
    json_schema: Optional[Dict[str, Any]] = None,
    custom_validation: Optional[Callable[[Dict[str, Any]], None]] = None,
    sanitize: bool = True
) -> Callable:
    """
    Generic validation decorator for request data.
    
    Args:
        required_fields: List of required field names
        forbidden_fields: List of field names that must not be present
        field_types: Dictionary mapping field names to expected types
        field_patterns: Dictionary mapping field names to pattern names
        field_ranges: Dictionary mapping field names to range constraints
        field_choices: Dictionary mapping field names to allowed values
        field_lengths: Dictionary mapping field names to length constraints
        positive_numbers: List of fields that must be positive numbers
        non_negative_numbers: List of fields that must be non-negative numbers
        enum_fields: Dictionary mapping field names to enum classes
        json_schema: JSON schema for validation
        custom_validation: Custom validation function that takes data dict and raises ValidationError
        sanitize: Whether to sanitize string inputs
        
    Returns:
        Decorated function with validation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get request data
                if request.is_json:
                    data = request.get_json() or {}
                elif request.form:
                    data = dict(request.form)
                else:
                    data = {}
                
                # Initialize validator
                validator = BaseValidator()
                
                # Apply validations in order
                if required_fields:
                    validator.validate_required_fields(data, required_fields)
                
                if forbidden_fields:
                    validator.validate_forbidden_fields(data, forbidden_fields)
                
                if field_types:
                    data = validator.validate_field_types(data, field_types)
                
                if field_patterns:
                    validator.validate_field_patterns(data, field_patterns)
                
                if field_ranges:
                    validator.validate_field_ranges(data, field_ranges)
                
                if field_choices:
                    validator.validate_field_choices(data, field_choices)
                
                if field_lengths:
                    validator.validate_string_length(data, field_lengths)
                
                if positive_numbers:
                    validator.validate_positive_numbers(data, positive_numbers)
                
                if non_negative_numbers:
                    validator.validate_non_negative_numbers(data, non_negative_numbers)
                
                if enum_fields:
                    data = validator.validate_enum_values(data, enum_fields)
                
                if json_schema:
                    validator.validate_json_schema(data, json_schema)
                
                if custom_validation:
                    custom_validation(data)
                
                if sanitize:
                    data = validator.sanitize_strings(data)
                
                # Store validated data in request context for controllers
                request.validated_data = data
                
                # Call the original function
                return func(*args, **kwargs)
                
            except ValidationError as e:
                current_app.logger.warning(f"Validation error: {e.message} for field: {e.field}")
                return jsonify({
                    "error": e.message,
                    "field": e.field,
                    "type": "validation_error"
                }), e.status_code
                
            except Exception as e:
                current_app.logger.error(f"Unexpected error during validation: {str(e)}")
                return jsonify({
                    "error": "Internal validation error",
                    "type": "validation_error"
                }), 500
        
        return wrapper
    return decorator


# Convenience functions for common validation patterns
def validate_required_string(field_name: str, min_length: int = 1, max_length: int = 255) -> Callable:
    """Validate a required string field with length constraints."""
    return validate_request(
        required_fields=[field_name],
        field_types={field_name: 'string'},
        field_lengths={field_name: {'min': min_length, 'max': max_length}},
        sanitize=True
    )


def validate_optional_string(field_name: str, max_length: int = 255) -> Callable:
    """Validate an optional string field with length constraints."""
    return validate_request(
        field_types={field_name: 'string'},
        field_lengths={field_name: {'max': max_length}},
        sanitize=True
    )


def validate_required_integer(field_name: str, min_value: int = 1) -> Callable:
    """Validate a required integer field with minimum value."""
    return validate_request(
        required_fields=[field_name],
        field_types={field_name: 'int'},
        field_ranges={field_name: {'min': min_value}}
    )


def validate_required_float(field_name: str, min_value: float = 0.0) -> Callable:
    """Validate a required float field with minimum value."""
    return validate_request(
        required_fields=[field_name],
        field_types={field_name: 'float'},
        field_ranges={field_name: {'min': min_value}}
    )


def validate_required_enum(field_name: str, enum_class: type) -> Callable:
    """Validate a required enum field."""
    return validate_request(
        required_fields=[field_name],
        enum_fields={field_name: enum_class}
    )


def validate_optional_enum(field_name: str, enum_class: type) -> Callable:
    """Validate an optional enum field."""
    return validate_request(
        enum_fields={field_name: enum_class}
    )
