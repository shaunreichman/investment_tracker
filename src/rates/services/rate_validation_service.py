"""
Rate Validation Service.
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import date

from src.shared.calculators.last_day_of_the_month_calculator import LastDayOfTheMonthCalculator

class RateValidationService:
    """
    Rate Validation Service.

    This module provides the RateValidationService class, which handles rate business rule validation.
    The service provides clean separation of concerns for:
    - FX rate creation validation
    """
    
    def __init__(self):
        """
        Initialize the Rate Validation Service.
        """
        self.last_day_of_the_month_calculator = LastDayOfTheMonthCalculator()

    ################################################################################
    # Validate FX Rate Creation
    ################################################################################

    def validate_fx_rate_creation(self, fx_rate_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate the FX rate creation.

        Args:
            fx_rate_data: Data to create an FX rate
            session: Database session

        Returns:
            Dictionary of validation errors
        """
        errors = {}
        
        # Validate fx_rate_data is not None or empty
        if not fx_rate_data:
            errors['data'] = ["FX rate data cannot be empty"]
            return errors
        
        # Validate the FX rate date is the last day of any month
        if 'date' not in fx_rate_data:
            errors['date'] = ["FX rate date is required"]
        else:
            fx_date = fx_rate_data['date']
            if isinstance(fx_date, str):
                fx_date = date.fromisoformat(fx_date)
            
            if not self.last_day_of_the_month_calculator.is_last_day_of_the_month(fx_date):
                errors['date'] = [f"FX rate date must be the last day of the month"]
        
        # Validate the FX rate rate is greater than 0
        if 'fx_rate' not in fx_rate_data:
            errors['fx_rate'] = ["FX rate value is required"]
        elif fx_rate_data['fx_rate'] <= 0:
            errors['fx_rate'] = [f"FX rate must be greater than 0"]
        
        return errors