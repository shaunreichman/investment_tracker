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

    
    @staticmethod
    def get_last_day_of_the_month(input_date: date) -> date:
        """
        Get the last day of the month for a given date.

        Args:
            input_date: Date to get the last day of the month for

        Returns:
            date: The last day of the month containing the input date
        """
        # Calculate the first day of the next month, then subtract one day
        if input_date.month == 12:
            next_month_first = date(input_date.year + 1, 1, 1)
        else:
            next_month_first = date(input_date.year, input_date.month + 1, 1)
        
        return next_month_first - timedelta(days=1)