"""
Fund PNL Service.
"""

from sqlalchemy.orm import Session
from src.fund.models import Fund, FundFieldChange
from src.fund.calculators.fund_pnl_calculator import FundPnlCalculator
from src.fund.repositories import FundEventRepository

class FundPnlService:
    """
    Fund PNL Service.

    This module provides the FundPnlService class, which handles fund PNL operations and business logic.
    The service provides clean separation of concerns for:
    - Update the PNL of a fund
        - Update the PNL of a fund
        - Update the Realized PNL of a fund
        - Update the Unrealized PNL of a fund
        - Update the Realized PNL Capital Gain of a fund
        - Update the Unrealized PNL Capital Gain of a fund
        - Update the Realized PNL Dividend of a fund
        - Update the Realized PNL Interest of a fund
        - Update the Realized PNL Distribution of a fund

    The service uses the FundEventRepository and FundPnlCalculator to perform operations.
    The service is used by the FundEventSecondaryService to update the PNL of a fund.
    """
    def __init__(self):
        """
        Initialize the FundPnlService.
        
        Args:
            fund_event_repository: Fund event repository to use. If None, creates a new one.
        """
        self.fund_event_repository = FundEventRepository()
        self.fund_pnl_calculator = FundPnlCalculator()

    def update_fund_pnl(self, fund: Fund, session: Session):
        """
        Update the PNL of a fund.

        Args:
            fund: The fund object
            session: Database session

        Returns:
            List[FundFieldChange] with updated values and metadata
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

        pnl_dict = self.fund_pnl_calculator.calculate_pnl(fund, session)
        
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