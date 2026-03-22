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

Validation Parameter Naming Convention:
- field_*: Validates individual field values
- array_element_*: Validates each element within arrays (parallel to field_*)
- array_size: Validates array structure (count of elements)

Examples:
- field_ranges ↔ array_element_ranges
- field_lengths ↔ array_element_lengths  
- field_choices ↔ array_element_choices
- enum_fields ↔ array_element_enum_fields
"""

import re
from typing import Dict, Any, List, Optional, Union, Callable
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.exceptions import BadRequest
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
        'phone': r'^[+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]*$',  # International phone: allows country codes, formatting chars
        'financial_year': r'^\d{4}$',  # e.g., "2023"
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
        'datetime': lambda x: datetime.fromisoformat(x) if isinstance(x, str) else x,
        # Array type converters
        'array': lambda x: x if isinstance(x, list) else [x] if x is not None else None,
        'int_array': lambda x: [int(item) for item in (x if isinstance(x, list) else [x])] if x is not None else None,
        'float_array': lambda x: [float(item) for item in (x if isinstance(x, list) else [x])] if x is not None else None,
        'string_array': lambda x: [str(item).strip() for item in (x if isinstance(x, list) else [x])] if x is not None else None,
        'bool_array': lambda x: [str(item).lower() in ('true', '1', 'yes', 'on') if isinstance(item, str) else bool(item) for item in (x if isinstance(x, list) else [x])] if x is not None else None
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
                    elif expected_type == 'array':
                        # Handle array type - convert single values to arrays for backward compatibility
                        if isinstance(value, list):
                            converted_data[field] = value
                        elif value is not None:
                            converted_data[field] = [value]
                        else:
                            converted_data[field] = None
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
    
    def validate_array_element_types(self, data: Dict[str, Any], array_element_types: Dict[str, str]) -> None:
        """
        Validate that array fields contain elements of the specified type.
        
        Args:
            data: Request data dictionary
            array_element_types: Dictionary mapping field names to expected element types
            
        Raises:
            ValidationError: If any array element is invalid
        """
        for field, element_type in array_element_types.items():
            if field in data and data[field] is not None:
                array_value = data[field]
                if not isinstance(array_value, list):
                    raise ValidationError(f"{field} must be an array", field)
                
                for i, element in enumerate(array_value):
                    try:
                        if element_type == 'int':
                            int(element)
                        elif element_type == 'float':
                            float(element)
                        elif element_type == 'string':
                            str(element)
                        elif element_type == 'bool':
                            if isinstance(element, str):
                                str(element).lower() in ('true', '1', 'yes', 'on')
                            else:
                                bool(element)
                    except (ValueError, TypeError):
                        raise ValidationError(f"{field}[{i}] must be a valid {element_type}", field)
    
    def validate_array_element_ranges(self, data: Dict[str, Any], array_element_ranges: Dict[str, Dict[str, Union[int, float]]]) -> None:
        """
        Validate that array elements fall within specified ranges.
        
        Args:
            data: Request data dictionary
            array_element_ranges: Dictionary mapping field names to range constraints for array elements
            
        Raises:
            ValidationError: If any array element is outside the specified range
        """
        for field, constraints in array_element_ranges.items():
            if field in data and data[field] is not None:
                array_value = data[field]
                if not isinstance(array_value, list):
                    raise ValidationError(f"{field} must be an array", field)
                
                for i, element in enumerate(array_value):
                    if not isinstance(element, (int, float)):
                        continue  # Skip non-numeric elements
                    
                    if 'min' in constraints and element < constraints['min']:
                        raise ValidationError(f"{field}[{i}] must be at least {constraints['min']}", field)
                    
                    if 'max' in constraints and element > constraints['max']:
                        raise ValidationError(f"{field}[{i}] must be at most {constraints['max']}", field)
    
    def validate_array_size(self, data: Dict[str, Any], array_size: Dict[str, Dict[str, int]]) -> None:
        """
        Validate that arrays have the specified size constraints.
        
        Args:
            data: Request data dictionary
            array_size: Dictionary mapping field names to size constraints
            
        Raises:
            ValidationError: If any array size constraint is violated
        """
        for field, constraints in array_size.items():
            if field in data and data[field] is not None:
                array_value = data[field]
                if not isinstance(array_value, list):
                    raise ValidationError(f"{field} must be an array", field)
                
                array_len = len(array_value)
                
                if 'min' in constraints and array_len < constraints['min']:
                    raise ValidationError(f"{field} must have at least {constraints['min']} elements", field)
                
                if 'max' in constraints and array_len > constraints['max']:
                    raise ValidationError(f"{field} must have at most {constraints['max']} elements", field)
    
    def validate_array_element_enum_fields(self, data: Dict[str, Any], array_element_enum_fields: Dict[str, type]) -> None:
        """
        Validate that array elements are valid enum values.
        
        Args:
            data: Request data dictionary
            array_element_enum_fields: Dictionary mapping field names to enum classes
            
        Raises:
            ValidationError: If any array element is not a valid enum value
        """
        for field, enum_class in array_element_enum_fields.items():
            if field in data and data[field] is not None:
                array_value = data[field]
                if not isinstance(array_value, list):
                    raise ValidationError(f"{field} must be an array", field)
                
                for i, element in enumerate(array_value):
                    try:
                        if isinstance(element, str):
                            enum_class(element)
                        else:
                            enum_class(element)
                    except ValueError:
                        valid_values = [e.value for e in enum_class]
                        raise ValidationError(f"{field}[{i}] must be one of: {', '.join(valid_values)}", field)
    
    def validate_array_element_choices(self, data: Dict[str, Any], array_element_choices: Dict[str, List[Any]]) -> None:
        """
        Validate that array elements are from allowed choices.
        
        Args:
            data: Request data dictionary
            array_element_choices: Dictionary mapping field names to allowed values
            
        Raises:
            ValidationError: If any array element is not in the allowed choices
        """
        for field, allowed_values in array_element_choices.items():
            if field in data and data[field] is not None:
                array_value = data[field]
                if not isinstance(array_value, list):
                    raise ValidationError(f"{field} must be an array", field)
                
                for i, element in enumerate(array_value):
                    if element not in allowed_values:
                        raise ValidationError(f"{field}[{i}] must be one of: {', '.join(map(str, allowed_values))}", field)

    def validate_array_element_lengths(self, data: Dict[str, Any], array_element_lengths: Dict[str, Dict[str, int]]) -> None:
        """
        Validate that string elements within arrays have the specified length constraints.
        
        Args:
            data: Request data dictionary
            array_element_lengths: Dictionary mapping field names to length constraints for array elements
            
        Raises:
            ValidationError: If any array element length constraint is violated
        """
        for field, constraints in array_element_lengths.items():
            if field in data and data[field] is not None:
                array_value = data[field]
                if not isinstance(array_value, list):
                    raise ValidationError(f"{field} must be an array", field)
                
                for i, element in enumerate(array_value):
                    if isinstance(element, str):
                        element_len = len(element)
                        
                        if 'min' in constraints and element_len < constraints['min']:
                            raise ValidationError(f"{field}[{i}] must be at least {constraints['min']} characters", field)
                        
                        if 'max' in constraints and element_len > constraints['max']:
                            raise ValidationError(f"{field}[{i}] must be at most {constraints['max']} characters", field)

    def validate_mutual_exclusivity(self, data: Dict[str, Any], mutually_exclusive_groups: List[List[str]]) -> None:
        """
        Validate that fields within mutually exclusive groups are not provided together.
        
        Args:
            data: Request data dictionary
            mutually_exclusive_groups: List of lists, where each inner list contains field names
                                     that are mutually exclusive with each other
                                     
        Raises:
            ValidationError: If multiple fields from the same group are provided
            
        Examples:
            # Single group with two fields
            validate_mutual_exclusivity(data, [['currency', 'currencies']])
            
            # Multiple groups
            validate_mutual_exclusivity(data, [
                ['currency', 'currencies'],
                ['rate_type', 'rate_types'],
                ['start_date', 'end_date', 'date_range']
            ])
        """
        for group in mutually_exclusive_groups:
            provided_fields = []
            
            for field in group:
                if field in data and data[field] is not None:
                    provided_fields.append(field)
            
            if len(provided_fields) > 1:
                fields_str = "', '".join(provided_fields)
                raise ValidationError(
                    f"Cannot specify multiple fields from the same group: '{fields_str}'. "
                    f"Choose only one from: {group}"
                )


def _detect_path_parameters() -> List[str]:
    """
    Detect path parameters using Flask's URL rule - single source of truth.
    
    Returns:
        List of parameter names that are path parameters in the current request
    """
    from flask import request
    
    if not request.url_rule:
        return []
    
    # Extract path parameter names from the URL rule
    # Flask's Rule object has a 'arguments' property that contains the parameter names
    path_params = list(request.url_rule.arguments)
    
    return path_params


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
    mutually_exclusive_groups: Optional[List[List[str]]] = None,
    custom_validation: Optional[Callable[[Dict[str, Any]], None]] = None,
    # Array validation parameters
    array_element_types: Optional[Dict[str, str]] = None,
    array_element_ranges: Optional[Dict[str, Dict[str, Union[int, float]]]] = None,
    array_element_lengths: Optional[Dict[str, Dict[str, int]]] = None,
    array_element_enum_fields: Optional[Dict[str, type]] = None,
    array_element_choices: Optional[Dict[str, List[Any]]] = None,
    array_size: Optional[Dict[str, Dict[str, int]]] = None,
    sanitize: bool = True,
    auto_detect_path_params: bool = True
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
        mutually_exclusive_groups: List of lists containing field names that are mutually exclusive
        custom_validation: Custom validation function that takes data dict and raises ValidationError
        # Array validation parameters
        array_element_types: Dictionary mapping field names to expected element types for arrays
        array_element_ranges: Dictionary mapping field names to range constraints for array elements
        array_element_lengths: Dictionary mapping field names to length constraints for array elements
        array_element_enum_fields: Dictionary mapping field names to enum classes for array elements
        array_element_choices: Dictionary mapping field names to allowed values for array elements
        array_size: Dictionary mapping field names to size constraints for arrays
        sanitize: Whether to sanitize string inputs
        auto_detect_path_params: Whether to automatically detect and forbid path parameters
        
    Returns:
        Decorated function with validation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get request data
                # For GET requests, always use query parameters
                if request.method == 'GET':
                    data = dict(request.args)
                elif request.is_json:
                    try:
                        data = request.get_json() or {}
                    except BadRequest:
                        # If JSON parsing fails, treat as empty data
                        # This can happen if Content-Type suggests JSON but body is malformed
                        current_app.logger.warning("Failed to parse JSON body, treating as empty")
                        data = {}
                elif request.form:
                    data = dict(request.form)
                else:
                    # Fallback to query parameters
                    data = dict(request.args)
                
                # Initialize validator
                validator = BaseValidator()
                
                # Auto-detect path parameters if enabled
                if auto_detect_path_params:
                    detected_path_params = _detect_path_parameters()
                    # Merge with manually specified forbidden_fields
                    all_forbidden_fields = (forbidden_fields or []) + detected_path_params
                else:
                    all_forbidden_fields = forbidden_fields
                
                # Apply validations in order
                if required_fields:
                    validator.validate_required_fields(data, required_fields)
                
                if all_forbidden_fields:
                    validator.validate_forbidden_fields(data, all_forbidden_fields)
                
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
                
                # Array element validations (array_element_*)
                if array_element_types:
                    validator.validate_array_element_types(data, array_element_types)
                
                if array_element_ranges:
                    validator.validate_array_element_ranges(data, array_element_ranges)
                
                if array_element_lengths:
                    validator.validate_array_element_lengths(data, array_element_lengths)
                
                if array_element_enum_fields:
                    validator.validate_array_element_enum_fields(data, array_element_enum_fields)
                
                if array_element_choices:
                    validator.validate_array_element_choices(data, array_element_choices)
                
                # Array structure validation (array_size)
                if array_size:
                    validator.validate_array_size(data, array_size)
                
                if json_schema:
                    validator.validate_json_schema(data, json_schema)
                
                if mutually_exclusive_groups:
                    validator.validate_mutual_exclusivity(data, mutually_exclusive_groups)
                
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
                
            except BadRequest as e:
                # Handle Werkzeug BadRequest (e.g., malformed JSON)
                current_app.logger.warning(f"Bad request during validation: {str(e)}")
                return jsonify({
                    "error": "Invalid request format",
                    "type": "validation_error",
                    "details": str(e)
                }), 400
                
            except Exception as e:
                current_app.logger.error(f"Unexpected error during validation: {str(e)}", exc_info=True)
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
