"""
Shared IRR Calculators Utilities.

This module contains pure IRR calculation logic that can be reused
across different domains (fund, company, etc.).
"""

from typing import List, Optional


class IRRCalculator:
    """Pure IRR calculator utility - shared across fund and company calculations."""
    
    
    @staticmethod
    def calculate_irr(cash_flows: List[float], days_from_start: List[int], tolerance: float = 1e-6, max_iterations: int = 200) -> Optional[float]:
        """
        Calculate annual IRR using monthly compounding with the Newton-Raphson method.
        
        Args:
            cash_flows: List of cash flow amounts (negative for outflows, positive for inflows)
            days_from_start: List of days from the start date for each cash flow
            tolerance: Convergence tolerance for the root-finding algorithm
            max_iterations: Maximum number of iterations to attempt
        
        Returns:
            float or None: The annual IRR as a decimal, or None if not computable
        """

        is_valid = IRRCalculator._validate_cash_flows(cash_flows, days_from_start)
        if not is_valid:
            return None

        # Initial guess: 10% return
        monthly_guess = 0.01

        # Calculate IRR using Newton-Raphson method
        for iteration in range(max_iterations):
            npv = 0
            derivative = 0
            for i, (cf, days) in enumerate(zip(cash_flows, days_from_start)):
                # Use monthly compounding for investment fund accuracy
                months = days / 30.44  # Average days per month
                discount_factor = (1 + monthly_guess) ** months
                npv += cf / discount_factor
                if months > 0:
                    derivative -= cf * months / (discount_factor * (1 + monthly_guess))
            if abs(npv) < tolerance:
                # Convert monthly IRR to annual IRR
                annual_irr = (1 + monthly_guess) ** 12 - 1
                return annual_irr
            if abs(derivative) < 1e-12:
                break
            monthly_guess = monthly_guess - npv / derivative
            if monthly_guess < -0.99 or monthly_guess > 2.0:
                return None
        return None
    
    @staticmethod
    def _validate_cash_flows(cash_flows: List[float], days_from_start: List[int]) -> bool:
        """
        Validate cash flows for IRR calculation.
        
        Args:
            cash_flows: List of cash flow amounts
            days_from_start: List of days from the start date for each cash flow
            
        Returns:
            bool: True if cash flows are valid for IRR calculation
        """
        if len(cash_flows) != len(days_from_start):
            return False
        
        if len(cash_flows) < 2:
            return False
        
        # Check for at least one positive and one negative cash flow
        has_positive = any(cf > 0 for cf in cash_flows)
        has_negative = any(cf < 0 for cf in cash_flows)
        
        if not (has_positive and has_negative):
            return False
        
        # Check for valid days
        if any(days < 0 for days in days_from_start):
            return False
        
        return True
