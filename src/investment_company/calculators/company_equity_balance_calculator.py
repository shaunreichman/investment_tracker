"""
Company Equity Balance Calculator.
"""

from typing import List, Tuple
from datetime import date

from src.fund.models import FundEvent

class CompanyEquityBalanceCalculator:
    """
    Company Equity Balance Calculator.
    """

    @staticmethod
    def calculate_company_equity_balance(fund_events: List[FundEvent]) -> Tuple[float, float, date]:
        """
        Calculate the equity balance for a company.

        Args:
            fund_events: List of sorted fund events

        Returns:
            Average equity balance, current equity balance, last event date
        """
        if not fund_events:
            return 0.0, 0.0, None

        today = date.today()
        fund_balances = {}
        company_balance = 0.0
        total_weighted_balance = 0.0
        last_event_date = None

        # Process each event in order
        for i in range(len(fund_events) - 1):
            event = fund_events[i]
            next_event = fund_events[i + 1]
            last_event_date = next_event.event_date

            # Update balances for this event
            fund_id = event.fund_id
            new_balance = event.current_equity_balance or 0.0  # Handle None values
            old_balance = fund_balances.get(fund_id, 0.0)
            company_balance += new_balance - old_balance
            fund_balances[fund_id] = new_balance

            # Weight by days until next event
            days = (next_event.event_date - event.event_date).days
            total_weighted_balance += company_balance * days

        # Handle last event → today
        last_event = fund_events[-1]
        last_event_date = last_event.event_date
        fund_id = last_event.fund_id
        new_balance = last_event.current_equity_balance or 0.0  # Handle None values
        old_balance = fund_balances.get(fund_id, 0.0)
        company_balance += new_balance - old_balance
        fund_balances[fund_id] = new_balance

        # Only extend to today if the last event is not in the future and balance is not zero
        if company_balance != 0 and last_event.event_date <= today:
            days = (today - last_event.event_date).days
            if days > 0:
                total_weighted_balance += company_balance * days
            last_event_date = today

        # Total days = first_event → last_event_date (either today or last event date if balance is 0)
        total_days = (last_event_date - fund_events[0].event_date).days
        average_equity_balance = total_weighted_balance / total_days if total_days > 0 else 0.0

        return average_equity_balance, company_balance, last_event_date