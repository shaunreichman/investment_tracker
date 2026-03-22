"""
Calculator for calculating the PNL of a fund.
"""

from src.fund.models import FundEvent, Fund
from src.fund.enums import FundTrackingType, EventType, DistributionType
from src.fund.calculators.fifo_capital_gains_calculator import FifoCapitalGainsCalculator
from typing import List, Dict

class FundPnlCalculator:
    """
    Fund PNL Calculator.

    This module provides the FundPnlCalculator class, which calculates the PNL of a fund.
    """
    def __init__(self):
        """
        Initialize the FundPnlCalculator.
        
        Args:
            None
        """
        pass

    @staticmethod
    def calculate_pnl(fund_events: List[FundEvent], fund: Fund) -> Dict[str, float]:
        """
        Calculate the PNL of a fund.
        
        Args:
            fund_events: The list of fund events
            fund: The fund object

        Returns:
            Dictionary with the PNL values
        """
        pnl_dict = {
            'pnl': 0,
            'realized_pnl': 0,
            'unrealized_pnl': 0,
            'realized_pnl_capital_gain': None,
            'unrealized_pnl_capital_gain': None,
            'realized_pnl_dividend': 0,
            'realized_pnl_interest': 0,
            'realized_pnl_distribution': 0
        }

        if fund.tracking_type == FundTrackingType.NAV_BASED:
            fifo_capital_gains_calculator = FifoCapitalGainsCalculator()
            capital_gains_dict = fifo_capital_gains_calculator.calculate_capital_gains(fund_events)
            if capital_gains_dict.remaining_units != fund.current_units:
                raise ValueError("Remaining units do not match current units")
            pnl_dict['realized_pnl_capital_gain'] = capital_gains_dict.capital_gains_total
            pnl_dict['unrealized_pnl_capital_gain'] = capital_gains_dict.remaining_units * (fund.current_unit_price - capital_gains_dict.average_cost_per_unit)

        # Sum up the Distribution PNL
        for event in fund_events:
            if event.event_type == EventType.DISTRIBUTION:
                if event.distribution_type == DistributionType.DIVIDEND_FRANKED or \
                        event.distribution_type == DistributionType.DIVIDEND_UNFRANKED:
                    pnl_dict['realized_pnl_dividend'] += event.amount
                elif event.distribution_type == DistributionType.INTEREST:
                    pnl_dict['realized_pnl_interest'] += event.amount
        pnl_dict['realized_pnl_distribution'] = pnl_dict['realized_pnl_dividend'] + pnl_dict['realized_pnl_interest']
        
        # Handle None values for capital gains in cost-based funds
        realized_capital_gain = pnl_dict['realized_pnl_capital_gain'] or 0
        unrealized_capital_gain = pnl_dict['unrealized_pnl_capital_gain'] or 0
        
        pnl_dict['realized_pnl'] = realized_capital_gain + pnl_dict['realized_pnl_distribution']
        pnl_dict['unrealized_pnl'] = unrealized_capital_gain
        pnl_dict['pnl'] = pnl_dict['realized_pnl'] + pnl_dict['unrealized_pnl']
        return pnl_dict

        