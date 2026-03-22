"""
Bank Account Balance Adjustment Service.
"""

from src.banking.models import BankAccountBalance
from sqlalchemy.orm import Session
from src.shared.models import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.shared.services.domain_update_event_service import DomainUpdateEventService
from src.fund.repositories.fund_event_cash_flow_repository import FundEventCashFlowRepository
from datetime import timedelta, date

class BankAccountBalanceAdjustmentService:
    """
    Bank Account Balance Adjustment Service.
    """
    def __init__(self):
        self.domain_update_event_service = DomainUpdateEventService()
        self.fund_event_cash_flow_repository = FundEventCashFlowRepository()
        
    def calculate_bank_account_balance_adjustment(self, bank_account_balance: BankAccountBalance, session: Session) -> list[DomainFieldChange]:
        """
        Calculate the balance adjustment for a bank account balance.
        """
        # 1. Get the fund event cash flows
        start_date_to_check = bank_account_balance.date.replace(day=1) # Start of the month
        # End of the next month
        year = start_date_to_check.year
        month = start_date_to_check.month + 2
        if month > 12:
            year += 1
            month -= 12
        end_date_to_check = date(year, month, 1) - timedelta(days=1)

        fund_event_cash_flows = self.fund_event_cash_flow_repository.get_fund_event_cash_flows(session,
                    bank_account_ids=[bank_account_balance.bank_account_id],
                    different_month=True,
                    start_fund_event_date=start_date_to_check,
                    end_fund_event_date=end_date_to_check,
                    start_transfer_date=start_date_to_check,
                    end_transfer_date=end_date_to_check)

        all_changes: list[DomainFieldChange] = []

        old_balance_adjustment = bank_account_balance.balance_adjustment
        old_balance_final = bank_account_balance.balance_final
        new_balance_adjustment = 0

        if fund_event_cash_flows:
            for fund_event_cash_flow in fund_event_cash_flows:
                # Determine if the Cash Flow date and Fund Event date are in different months
                if fund_event_cash_flow.fund_event_date.month != fund_event_cash_flow.transfer_date.month:
                    # Check if the Cash Flow date is before the Bank Account Balance date
                    if fund_event_cash_flow.transfer_date > fund_event_cash_flow.fund_event_date:
                        new_balance_adjustment -= fund_event_cash_flow.amount
                    else:
                        new_balance_adjustment += fund_event_cash_flow.amount

                    # Update the Fund Event Cash Flow with the Bank Account Balance ID
                    old_bank_account_balance_id = fund_event_cash_flow.adjusted_bank_account_balance_id
                    if old_bank_account_balance_id != bank_account_balance.id:
                        fund_event_cash_flow.adjusted_bank_account_balance_id = bank_account_balance.id
                        all_changes.append(DomainFieldChange(DomainObjectType.FUND_EVENT_CASH_FLOW, fund_event_cash_flow.id, 'adjusted_bank_account_balance_id', old_bank_account_balance_id, bank_account_balance.id))

                else:
                    continue

        new_balance_final = bank_account_balance.balance_statement + new_balance_adjustment

        if old_balance_adjustment != new_balance_adjustment:
            bank_account_balance.balance_adjustment = new_balance_adjustment
            all_changes.append(DomainFieldChange(DomainObjectType.BANK_ACCOUNT_BALANCE, bank_account_balance.id, 'balance_adjustment', old_balance_adjustment, new_balance_adjustment))

        if old_balance_final != new_balance_final:
            bank_account_balance.balance_final = new_balance_final
            all_changes.append(DomainFieldChange(DomainObjectType.BANK_ACCOUNT_BALANCE, bank_account_balance.id, 'balance_final', old_balance_final, new_balance_final))

        return all_changes