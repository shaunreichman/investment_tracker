"""
Calculator for calculating the PNL of a fund.
"""

from src.fund.models import Fund
from src.fund.enums import FundType, EventType, DistributionType
from src.fund.calculators.fifo_capital_gains_calculator import FifoCapitalGainsCalculator
from src.fund.repositories import FundEventRepository
from sqlalchemy.orm import Session


class FundPnlCalculator:
    def __init__(self, session: Session):
        self.fund_event_repository = FundEventRepository(session)

    def calculate_pnl(self, fund: Fund, session: Session):
        pnl_dict = {}
        pnl_dict['pnl'] = 0
        pnl_dict['realized_pnl'] = 0
        pnl_dict['unrealized_pnl'] = 0
        pnl_dict['realized_pnl_capital_gain'] = None
        pnl_dict['unrealized_pnl_capital_gain'] = None
        pnl_dict['realized_pnl_dividend'] = 0
        pnl_dict['realized_pnl_interest'] = 0
        pnl_dict['realized_pnl_distribution'] = 0

        events = self.fund_event_repository.get_by_fund(fund.id, session)

        if fund.tracking_type == FundType.NAV_BASED:
            fifo_capital_gains_calculator = FifoCapitalGainsCalculator(session)
            capital_gains_dict = fifo_capital_gains_calculator.calculate_capital_gains(events)
            if capital_gains_dict.remaining_units != fund.current_units:
                ValueError("Remaining units do not match current units")
            pnl_dict['realized_pnl_capital_gain'] = capital_gains_dict.total_capital_gains
            pnl_dict['unrealized_pnl_capital_gain'] = capital_gains_dict.remaining_units * (fund.current_unit_price - capital_gains_dict.average_cost_per_unit)

        # Sum up the Distribution PNL
        for event in events:
            if event.event_type == EventType.DISTRIBUTION:
                if event.distribution_type == DistributionType.DIVIDEND_FRANKED or \
                        event.distribution_type == DistributionType.DIVIDEND_UNFRANKED:
                    pnl_dict['realized_pnl_dividend'] += event.amount
                elif event.distribution_type == DistributionType.INTEREST:
                    pnl_dict['realized_pnl_interest'] += event.amount
        pnl_dict['realized_pnl_distribution'] = pnl_dict['realized_pnl_dividend'] + pnl_dict['realized_pnl_interest']
        pnl_dict['realized_pnl'] = pnl_dict['realized_pnl_capital_gain'] + pnl_dict['realized_pnl_distribution']
        pnl_dict['unrealized_pnl'] = pnl_dict['unrealized_pnl_capital_gain']
        pnl_dict['pnl'] = pnl_dict['realized_pnl'] + pnl_dict['unrealized_pnl']
        return pnl_dict

        