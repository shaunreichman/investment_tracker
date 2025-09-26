"""
Example usage of the new validation structure.

This file shows how to use the base validator and domain-specific
validation decorators in your route files.
"""

# Example 1: Using the generic validate_request decorator
from src.api.middleware.validation.base_validation import validate_request
from src.shared.enums.shared_enums import Country

def example_entity_creation_route():
    """Example of using validate_request directly."""
    
    @validate_request(
        required_fields=['name'],
        field_types={'name': 'string', 'description': 'string'},
        field_lengths={'name': {'min': 2, 'max': 255}},
        enum_fields={'tax_jurisdiction': Country},
        sanitize=True
    )
    def create_entity():
        # Your route logic here
        pass


# Example 2: Using domain-specific validation decorators
from src.api.middleware.validation.entity_validation import validate_entity_creation

def example_entity_route_with_domain_validation():
    """Example of using domain-specific validation."""
    
    @validate_entity_creation
    def create_entity():
        # Your route logic here
        # request.validated_data will contain the validated and sanitized data
        pass


# Example 3: Using convenience functions
from src.api.middleware.validation.base_validation import (
    validate_required_string,
    validate_required_integer,
    validate_required_enum
)

def example_convenience_functions():
    """Example of using convenience validation functions."""
    
    @validate_required_string('name', min_length=2, max_length=255)
    @validate_required_integer('entity_id', min_value=1)
    @validate_required_enum('tax_jurisdiction', Country)
    def create_entity():
        # Your route logic here
        pass


# Example 4: Complex validation with multiple rules
def example_complex_validation():
    """Example of complex validation with multiple rules."""
    
    @validate_request(
        required_fields=['name', 'entity_id', 'investment_company_id'],
        field_types={
            'name': 'string',
            'entity_id': 'int',
            'investment_company_id': 'int',
            'commitment_amount': 'float',
            'expected_irr': 'float'
        },
        field_lengths={'name': {'min': 2, 'max': 255}},
        field_ranges={
            'entity_id': {'min': 1},
            'investment_company_id': {'min': 1},
            'commitment_amount': {'min': 0},
            'expected_irr': {'min': 0, 'max': 1000}
        },
        positive_numbers=['entity_id', 'investment_company_id'],
        non_negative_numbers=['commitment_amount', 'expected_irr'],
        enum_fields={'tax_jurisdiction': Country},
        sanitize=True
    )
    def create_fund():
        # Your route logic here
        pass
