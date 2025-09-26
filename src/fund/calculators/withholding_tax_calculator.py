"""
Withholding Tax Calculator

Pure calculation logic for withholding tax computations.
Handles complex tax calculations for distributions with withholding.
"""

from typing import Tuple
from decimal import Decimal


class WithholdingTaxCalculator:
    """Calculator for withholding tax amounts and distributions"""
    
    @staticmethod
    def calculate_withholding_tax_amounts(
        gross_interest_amount: float = None,
        net_interest_amount: float = None,
        withholding_tax_amount: float = None,
        withholding_tax_rate: float = None
    ) -> Tuple[float, float]:
        """
        Calculate withholding tax amounts for distributions.
        
        Args:
            gross_interest_amount: Gross amount before withholding
            net_interest_amount: Net amount after withholding
            withholding_tax_amount: Specific tax amount to withhold
            withholding_tax_rate: Tax rate as percentage (e.g., 15.0 for 15%)
            
        Returns:
            Tuple of (gross_amount, tax_amount)
            
        Raises:
            ValueError: If insufficient parameters provided
        """
        # Validate input parameters
        if not any([gross_interest_amount, net_interest_amount, withholding_tax_amount]):
            raise ValueError("At least one amount parameter must be provided")
        
        if withholding_tax_rate is not None and not (0 <= withholding_tax_rate <= 100):
            raise ValueError("Withholding tax rate must be between 0 and 100")
        
        # Case 1: Gross amount + tax rate provided
        if gross_interest_amount is not None and withholding_tax_rate is not None:
            gross_amount = float(gross_interest_amount)
            tax_rate_decimal = withholding_tax_rate / 100.0
            tax_amount = gross_amount * tax_rate_decimal
            net_amount = gross_amount - tax_amount
            
            return gross_amount, tax_amount
        
        # Case 2: Net amount + tax rate provided
        elif net_interest_amount is not None and withholding_tax_rate is not None:
            net_amount = float(net_interest_amount)
            tax_rate_decimal = withholding_tax_rate / 100.0
            # Calculate gross: net / (1 - tax_rate)
            gross_amount = net_amount / (1 - tax_rate_decimal)
            tax_amount = gross_amount - net_amount
            
            return gross_amount, tax_amount
        
        # Case 3: Gross amount + specific tax amount provided
        elif gross_interest_amount is not None and withholding_tax_amount is not None:
            gross_amount = float(gross_interest_amount)
            tax_amount = float(withholding_tax_amount)
            net_amount = gross_amount - tax_amount
            
            return gross_amount, tax_amount
        
        # Case 4: Net amount + specific tax amount provided
        elif net_interest_amount is not None and withholding_tax_amount is not None:
            net_amount = float(net_interest_amount)
            tax_amount = float(withholding_tax_amount)
            gross_amount = net_amount + tax_amount
            
            return gross_amount, tax_amount
        
        # Case 5: Only gross amount provided (no withholding)
        elif gross_interest_amount is not None:
            gross_amount = float(gross_interest_amount)
            return gross_amount, 0.0
        
        # Case 6: Only net amount provided (no withholding)
        elif net_interest_amount is not None:
            net_amount = float(net_interest_amount)
            return net_amount, 0.0
        
        # Case 7: Only tax amount provided (invalid - need context)
        else:
            raise ValueError("Tax amount alone is insufficient - provide gross or net amount")
    
