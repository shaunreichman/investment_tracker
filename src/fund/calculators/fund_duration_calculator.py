"""
Fund Duration Calculator.

Pure mathematical calculation logic for fund duration operations.
"""

from datetime import date


class FundDurationCalculator:
    """Pure mathematical calculation logic for fund duration operations."""
    
    @staticmethod
    def calculate_duration_months(start_date: date, end_date: date) -> int:
        """Calculate duration in months between two dates.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            int: Duration in months (always >= 0)
        """
        # Calculate months between start and end dates
        year_diff = end_date.year - start_date.year
        month_diff = end_date.month - start_date.month
        
        total_months = year_diff * 12 + month_diff
        
        # Adjust for day of month
        if end_date.day < start_date.day:
            total_months -= 1
        
        return max(0, total_months)
