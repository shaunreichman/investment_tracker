"""
Request Validation Middleware.

This module provides comprehensive request validation including:
- JSON schema validation for request bodies
- Type checking and sanitization
- Required field validation
- Custom validation decorators for routes
- Input sanitization and security checks
- Business rule validation aligned with actual models
"""

import re
import json
from typing import Dict, Any, List, Optional, Union, Callable
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, date

# Import actual enums to ensure validation matches business logic
from src.fund.enums import (
    FundStatus, FundType, EventType, DistributionType, 
    CashFlowDirection, TaxPaymentType, GroupType, TaxJurisdiction, Currency
)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, status_code: int = 400):
        self.message = message
        self.field = field
        self.status_code = status_code
        super().__init__(self.message)


class RequestValidator:
    """
    Request validation engine.
    
    Provides methods for validating request data including:
    - JSON schema validation
    - Type checking and conversion
    - Field validation and sanitization
    - Security checks
    - Business rule validation
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
        'financial_year': r'^\d{4}-\d{2}$'  # e.g., "2023-24"
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
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}", field)
            
            value = data[field]
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValidationError(f"Required field cannot be empty: {field}", field)
    
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
            if field in data:
                value = data[field]
                
                try:
                    if expected_type in self.TYPE_CONVERTERS:
                        converted_data[field] = self.TYPE_CONVERTERS[expected_type](value)
                    else:
                        # For custom types, just validate they exist
                        if not hasattr(value, expected_type):
                            raise ValidationError(f"Invalid type for {field}: expected {expected_type}", field)
                except (ValueError, TypeError) as e:
                    raise ValidationError(f"Invalid {expected_type} value for {field}: {str(e)}", field)
        
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
            if field in data and data[field]:
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
                        converted_data[field] = enum_class(value.upper())
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
                sanitized_data[field] = re.sub(r'[<>"\']', '', value).strip()
        
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


def validate_request(
    required_fields: Optional[List[str]] = None,
    field_types: Optional[Dict[str, str]] = None,
    field_patterns: Optional[Dict[str, str]] = None,
    field_ranges: Optional[Dict[str, Dict[str, Union[int, float]]]] = None,
    field_choices: Optional[Dict[str, List[Any]]] = None,
    enum_fields: Optional[Dict[str, type]] = None,
    json_schema: Optional[Dict[str, Any]] = None,
    sanitize: bool = True
) -> Callable:
    """
    Decorator for validating request data.
    
    Args:
        required_fields: List of required field names
        field_types: Dictionary mapping field names to expected types
        field_patterns: Dictionary mapping field names to pattern names
        field_ranges: Dictionary mapping field names to range constraints
        field_choices: Dictionary mapping field names to allowed values
        enum_fields: Dictionary mapping field names to enum classes
        json_schema: JSON schema for validation
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
                validator = RequestValidator()
                
                # Apply validations
                if required_fields:
                    validator.validate_required_fields(data, required_fields)
                
                if field_types:
                    data = validator.validate_field_types(data, field_types)
                
                if field_patterns:
                    validator.validate_field_patterns(data, field_patterns)
                
                if field_ranges:
                    validator.validate_field_ranges(data, field_ranges)
                
                if field_choices:
                    validator.validate_field_choices(data, field_choices)
                
                if enum_fields:
                    data = validator.validate_enum_values(data, enum_fields)
                
                if json_schema:
                    validator.validate_json_schema(data, json_schema)
                
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


# Convenience decorators for common validation patterns
def validate_bank_data(func: Callable) -> Callable:
    """Validate bank creation/update data."""
    return validate_request(
        required_fields=['name', 'country'],
        field_patterns={'country': 'country_code'},  # Use 2-letter country code pattern
        sanitize=True
    )(func)


def validate_bank_account_data(func: Callable) -> Callable:
    """Validate bank account creation/update data."""
    return validate_request(
        required_fields=['entity_id', 'bank_id', 'account_name', 'account_number', 'currency'],
        enum_fields={'currency': Currency},  # Use enum validation instead of pattern
        sanitize=True
    )(func)


def validate_fund_data(func: Callable) -> Callable:
    """
    Validate fund data for POST/PUT requests.
    
    Validates:
    - Required fields (name, entity_id, investment_company_id, tracking_type)
    - Tracking type validation against FundType enum
    - Fund type validation (optional string field)
    - String field sanitization
    - Optional field validation
    - Business rule validation
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            # Get request data
            data = request.get_json()
            if not data:
                raise ValidationError("No data provided")
            
            # REJECT only the status field that doesn't exist in the model
            old_field_names = ['status']  # Removed 'fund_type' since it exists in the model
            for old_field in old_field_names:
                if old_field in data:
                    raise ValidationError(f"Field '{old_field}' is not valid.", old_field)
            
            # Validate required fields - CORRECTED to match actual model
            required_fields = ['name', 'entity_id', 'investment_company_id', 'tracking_type']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Missing required field: {field}", field)
            
            # Validate and sanitize name
            name = data['name']
            if not isinstance(name, str) or not name.strip():
                raise ValidationError("Name must be a non-empty string", 'name')
            data['name'] = name.strip()
            
            # Validate fund_type if provided (optional string field)
            if 'fund_type' in data and data['fund_type'] is not None:
                fund_type = data['fund_type']
                if not isinstance(fund_type, str) or not fund_type.strip():
                    raise ValidationError("Fund type must be a non-empty string", 'fund_type')
                data['fund_type'] = fund_type.strip()
            
            # Validate tracking_type using actual enum - CORRECTED field name
            try:
                tracking_type = FundType(data['tracking_type'].upper())
                data['tracking_type'] = tracking_type
            except ValueError:
                valid_types = [t.value for t in FundType]
                raise ValidationError(f"Invalid tracking_type. Must be one of: {', '.join(valid_types)}", 'tracking_type')
            
            # Validate entity_id and investment_company_id are positive integers
            try:
                entity_id = int(data['entity_id'])
                if entity_id <= 0:
                    raise ValidationError("Entity ID must be a positive integer", 'entity_id')
                data['entity_id'] = entity_id
            except (ValueError, TypeError):
                raise ValidationError("Entity ID must be a valid integer", 'entity_id')
            
            try:
                investment_company_id = int(data['investment_company_id'])
                if investment_company_id <= 0:
                    raise ValidationError("Investment company ID must be a positive integer", 'investment_company_id')
                data['investment_company_id'] = investment_company_id
            except (ValueError, TypeError):
                raise ValidationError("Investment company ID must be a valid integer", 'investment_company_id')
            
            # Validate optional fields
            if 'description' in data and data['description'] is not None:
                description = data['description']
                if not isinstance(description, str):
                    raise ValidationError("Description must be a string", 'description')
                data['description'] = description.strip() if description.strip() else None
            
            if 'commitment_amount' in data and data['commitment_amount'] is not None:
                try:
                    commitment_amount = float(data['commitment_amount'])
                    if commitment_amount < 0:
                        raise ValidationError("Commitment amount cannot be negative", 'commitment_amount')
                    data['commitment_amount'] = commitment_amount
                except (ValueError, TypeError):
                    raise ValidationError("Commitment amount must be a valid number", 'commitment_amount')
            
            if 'expected_irr' in data and data['expected_irr'] is not None:
                try:
                    expected_irr = float(data['expected_irr'])
                    if expected_irr < 0 or expected_irr > 1000:
                        raise ValidationError("Expected IRR must be between 0 and 1000", 'expected_irr')
                    data['expected_irr'] = expected_irr
                except (ValueError, TypeError):
                    raise ValidationError("Expected IRR must be a valid number", 'expected_irr')
            
            if 'expected_duration_months' in data and data['expected_duration_months'] is not None:
                try:
                    expected_duration = int(data['expected_duration_months'])
                    if expected_duration <= 0:
                        raise ValidationError("Expected duration must be positive", 'expected_duration_months')
                    data['expected_duration_months'] = expected_duration
                except (ValueError, TypeError):
                    raise ValidationError("Expected duration must be a valid integer", 'expected_duration_months')
            
            if 'currency' in data and data['currency'] is not None:
                try:
                    currency = Currency(data['currency'].upper())
                    data['currency'] = currency.value
                except ValueError:
                    valid_currencies = [c.value for c in Currency]
                    raise ValidationError(f"Invalid currency. Must be one of: {', '.join(valid_currencies)}", 'currency')
            
            # Store validated data for controller access
            request.validated_data = data
            
            return func(*args, **kwargs)
            
        except ValidationError as e:
            return jsonify({"error": e.message, "field": e.field}), e.status_code
        except Exception as e:
            current_app.logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": "Validation failed"}), 400
    
    return decorated_function


def validate_entity_data(func: Callable) -> Callable:
    """
    Validate entity data for POST/PUT requests.
    
    Validates:
    - Required fields (name) - CORRECTED: only name is required
    - Tax jurisdiction validation against TaxJurisdiction enum
    - String field sanitization
    - Optional field validation
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            # Get request data
            data = request.get_json()
            if not data:
                raise ValidationError("No data provided")
            
            # Validate required fields - CORRECTED: only name is required
            required_fields = ['name']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Missing required field: {field}", field)
            
            # Validate and sanitize name
            name = data['name']
            if not isinstance(name, str) or not name.strip():
                raise ValidationError("Name must be a non-empty string", 'name')
            data['name'] = name.strip()
            
            # Validate tax_jurisdiction using actual enum
            if 'tax_jurisdiction' in data and data['tax_jurisdiction'] is not None:
                try:
                    tax_jurisdiction = TaxJurisdiction(data['tax_jurisdiction'].upper())
                    data['tax_jurisdiction'] = tax_jurisdiction.value
                except ValueError:
                    valid_jurisdictions = [j.value for j in TaxJurisdiction]
                    raise ValidationError(f"Invalid tax_jurisdiction. Must be one of: {', '.join(valid_jurisdictions)}", 'tax_jurisdiction')
            
            # Validate optional fields
            if 'description' in data and data['description'] is not None:
                description = data['description']
                if not isinstance(description, str):
                    raise ValidationError("Description must be a string", 'description')
                data['description'] = description.strip()
            
            # Store validated data for controller access
            request.validated_data = data
            
            return func(*args, **kwargs)
            
        except ValidationError as e:
            return jsonify({"error": e.message, "field": e.field}), e.status_code
        except Exception as e:
            current_app.logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": "Validation failed"}), 400
    
    return decorated_function


def validate_tax_statement_data(func: Callable) -> Callable:
    """
    Validate tax statement data for POST/PUT requests.
    
    Validates:
    - Required fields (fund_id, entity_id, financial_year) - CORRECTED
    - Date format validation
    - Numeric field validation (non-negative)
    - Percentage field validation (0-100%)
    - Business rule validation
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            # Get request data
            data = request.get_json()
            if not data:
                raise ValidationError("No data provided")
            
            # Validate required fields - CORRECTED to match actual model
            required_fields = ['fund_id', 'entity_id', 'financial_year']
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValidationError(f"Missing required field: {field}", field)
            
            # Validate fund_id is positive integer
            try:
                fund_id = int(data['fund_id'])
                if fund_id <= 0:
                    raise ValidationError("Fund ID must be a positive integer", 'fund_id')
                data['fund_id'] = fund_id
            except (ValueError, TypeError):
                raise ValidationError("Fund ID must be a valid integer", 'fund_id')
            
            # Validate entity_id is positive integer
            try:
                entity_id = int(data['entity_id'])
                if entity_id <= 0:
                    raise ValidationError("Entity ID must be a positive integer", 'entity_id')
                data['entity_id'] = entity_id
            except (ValueError, TypeError):
                raise ValidationError("Entity ID must be a valid integer", 'entity_id')
            
            # Validate financial_year format
            financial_year = data['financial_year']
            if not isinstance(financial_year, str) or not re.match(r'^\d{4}-\d{2}$', financial_year):
                raise ValidationError("Financial year must be in format YYYY-YY (e.g., 2023-24)", 'financial_year')
            
            # Validate optional date fields
            if 'statement_date' in data and data['statement_date'] is not None:
                statement_date = data['statement_date']
                if isinstance(statement_date, str):
                    try:
                        parsed_date = datetime.strptime(statement_date, '%Y-%m-%d').date()
                        data['statement_date'] = parsed_date
                    except ValueError:
                        raise ValidationError("Invalid statement date format. Use YYYY-MM-DD", 'statement_date')
                elif not isinstance(statement_date, date):
                    raise ValidationError("Statement date must be a valid date", 'statement_date')
            
            if 'tax_payment_date' in data and data['tax_payment_date'] is not None:
                tax_payment_date = data['tax_payment_date']
                if isinstance(tax_payment_date, str):
                    try:
                        parsed_date = datetime.strptime(tax_payment_date, '%Y-%m-%d').date()
                        data['tax_payment_date'] = parsed_date
                    except ValueError:
                        raise ValidationError("Invalid tax payment date format. Use YYYY-MM-DD", 'tax_payment_date')
                elif not isinstance(tax_payment_date, date):
                    raise ValidationError("Tax payment date must be a valid date", 'tax_payment_date')
            
            # Validate numeric fields (non-negative)
            numeric_fields = [
                'eofy_debt_interest_deduction_rate',
                'interest_received_in_cash',
                'interest_receivable_this_fy',
                'interest_receivable_prev_fy',
                'interest_non_resident_withholding_tax_from_statement',
                'interest_income_tax_rate',
                'dividend_franked_income_amount',
                'dividend_unfranked_income_amount',
                'dividend_franked_income_tax_rate',
                'dividend_unfranked_income_tax_rate',
                'capital_gain_income_amount',
                'capital_gain_income_tax_rate'
            ]
            
            for field in numeric_fields:
                value = data.get(field)
                if value is not None:
                    try:
                        float_value = float(value)
                        if float_value < 0:
                            raise ValidationError(f"{field.replace('_', ' ').title()} must be non-negative", field)
                        data[field] = float_value
                    except (ValueError, TypeError):
                        raise ValidationError(f"{field.replace('_', ' ').title()} must be a valid number", field)
            
            # Validate percentage fields (0-100%)
            percentage_fields = [
                'eofy_debt_interest_deduction_rate',
                'interest_income_tax_rate',
                'dividend_franked_income_tax_rate',
                'dividend_unfranked_income_tax_rate',
                'capital_gain_income_tax_rate'
            ]
            
            for field in percentage_fields:
                value = data.get(field)
                if value is not None:
                    if not (0 <= float(value) <= 100):
                        raise ValidationError(f"{field.replace('_', ' ').title()} must be between 0 and 100", field)
            
            # Validate boolean fields - CORRECTED boolean validation
            if 'non_resident' in data and data['non_resident'] is not None:
                if not isinstance(data['non_resident'], bool):
                    try:
                        # Handle string boolean values correctly
                        if isinstance(data['non_resident'], str):
                            data['non_resident'] = data['non_resident'].lower() in ('true', '1', 'yes', 'on')
                        else:
                            data['non_resident'] = bool(data['non_resident'])
                    except (ValueError, TypeError):
                        raise ValidationError("Non-resident must be a valid boolean value", 'non_resident')
            
            # Store validated data for controller access
            request.validated_data = data
            
            return func(*args, **kwargs)
            
        except ValidationError as e:
            return jsonify({"error": e.message, "field": e.field}), e.status_code
        except Exception as e:
            current_app.logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": "Validation failed"}), 400
    
    return decorated_function


def validate_fund_event_data(func: Callable) -> Callable:
    """
    Validate fund event data before processing.
    
    Validates:
    - Required fields: event_type, event_date
    - Field types and ranges
    - Business logic constraints
    - Event type validation against actual enum
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            # Get request data
            data = request.get_json()
            if not data:
                raise ValidationError("No data provided")
            
            # Validate required fields
            required_fields = ['event_type', 'event_date']
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValidationError(f"Missing required field: {field}", field)
            
            # Validate event_type using actual enum - CORRECTED
            try:
                event_type = EventType(data['event_type'].upper())
                data['event_type'] = event_type
            except ValueError:
                valid_event_types = [e.value for e in EventType]
                raise ValidationError(f"Invalid event_type. Must be one of: {', '.join(valid_event_types)}", 'event_type')
            
            # Validate event_date format
            event_date = data['event_date']
            if isinstance(event_date, str):
                try:
                    parsed_date = datetime.strptime(event_date, '%Y-%m-%d').date()
                    data['event_date'] = parsed_date
                except ValueError:
                    raise ValidationError("Invalid event_date format. Use YYYY-MM-DD", 'event_date')
            elif not isinstance(event_date, date):
                raise ValidationError("Event date must be a valid date", 'event_date')
            
            # Validate amount - CORRECTED: allow negative for certain event types
            if 'amount' in data and data['amount'] is not None:
                try:
                    amount = float(data['amount'])
                    # Allow negative amounts for certain event types (e.g., returns, distributions)
                    data['amount'] = amount
                except (ValueError, TypeError):
                    raise ValidationError("Amount must be a valid number", 'amount')
            
            # Validate optional numeric fields
            numeric_fields = ['units_purchased', 'units_sold', 'unit_price', 'nav_per_share', 'brokerage_fee']
            for field in numeric_fields:
                value = data.get(field)
                if value is not None:
                    try:
                        float_value = float(value)
                        if float_value < 0:
                            raise ValidationError(f"{field.replace('_', ' ').title()} must be non-negative", field)
                        data[field] = float_value
                    except (ValueError, TypeError):
                        raise ValidationError(f"{field.replace('_', ' ').title()} must be a valid number", field)
            
            # Validate distribution_type if present
            if 'distribution_type' in data and data['distribution_type'] is not None:
                try:
                    distribution_type = DistributionType(data['distribution_type'].upper())
                    data['distribution_type'] = distribution_type
                except ValueError:
                    valid_distribution_types = [d.value for d in DistributionType]
                    raise ValidationError(f"Invalid distribution_type. Must be one of: {', '.join(valid_distribution_types)}", 'distribution_type')
            
            # Validate tax_payment_type if present
            if 'tax_payment_type' in data and data['tax_payment_type'] is not None:
                try:
                    tax_payment_type = TaxPaymentType(data['tax_payment_type'].upper())
                    data['tax_payment_type'] = tax_payment_type
                except ValueError:
                    valid_tax_payment_types = [t.value for t in TaxPaymentType]
                    raise ValidationError(f"Invalid tax_payment_type. Must be one of: {', '.join(valid_tax_payment_types)}", 'tax_payment_type')
            
            # Validate description length
            if 'description' in data and data['description']:
                if len(data['description']) > 500:
                    raise ValidationError("Description must be 500 characters or less", 'description')
            
            # Store validated data for controller access
            request.validated_data = data
            
            return func(*args, **kwargs)
            
        except ValidationError as e:
            return jsonify({"error": e.message, "field": e.field}), e.status_code
        except Exception as e:
            current_app.logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": "Validation failed"}), 400
    
    return decorated_function


def validate_cash_flow_data(func: Callable) -> Callable:
    """
    Validate cash flow data before processing.
    
    Validates:
    - Required fields: bank_account_id, transfer_date, currency, amount
    - Field types and ranges
    - Business logic constraints
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            # Get request data
            data = request.get_json()
            if not data:
                raise ValidationError("No data provided")
            
            # Validate required fields
            required_fields = ['bank_account_id', 'transfer_date', 'currency', 'amount']
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValidationError(f"Missing required field: {field}", field)
            
            # Validate bank_account_id is integer
            try:
                bank_account_id = int(data['bank_account_id'])
                if bank_account_id <= 0:
                    raise ValidationError("Bank account ID must be a positive integer", 'bank_account_id')
                data['bank_account_id'] = bank_account_id
            except (ValueError, TypeError):
                raise ValidationError("Bank account ID must be a valid integer", 'bank_account_id')
            
            # Validate transfer_date format
            transfer_date = data['transfer_date']
            if isinstance(transfer_date, str):
                try:
                    parsed_date = datetime.strptime(transfer_date, '%Y-%m-%d').date()
                    data['transfer_date'] = parsed_date
                except ValueError:
                    raise ValidationError("Invalid transfer_date format. Use YYYY-MM-DD", 'transfer_date')
            elif not isinstance(transfer_date, date):
                raise ValidationError("Transfer date must be a valid date", 'transfer_date')
            
            # Validate currency format using actual enum
            try:
                currency = Currency(data['currency'].upper())
                data['currency'] = currency.value
            except ValueError:
                valid_currencies = [c.value for c in Currency]
                raise ValidationError(f"Invalid currency. Must be one of: {', '.join(valid_currencies)}", 'currency')
            
            # Validate amount is numeric and non-zero
            try:
                amount = float(data['amount'])
                if amount == 0:
                    raise ValidationError("Amount cannot be zero", 'amount')
                data['amount'] = amount
            except (ValueError, TypeError):
                raise ValidationError("Amount must be a valid number", 'amount')
            
            # Validate optional fields
            if 'reference' in data and data['reference']:
                if len(data['reference']) > 100:
                    raise ValidationError("Reference must be 100 characters or less", 'reference')
            
            if 'notes' in data and data['notes']:
                if len(data['notes']) > 1000:
                    raise ValidationError("Notes must be 1000 characters or less", 'notes')
            
            # Store validated data for controller access
            request.validated_data = data
            
            return func(*args, **kwargs)
            
        except ValidationError as e:
            return jsonify({"error": e.message, "field": e.field}), e.status_code
        except Exception as e:
            current_app.logger.error(f"Validation error: {str(e)}")
            return jsonify({"error": "Validation failed"}), 400
    
    return decorated_function


def validate_investment_company_data(func: Callable) -> Callable:
    """
    Validate investment company data before processing.
    
    Validates:
    - Required fields: name
    - Field types and ranges
    - Business logic constraints
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            current_app.logger.info("🔍 validate_investment_company_data: Starting validation")
            
            # Get request data
            data = request.get_json()
            current_app.logger.info(f"📥 validate_investment_company_data: Received data: {data}")
            
            if not data:
                current_app.logger.warning("❌ validate_investment_company_data: No data provided")
                raise ValidationError("No data provided")
            
            # Validate required fields
            required_fields = ['name']
            current_app.logger.info(f"🔍 validate_investment_company_data: Validating required fields: {required_fields}")
            
            for field in required_fields:
                if field not in data or not data[field]:
                    current_app.logger.warning(f"❌ validate_investment_company_data: Missing required field: {field}")
                    raise ValidationError(f"Missing required field: {field}", field)
            
            # Validate name length and format
            name = data['name'].strip()
            current_app.logger.info(f"🔍 validate_investment_company_data: Validating name: '{name}'")
            
            if len(name) > 255:
                current_app.logger.warning(f"❌ validate_investment_company_data: Name too long: {len(name)} characters")
                raise ValidationError("Company name must be 255 characters or less", 'name')
            if len(name) < 2:
                current_app.logger.warning(f"❌ validate_investment_company_data: Name too short: {len(name)} characters")
                raise ValidationError("Company name must be at least 2 characters", 'name')
            data['name'] = name
            
            # Validate optional fields
            if 'description' in data and data['description']:
                if len(data['description']) > 65535:  # Text field limit
                    current_app.logger.warning(f"❌ validate_investment_company_data: Description too long: {len(data['description'])} characters")
                    raise ValidationError("Description must be 65535 characters or less", 'description')
            
            if 'company_type' in data and data['company_type']:
                if len(data['company_type']) > 100:
                    current_app.logger.warning(f"❌ validate_investment_company_data: Company type too long: {len(data['company_type'])} characters")
                    raise ValidationError("Company type must be 100 characters or less", 'company_type')
            
            if 'business_address' in data and data['business_address']:
                if len(data['business_address']) > 65535:  # Text field limit
                    current_app.logger.warning(f"❌ validate_investment_company_data: Business address too long: {len(data['business_address'])} characters")
                    raise ValidationError("Business address must be 65535 characters or less", 'business_address')
            
            if 'website' in data and data['website']:
                if len(data['website']) > 255:
                    current_app.logger.warning(f"❌ validate_investment_company_data: Website too long: {len(data['website'])} characters")
                    raise ValidationError("Website must be 255 characters or less", 'website')
                # Basic URL validation
                if not data['website'].startswith(('http://', 'https://')):
                    data['website'] = 'https://' + data['website']
                    current_app.logger.info(f"🔧 validate_investment_company_data: Added https:// to website: {data['website']}")
            
            current_app.logger.info(f"✅ validate_investment_company_data: Validation passed, storing validated data")
            
            # Store validated data for controller access
            request.validated_data = data
            
            current_app.logger.info("🚀 validate_investment_company_data: Calling controller function")
            return func(*args, **kwargs)
            
        except ValidationError as e:
            current_app.logger.warning(f"❌ validate_investment_company_data: Validation error: {e.message} for field: {e.field}")
            return jsonify({"error": e.message, "field": e.field}), e.status_code
        except Exception as e:
            current_app.logger.error(f"❌ validate_investment_company_data: Unexpected error: {str(e)}")
            return jsonify({"error": "Validation failed"}), 400
    
    return decorated_function
