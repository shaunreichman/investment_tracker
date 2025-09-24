"""
BankAccountBalanceService is responsible for updating the balance of a bank account.
"""

import logging
from sqlalchemy.orm import Session

class BankAccountBalanceService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def update_bank_account_balance(self, bank_account_id: int, session: Session):
        # We will not update the bank account balance after fund event cash flow updates
        # We will only update the balance on monthly updates (same applies for banks)
        # We will use these fund event cash flows to adjust the monthly balance with cashflows in the wrong month
        pass