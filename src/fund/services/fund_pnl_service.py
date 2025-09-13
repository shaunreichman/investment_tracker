"""
Service for handling fund PNL calculations.
"""

from sqlalchemy.orm import Session
from src.fund.models import Fund, FundFieldChange
import logging

class FundPnlService:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def update_fund_pnl(self, fund: Fund, session: Session):
        """
        Update the PNL of a fund.
        """
        old_pnl = fund.pnl
        old_realized_pnl = fund.realized_pnl
        old_unrealized_pnl = fund.unrealized_pnl
        old_realized_pnl_capital_gain = fund.realized_pnl_capital_gain
        old_unrealized_pnl_capital_gain = fund.unrealized_pnl_capital_gain
        old_realized_pnl_dividend = fund.realized_pnl_dividend
        old_realized_pnl_interest = fund.realized_pnl_interest
        old_realized_pnl_distribution = fund.realized_pnl_distribution

        all_changes = []

        from src.fund.calculators.fund_pnl_calculator import FundPnlCalculator
        pnl_dict = FundPnlCalculator.calculate_pnl(fund, session)
        
        if pnl_dict['pnl'] != old_pnl:
            fund.pnl = pnl_dict['pnl']
            all_changes.append(FundFieldChange(field_name='pnl', old_value=old_pnl, new_value=pnl_dict['pnl']))
        if pnl_dict['realized_pnl'] != old_realized_pnl:
            fund.realized_pnl = pnl_dict['realized_pnl']
            all_changes.append(FundFieldChange(field_name='realized_pnl', old_value=old_realized_pnl, new_value=pnl_dict['realized_pnl']))
        if pnl_dict['unrealized_pnl'] != old_unrealized_pnl:
            fund.unrealized_pnl = pnl_dict['unrealized_pnl']
            all_changes.append(FundFieldChange(field_name='unrealized_pnl', old_value=old_unrealized_pnl, new_value=pnl_dict['unrealized_pnl']))
        if pnl_dict['realized_pnl_capital_gain'] != old_realized_pnl_capital_gain:
            fund.realized_pnl_capital_gain = pnl_dict['realized_pnl_capital_gain']
            all_changes.append(FundFieldChange(field_name='realized_pnl_capital_gain', old_value=old_realized_pnl_capital_gain, new_value=pnl_dict['realized_pnl_capital_gain']))
        if pnl_dict['unrealized_pnl_capital_gain'] != old_unrealized_pnl_capital_gain:
            fund.unrealized_pnl_capital_gain = pnl_dict['unrealized_pnl_capital_gain']
            all_changes.append(FundFieldChange(field_name='unrealized_pnl_capital_gain', old_value=old_unrealized_pnl_capital_gain, new_value=pnl_dict['unrealized_pnl_capital_gain']))
        if pnl_dict['realized_pnl_dividend'] != old_realized_pnl_dividend:
            fund.realized_pnl_dividend = pnl_dict['realized_pnl_dividend']
            all_changes.append(FundFieldChange(field_name='realized_pnl_dividend', old_value=old_realized_pnl_dividend, new_value=pnl_dict['realized_pnl_dividend']))
        if pnl_dict['realized_pnl_interest'] != old_realized_pnl_interest:
            fund.realized_pnl_interest = pnl_dict['realized_pnl_interest']
            all_changes.append(FundFieldChange(field_name='realized_pnl_interest', old_value=old_realized_pnl_interest, new_value=pnl_dict['realized_pnl_interest']))
        if pnl_dict['realized_pnl_distribution'] != old_realized_pnl_distribution:
            fund.realized_pnl_distribution = pnl_dict['realized_pnl_distribution']
            all_changes.append(FundFieldChange(field_name='realized_pnl_distribution', old_value=old_realized_pnl_distribution, new_value=pnl_dict['realized_pnl_distribution']))

        return all_changes if all_changes else None