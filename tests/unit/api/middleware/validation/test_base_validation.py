"""
Test suite for base validation utilities.

This module tests all validation parameters and methods in the base validation system,
including field validation, array element validation, and array size validation.
"""

import pytest
from unittest.mock import Mock, patch
from flask import Flask, request
from datetime import date, datetime

from src.api.middleware.validation.base_validation import (
    validate_request, 
    BaseValidator, 
    ValidationError,
    validate_required_string,
    validate_optional_string,
    validate_required_integer,
    validate_required_float,
    validate_required_enum,
    validate_optional_enum,
    _detect_path_parameters
)


class TestBaseValidator:
    """Test the BaseValidator class methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = BaseValidator()
        self.test_data = {
            'name': 'John Doe',
            'age': 25,
            'price': 99.99,
            'email': 'john@example.com',
            'phone': '+1234567890',
            'date_str': '2023-12-25',
            'company_ids': [1, 2, 3, 4, 5],
            'names': ['John', 'Jane', 'Bob'],
            'prices': [10.5, 20.0, 30.75]
        }

    def test_validate_required_fields_success(self):
        """Test successful required field validation."""
        required_fields = ['name', 'age']
        self.validator.validate_required_fields(self.test_data, required_fields)
        # Should not raise any exception

    def test_validate_required_fields_missing(self):
        """Test required field validation with missing fields."""
        required_fields = ['name', 'age', 'missing_field']
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_required_fields(self.test_data, required_fields)
        assert "Missing required fields: missing_field" in str(exc_info.value)

    def test_validate_required_fields_empty(self):
        """Test required field validation with empty fields."""
        data = {'name': '', 'age': 25}
        required_fields = ['name', 'age']
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_required_fields(data, required_fields)
        assert "Required fields cannot be empty: name" in str(exc_info.value)

    def test_validate_forbidden_fields_success(self):
        """Test successful forbidden field validation."""
        forbidden_fields = ['secret_field', 'admin_data']
        self.validator.validate_forbidden_fields(self.test_data, forbidden_fields)
        # Should not raise any exception

    def test_validate_forbidden_fields_present(self):
        """Test forbidden field validation with present forbidden fields."""
        data = {'name': 'John', 'secret_field': 'secret'}
        forbidden_fields = ['secret_field']
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_forbidden_fields(data, forbidden_fields)
        assert "Forbidden fields must not be included: secret_field" in str(exc_info.value)

    def test_validate_field_types_success(self):
        """Test successful field type validation and conversion."""
        field_types = {
            'name': 'string',
            'age': 'int',
            'price': 'float',
            'is_active': 'bool'
        }
        data = {
            'name': 'John',
            'age': '25',  # String that should be converted to int
            'price': '99.99',  # String that should be converted to float
            'is_active': 'true'  # String that should be converted to bool
        }
        result = self.validator.validate_field_types(data, field_types)
        
        assert result['name'] == 'John'
        assert result['age'] == 25
        assert result['price'] == 99.99
        assert result['is_active'] is True

    def test_validate_field_types_invalid(self):
        """Test field type validation with invalid types."""
        field_types = {'age': 'int'}
        data = {'age': 'not_a_number'}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_field_types(data, field_types)
        assert "Invalid int value for 'age'" in str(exc_info.value)

    def test_validate_field_ranges_success(self):
        """Test successful field range validation."""
        field_ranges = {
            'age': {'min': 18, 'max': 65},
            'price': {'min': 0, 'max': 1000}
        }
        self.validator.validate_field_ranges(self.test_data, field_ranges)
        # Should not raise any exception

    def test_validate_field_ranges_min_violation(self):
        """Test field range validation with minimum violation."""
        field_ranges = {'age': {'min': 30}}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_field_ranges(self.test_data, field_ranges)
        assert "age must be at least 30" in str(exc_info.value)

    def test_validate_field_ranges_max_violation(self):
        """Test field range validation with maximum violation."""
        field_ranges = {'age': {'max': 20}}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_field_ranges(self.test_data, field_ranges)
        assert "age must be at most 20" in str(exc_info.value)

    def test_validate_field_choices_success(self):
        """Test successful field choice validation."""
        field_choices = {
            'status': ['active', 'inactive', 'pending']
        }
        data = {'status': 'active'}
        self.validator.validate_field_choices(data, field_choices)
        # Should not raise any exception

    def test_validate_field_choices_invalid(self):
        """Test field choice validation with invalid choice."""
        field_choices = {'status': ['active', 'inactive']}
        data = {'status': 'invalid'}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_field_choices(data, field_choices)
        assert "Invalid value for status" in str(exc_info.value)

    def test_validate_string_length_success(self):
        """Test successful string length validation."""
        field_lengths = {
            'name': {'min': 2, 'max': 50}
        }
        self.validator.validate_string_length(self.test_data, field_lengths)
        # Should not raise any exception

    def test_validate_string_length_too_short(self):
        """Test string length validation with too short string."""
        field_lengths = {'name': {'min': 10}}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_string_length(self.test_data, field_lengths)
        assert "name must be at least 10 characters" in str(exc_info.value)

    def test_validate_string_length_too_long(self):
        """Test string length validation with too long string."""
        field_lengths = {'name': {'max': 5}}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_string_length(self.test_data, field_lengths)
        assert "name must be at most 5 characters" in str(exc_info.value)

    def test_validate_positive_numbers_success(self):
        """Test successful positive number validation."""
        positive_fields = ['age', 'price']
        self.validator.validate_positive_numbers(self.test_data, positive_fields)
        # Should not raise any exception

    def test_validate_positive_numbers_negative(self):
        """Test positive number validation with negative numbers."""
        data = {'age': -5}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_positive_numbers(data, ['age'])
        assert "age must be a positive number" in str(exc_info.value)

    def test_validate_non_negative_numbers_success(self):
        """Test successful non-negative number validation."""
        data = {'age': 0, 'count': 5}
        non_negative_fields = ['age', 'count']
        self.validator.validate_non_negative_numbers(data, non_negative_fields)
        # Should not raise any exception

    def test_validate_non_negative_numbers_negative(self):
        """Test non-negative number validation with negative numbers."""
        data = {'age': -1}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_non_negative_numbers(data, ['age'])
        assert "age must be a non-negative number" in str(exc_info.value)

    def test_validate_array_element_types_success(self):
        """Test successful array element type validation."""
        array_element_types = {
            'company_ids': 'int',
            'names': 'string'
        }
        self.validator.validate_array_element_types(self.test_data, array_element_types)
        # Should not raise any exception

    def test_validate_array_element_types_invalid(self):
        """Test array element type validation with invalid types."""
        array_element_types = {'company_ids': 'string'}
        # The validation actually converts integers to strings, so this should not raise an error
        # Let's test with a truly invalid case - non-convertible types
        data = {'mixed_array': [1, None, 'valid_string']}
        array_element_types = {'mixed_array': 'int'}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_array_element_types(data, array_element_types)
        assert "mixed_array[1] must be a valid int" in str(exc_info.value)

    def test_validate_array_element_ranges_success(self):
        """Test successful array element range validation."""
        array_element_ranges = {
            'company_ids': {'min': 1, 'max': 10},
            'prices': {'min': 0, 'max': 100}
        }
        self.validator.validate_array_element_ranges(self.test_data, array_element_ranges)
        # Should not raise any exception

    def test_validate_array_element_ranges_min_violation(self):
        """Test array element range validation with minimum violation."""
        array_element_ranges = {'company_ids': {'min': 5}}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_array_element_ranges(self.test_data, array_element_ranges)
        assert "company_ids[0] must be at least 5" in str(exc_info.value)

    def test_validate_array_element_lengths_success(self):
        """Test successful array element length validation."""
        array_element_lengths = {
            'names': {'min': 2, 'max': 10}
        }
        self.validator.validate_array_element_lengths(self.test_data, array_element_lengths)
        # Should not raise any exception

    def test_validate_array_element_lengths_too_long(self):
        """Test array element length validation with too long string."""
        array_element_lengths = {'names': {'max': 2}}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_array_element_lengths(self.test_data, array_element_lengths)
        assert "names[0] must be at most 2 characters" in str(exc_info.value)

    def test_validate_array_size_success(self):
        """Test successful array size validation."""
        array_size = {
            'company_ids': {'min': 1, 'max': 10},
            'names': {'min': 2, 'max': 5}
        }
        self.validator.validate_array_size(self.test_data, array_size)
        # Should not raise any exception

    def test_validate_array_size_too_small(self):
        """Test array size validation with too few elements."""
        array_size = {'names': {'min': 5}}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_array_size(self.test_data, array_size)
        assert "names must have at least 5 elements" in str(exc_info.value)

    def test_validate_array_size_too_large(self):
        """Test array size validation with too many elements."""
        array_size = {'names': {'max': 2}}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_array_size(self.test_data, array_size)
        assert "names must have at most 2 elements" in str(exc_info.value)

    def test_validate_array_element_choices_success(self):
        """Test successful array element choice validation."""
        array_element_choices = {
            'names': ['John', 'Jane', 'Bob', 'Alice']
        }
        self.validator.validate_array_element_choices(self.test_data, array_element_choices)
        # Should not raise any exception

    def test_validate_array_element_choices_invalid(self):
        """Test array element choice validation with invalid choice."""
        array_element_choices = {'names': ['John', 'Jane']}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_array_element_choices(self.test_data, array_element_choices)
        assert "names[2] must be one of: John, Jane" in str(exc_info.value)

    def test_sanitize_strings(self):
        """Test string sanitization."""
        data = {
            'name': 'John<script>alert("xss")</script>',
            'description': 'Safe text',
            'email': 'test@example.com'
        }
        result = self.validator.sanitize_strings(data)
        
        # The actual sanitization removes <, >, ", ', and control characters
        assert result['name'] == 'Johnscriptalert(xss)/script'
        assert result['description'] == 'Safe text'
        assert result['email'] == 'test@example.com'

    def test_validate_mutual_exclusivity_success(self):
        """Test successful mutual exclusivity validation."""
        mutually_exclusive_groups = [['name', 'names']]
        data = {'name': 'John'}
        self.validator.validate_mutual_exclusivity(data, mutually_exclusive_groups)
        # Should not raise any exception

    def test_validate_mutual_exclusivity_violation(self):
        """Test mutual exclusivity validation with violation."""
        mutually_exclusive_groups = [['name', 'names']]
        data = {'name': 'John', 'names': ['Jane', 'Bob']}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_mutual_exclusivity(data, mutually_exclusive_groups)
        assert "Cannot specify multiple fields from the same group" in str(exc_info.value)


class TestValidateRequestDecorator:
    """Test the validate_request decorator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_validate_request_success(self):
        """Test successful validation with all parameter types."""
        @self.app.route('/test', methods=['POST'])
        @validate_request(
            required_fields=['name', 'age'],
            forbidden_fields=['secret'],
            field_types={
                'name': 'string',
                'age': 'int',
                'price': 'float',
                'is_active': 'bool'
            },
            field_ranges={
                'age': {'min': 18, 'max': 65},
                'price': {'min': 0}
            },
            field_lengths={
                'name': {'min': 2, 'max': 50}
            },
            field_choices={
                'status': ['active', 'inactive']
            },
            positive_numbers=['age'],
            enum_fields={},
            array_element_types={
                'tags': 'string'
            },
            array_element_ranges={
                'scores': {'min': 0, 'max': 100}
            },
            array_element_lengths={
                'tags': {'max': 20}
            },
            array_size={
                'tags': {'max': 5}
            },
            array_element_choices={
                'categories': ['tech', 'business', 'finance']
            },
            sanitize=True
        )
        def test_endpoint():
            return {'message': 'success'}

        # Test with valid data
        response = self.client.post('/test', json={
            'name': 'John Doe',
            'age': 25,
            'price': 99.99,
            'is_active': True,
            'status': 'active',
            'tags': ['tech', 'finance'],
            'scores': [85, 92, 78],
            'categories': ['tech', 'business']
        })
        
        assert response.status_code == 200
        assert response.get_json()['message'] == 'success'

    def test_validate_request_missing_required(self):
        """Test validation with missing required fields."""
        @self.app.route('/test', methods=['POST'])
        @validate_request(required_fields=['name', 'age'])
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'name': 'John'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing required fields' in data['error']

    def test_validate_request_forbidden_field(self):
        """Test validation with forbidden field present."""
        @self.app.route('/test', methods=['POST'])
        @validate_request(forbidden_fields=['secret'])
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'secret': 'value'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Forbidden fields must not be included' in data['error']

    def test_validate_request_invalid_type(self):
        """Test validation with invalid field type."""
        @self.app.route('/test', methods=['POST'])
        @validate_request(field_types={'age': 'int'})
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'age': 'not_a_number'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid int value' in data['error']

    def test_validate_request_range_violation(self):
        """Test validation with range violation."""
        @self.app.route('/test', methods=['POST'])
        @validate_request(field_ranges={'age': {'min': 18, 'max': 65}})
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'age': 70})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'age must be at most 65' in data['error']

    def test_validate_request_length_violation(self):
        """Test validation with string length violation."""
        @self.app.route('/test', methods=['POST'])
        @validate_request(field_lengths={'name': {'min': 5}})
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'name': 'John'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'name must be at least 5 characters' in data['error']

    def test_validate_request_array_size_violation(self):
        """Test validation with array size violation."""
        @self.app.route('/test', methods=['POST'])
        @validate_request(array_size={'tags': {'max': 2}})
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'tags': ['a', 'b', 'c']})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'tags must have at most 2 elements' in data['error']

    def test_validate_request_array_element_range_violation(self):
        """Test validation with array element range violation."""
        @self.app.route('/test', methods=['POST'])
        @validate_request(array_element_ranges={'scores': {'min': 0, 'max': 100}})
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'scores': [85, 150, 78]})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'scores[1] must be at most 100' in data['error']

    def test_validate_request_mutual_exclusivity_violation(self):
        """Test validation with mutual exclusivity violation."""
        @self.app.route('/test', methods=['POST'])
        @validate_request(
            mutually_exclusive_groups=[['name', 'names']]
        )
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={
            'name': 'John',
            'names': ['Jane', 'Bob']
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Cannot specify multiple fields from the same group' in data['error']

    def test_validate_request_custom_validation(self):
        """Test validation with custom validation function."""
        def custom_validation(data):
            if 'name' in data and data['name'] == 'forbidden':
                raise ValidationError("Name cannot be 'forbidden'", 'name')

        @self.app.route('/test', methods=['POST'])
        @validate_request(custom_validation=custom_validation)
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'name': 'forbidden'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert "Name cannot be 'forbidden'" in data['error']


class TestConvenienceFunctions:
    """Test the convenience validation functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_validate_required_string_success(self):
        """Test successful required string validation."""
        @self.app.route('/test', methods=['POST'])
        @validate_required_string('name', min_length=2, max_length=50)
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'name': 'John Doe'})
        assert response.status_code == 200

    def test_validate_required_string_missing(self):
        """Test required string validation with missing field."""
        @self.app.route('/test', methods=['POST'])
        @validate_required_string('name')
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={})
        assert response.status_code == 400

    def test_validate_required_string_too_short(self):
        """Test required string validation with too short string."""
        @self.app.route('/test', methods=['POST'])
        @validate_required_string('name', min_length=5)
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'name': 'John'})
        assert response.status_code == 400

    def test_validate_optional_string_success(self):
        """Test successful optional string validation."""
        @self.app.route('/test', methods=['POST'])
        @validate_optional_string('description', max_length=100)
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'description': 'Test description'})
        assert response.status_code == 200

    def test_validate_optional_string_missing(self):
        """Test optional string validation with missing field."""
        @self.app.route('/test', methods=['POST'])
        @validate_optional_string('description')
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={})
        assert response.status_code == 200  # Should succeed when field is missing

    def test_validate_required_integer_success(self):
        """Test successful required integer validation."""
        @self.app.route('/test', methods=['POST'])
        @validate_required_integer('age', min_value=18)
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'age': 25})
        assert response.status_code == 200

    def test_validate_required_integer_too_small(self):
        """Test required integer validation with value too small."""
        @self.app.route('/test', methods=['POST'])
        @validate_required_integer('age', min_value=18)
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'age': 16})
        assert response.status_code == 400

    def test_validate_required_float_success(self):
        """Test successful required float validation."""
        @self.app.route('/test', methods=['POST'])
        @validate_required_float('price', min_value=0.0)
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'price': 99.99})
        assert response.status_code == 200

    def test_validate_required_enum_success(self):
        """Test successful required enum validation."""
        from enum import Enum
        
        class Status(Enum):
            ACTIVE = 'active'
            INACTIVE = 'inactive'
        
        @self.app.route('/test', methods=['POST'])
        @validate_required_enum('status', Status)
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'status': 'active'})
        assert response.status_code == 200

    def test_validate_optional_enum_success(self):
        """Test successful optional enum validation."""
        from enum import Enum
        
        class Status(Enum):
            ACTIVE = 'active'
            INACTIVE = 'inactive'
        
        @self.app.route('/test', methods=['POST'])
        @validate_optional_enum('status', Status)
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={'status': 'active'})
        assert response.status_code == 200

    def test_validate_optional_enum_missing(self):
        """Test optional enum validation with missing field."""
        from enum import Enum
        
        class Status(Enum):
            ACTIVE = 'active'
            INACTIVE = 'inactive'
        
        @self.app.route('/test', methods=['POST'])
        @validate_optional_enum('status', Status)
        def test_endpoint():
            return {'message': 'success'}

        response = self.client.post('/test', json={})
        assert response.status_code == 200  # Should succeed when field is missing


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = BaseValidator()

    def test_validate_field_types_none_value(self):
        """Test field type validation with None values."""
        field_types = {'optional_field': 'string'}
        data = {'optional_field': None}
        result = self.validator.validate_field_types(data, field_types)
        assert result['optional_field'] is None

    def test_validate_field_ranges_none_value(self):
        """Test field range validation with None values."""
        field_ranges = {'optional_field': {'min': 0}}
        data = {'optional_field': None}
        self.validator.validate_field_ranges(data, field_ranges)
        # Should not raise any exception for None values

    def test_validate_array_element_ranges_non_numeric(self):
        """Test array element range validation with non-numeric elements."""
        array_element_ranges = {'mixed_array': {'min': 0}}
        data = {'mixed_array': [1, 'not_a_number', 3]}
        self.validator.validate_array_element_ranges(data, array_element_ranges)
        # Should skip non-numeric elements without error

    def test_validate_array_element_lengths_non_string(self):
        """Test array element length validation with non-string elements."""
        array_element_lengths = {'mixed_array': {'max': 10}}
        data = {'mixed_array': ['string', 123, 'short']}  # Changed to avoid length violation
        self.validator.validate_array_element_lengths(data, array_element_lengths)
        # Should skip non-string elements without error

    def test_validate_array_size_empty_array(self):
        """Test array size validation with empty array."""
        array_size = {'empty_array': {'min': 0}}
        data = {'empty_array': []}
        self.validator.validate_array_size(data, array_size)
        # Should not raise any exception for empty array

    def test_validate_array_size_none_value(self):
        """Test array size validation with None value."""
        array_size = {'optional_array': {'min': 0}}
        data = {'optional_array': None}
        self.validator.validate_array_size(data, array_size)
        # Should not raise any exception for None values

    def test_validate_field_patterns_success(self):
        """Test successful field pattern validation."""
        field_patterns = {
            'email': 'email',
            'phone': 'phone'
        }
        data = {
            'email': 'test@example.com',
            'phone': '+1234567890'
        }
        self.validator.validate_field_patterns(data, field_patterns)
        # Should not raise any exception

    def test_validate_field_patterns_invalid(self):
        """Test field pattern validation with invalid pattern."""
        field_patterns = {'email': 'email'}
        data = {'email': 'invalid_email'}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_field_patterns(data, field_patterns)
        assert "Invalid email format for email" in str(exc_info.value)

    def test_validate_enum_values_success(self):
        """Test successful enum validation."""
        from enum import Enum
        
        class Status(Enum):
            ACTIVE = 'active'
            INACTIVE = 'inactive'
        
        enum_fields = {'status': Status}
        data = {'status': 'active'}
        result = self.validator.validate_enum_values(data, enum_fields)
        assert result['status'] == Status.ACTIVE

    def test_validate_enum_values_invalid(self):
        """Test enum validation with invalid value."""
        from enum import Enum
        
        class Status(Enum):
            ACTIVE = 'active'
            INACTIVE = 'inactive'
        
        enum_fields = {'status': Status}
        data = {'status': 'invalid'}
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_enum_values(data, enum_fields)
        assert "Invalid status" in str(exc_info.value)


class TestPathParameterDetection:
    """Test automatic path parameter detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_detect_path_parameters_single_param(self):
        """Test detection of single path parameter."""
        @self.app.route('/api/banks/<int:bank_id>')
        def test_route(bank_id):
            with self.app.test_request_context('/api/banks/123'):
                params = _detect_path_parameters()
                assert params == ['bank_id']
                return 'OK'

        with self.app.test_client() as client:
            response = client.get('/api/banks/123')
            assert response.status_code == 200

    def test_detect_path_parameters_multiple_params(self):
        """Test detection of multiple path parameters."""
        @self.app.route('/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>')
        def test_route(bank_id, bank_account_id):
            with self.app.test_request_context('/api/banks/123/bank-accounts/456'):
                params = _detect_path_parameters()
                # Check that both parameters are detected (order may vary)
                assert set(params) == {'bank_id', 'bank_account_id'}
                assert len(params) == 2
                return 'OK'

        with self.app.test_client() as client:
            response = client.get('/api/banks/123/bank-accounts/456')
            assert response.status_code == 200

    def test_detect_path_parameters_no_params(self):
        """Test detection with no path parameters."""
        @self.app.route('/api/banks')
        def test_route():
            with self.app.test_request_context('/api/banks'):
                params = _detect_path_parameters()
                assert params == []
                return 'OK'

        with self.app.test_client() as client:
            response = client.get('/api/banks')
            assert response.status_code == 200

    def test_detect_path_parameters_no_url_rule(self):
        """Test detection when no URL rule is available."""
        with self.app.test_request_context():
            # Mock request.url_rule to be None
            with patch('flask.request.url_rule', None):
                params = _detect_path_parameters()
                assert params == []

    def test_validate_request_auto_detect_path_params_enabled(self):
        """Test validate_request with automatic path parameter detection enabled."""
        @self.app.route('/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>', methods=['GET'])
        @validate_request(
            field_types={'include_balances': 'bool'},
            auto_detect_path_params=True  # Explicitly enable (this is the default)
        )
        def test_route(bank_id, bank_account_id):
            return {'bank_id': bank_id, 'bank_account_id': bank_account_id}

        # Test valid request (no conflicting parameters)
        response = self.client.get('/api/banks/123/bank-accounts/456')
        assert response.status_code == 200
        data = response.get_json()
        assert data['bank_id'] == 123
        assert data['bank_account_id'] == 456

        # Test invalid request (bank_id in query params - should be forbidden)
        response = self.client.get('/api/banks/123/bank-accounts/456?bank_id=999')
        assert response.status_code == 400
        data = response.get_json()
        assert 'Forbidden fields must not be included: bank_id' in data['error']

        # Test invalid request (bank_account_id in query params - should be forbidden)
        response = self.client.get('/api/banks/123/bank-accounts/456?bank_account_id=999')
        assert response.status_code == 400
        data = response.get_json()
        assert 'Forbidden fields must not be included: bank_account_id' in data['error']

    def test_validate_request_auto_detect_path_params_disabled(self):
        """Test validate_request with automatic path parameter detection disabled."""
        @self.app.route('/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>', methods=['GET'])
        @validate_request(
            field_types={'include_balances': 'bool'},
            auto_detect_path_params=False  # Disable automatic detection
        )
        def test_route(bank_id, bank_account_id):
            return {'bank_id': bank_id, 'bank_account_id': bank_account_id}

        # Test request with bank_id in query params - should be allowed when auto-detection is disabled
        response = self.client.get('/api/banks/123/bank-accounts/456?bank_id=999')
        assert response.status_code == 200
        data = response.get_json()
        assert data['bank_id'] == 123  # Path parameter takes precedence
        assert data['bank_account_id'] == 456

    def test_validate_request_manual_forbidden_fields_with_auto_detect(self):
        """Test validate_request with both manual forbidden fields and auto-detection."""
        @self.app.route('/api/banks/<int:bank_id>/bank-accounts/<int:bank_account_id>', methods=['GET'])
        @validate_request(
            forbidden_fields=['secret_field'],  # Manual forbidden field
            field_types={'include_balances': 'bool'},
            auto_detect_path_params=True
        )
        def test_route(bank_id, bank_account_id):
            return {'bank_id': bank_id, 'bank_account_id': bank_account_id}

        # Test valid request
        response = self.client.get('/api/banks/123/bank-accounts/456')
        assert response.status_code == 200

        # Test invalid request (manual forbidden field)
        response = self.client.get('/api/banks/123/bank-accounts/456?secret_field=value')
        assert response.status_code == 400
        data = response.get_json()
        assert 'Forbidden fields must not be included: secret_field' in data['error']

        # Test invalid request (auto-detected forbidden field)
        response = self.client.get('/api/banks/123/bank-accounts/456?bank_id=999')
        assert response.status_code == 400
        data = response.get_json()
        assert 'Forbidden fields must not be included: bank_id' in data['error']

    def test_validate_request_different_route_patterns(self):
        """Test automatic path parameter detection with different route patterns."""
        # Test with string parameters
        @self.app.route('/api/entities/<entity_name>/accounts/<account_name>', methods=['GET'])
        @validate_request(field_types={'include_details': 'bool'})
        def test_string_params(entity_name, account_name):
            return {'entity_name': entity_name, 'account_name': account_name}

        # Test valid request
        response = self.client.get('/api/entities/test-entity/accounts/test-account')
        assert response.status_code == 200
        data = response.get_json()
        assert data['entity_name'] == 'test-entity'
        assert data['account_name'] == 'test-account'

        # Test invalid request (entity_name in query params)
        response = self.client.get('/api/entities/test-entity/accounts/test-account?entity_name=conflict')
        assert response.status_code == 400
        data = response.get_json()
        assert 'Forbidden fields must not be included: entity_name' in data['error']

    def test_validate_request_post_with_path_params(self):
        """Test automatic path parameter detection with POST requests."""
        @self.app.route('/api/banks/<int:bank_id>/bank-accounts', methods=['POST'])
        @validate_request(
            required_fields=['account_name'],
            field_types={'account_name': 'string', 'balance': 'float'}
        )
        def test_post_route(bank_id):
            return {'bank_id': bank_id, 'message': 'created'}

        # Test valid POST request
        response = self.client.post('/api/banks/123/bank-accounts', 
                                  json={'account_name': 'Test Account', 'balance': 1000.0})
        assert response.status_code == 200
        data = response.get_json()
        assert data['bank_id'] == 123

        # Test invalid POST request (bank_id in JSON body)
        response = self.client.post('/api/banks/123/bank-accounts', 
                                  json={'account_name': 'Test Account', 'bank_id': 999})
        assert response.status_code == 400
        data = response.get_json()
        assert 'Forbidden fields must not be included: bank_id' in data['error']


if __name__ == '__main__':
    pytest.main([__file__])
