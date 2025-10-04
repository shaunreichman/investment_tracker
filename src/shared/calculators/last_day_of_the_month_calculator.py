"""
Last Day of the Month Calculator.
"""

from datetime import date, timedelta

class LastDayOfTheMonthCalculator:
    """
    Last Day of the Month Calculator.
    """
    
    @staticmethod
    def is_last_day_of_the_month(input_date: date) -> bool:
        """
        Check if a given date is the last day of the month.

        Args:
            input_date: Date to check

        Returns:
            True if the date is the last day of the month, False otherwise
        """
        # Calculate the last day of the month
        if input_date.month == 12:
            next_month_first = date(input_date.year + 1, 1, 1)
        else:
            next_month_first = date(input_date.year, input_date.month + 1, 1)
        
        last_day_of_month = next_month_first - timedelta(days=1)
        
        return input_date == last_day_of_month