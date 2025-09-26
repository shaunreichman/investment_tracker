"""
Fund Event Validation Functions.

This module provides custom validation functions for fund event creation,
handling event-type-specific validation rules.
"""

from src.api.middleware.validation.base_validation import ValidationError


def validate_distribution_data(data: dict) -> None:
    """
    Custom validation for distribution events.
    
    Validates both simple distributions and withholding tax distributions
    based on the fields provided in the request.
    
    Args:
        data: Validated request data
        
    Raises:
        ValidationError: If validation fails
    """
    # Check if this is a withholding tax distribution
    if data.get('has_withholding_tax'):
        # Validate withholding tax distribution
        validate_withholding_tax_distribution(data)
    else:
        # Validate simple distribution
        validate_simple_distribution(data)


def validate_withholding_tax_distribution(data: dict) -> None:
    """
    Validate withholding tax distribution fields.
    
    For withholding tax distributions, we need:
    - Exactly one of gross_amount or net_amount
    - Exactly one of withholding_tax_amount or withholding_tax_rate
    
    Args:
        data: Request data
        
    Raises:
        ValidationError: If validation fails
    """
    # Must have exactly one of gross_amount or net_amount
    gross_amount = data.get('gross_amount')
    net_amount = data.get('net_amount')
    
    if (gross_amount is not None and net_amount is not None) or \
       (gross_amount is None and net_amount is None):
        raise ValidationError(
            "Withholding tax distributions must have exactly one of: gross_amount or net_amount",
            'gross_amount'
        )
    
    # Must have exactly one of withholding_tax_amount or withholding_tax_rate
    tax_amount = data.get('withholding_tax_amount')
    tax_rate = data.get('withholding_tax_rate')
    
    if (tax_amount is not None and tax_rate is not None) or \
       (tax_amount is None and tax_rate is None):
        raise ValidationError(
            "Withholding tax distributions must have exactly one of: withholding_tax_amount or withholding_tax_rate",
            'withholding_tax_amount'
        )
    
    if 'amount' in data:
        raise ValidationError("Withholding tax distributions should not have amount field", 'amount')


def validate_simple_distribution(data: dict) -> None:
    """
    Validate simple distribution fields.
    
    For simple distributions, we need:
    - An amount field
    
    Args:
        data: Request data
        
    Raises:
        ValidationError: If validation fails
    """
    if 'amount' not in data or data['amount'] is None:
        raise ValidationError("Simple distributions require an amount field", 'amount')
    
    if 'gross_amount' in data or 'net_amount' in data or 'withholding_tax_amount' in data or 'withholding_tax_rate' in data:
        raise ValidationError("Simple distributions should not have withholding tax fields", 'withholding_tax')
