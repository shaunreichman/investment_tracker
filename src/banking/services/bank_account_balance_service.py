"""
Bank Account Balance Service.
"""

from datetime import date, timedelta
from src.banking.repositories.bank_account_balance_repository import BankAccountBalanceRepository
from src.banking.repositories.bank_account_repository import BankAccountRepository
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from src.shared.enums.shared_enums import Currency, SortOrder
from src.banking.enums.bank_account_balance_enums import SortFieldBankAccountBalance
from src.banking.models import BankAccountBalance
from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.services.bank_account_balance_adjustment_service import BankAccountBalanceAdjustmentService
from src.shared.services.domain_update_event_service import DomainUpdateEventService
from src.shared.models import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.shared.enums.shared_enums import EventOperation

class BankAccountBalanceService:
    """
    Bank Account Balance Service.

    This service is responsible for bank account balance operations and business logic.
    The service provides clean separation of concerns for:
    - Bank account balance retrieval
    - Bank account balance creation
    - Bank account balance deletion
    """

    def __init__(self):
        """
        Initialize the bank account balance service.

        Args:
            None
        """
        self.bank_account_balance_repository = BankAccountBalanceRepository()
        self.bank_account_repository = BankAccountRepository()
        self.banking_validation_service = BankingValidationService()
        self.bank_account_balance_adjustment_service = BankAccountBalanceAdjustmentService()
        self.domain_update_event_service = DomainUpdateEventService()

    ################################################################################
    # Get Bank Account Balance
    ################################################################################

    def get_bank_account_balances(self, session: Session,
            bank_ids: Optional[List[int]] = None,
            bank_account_ids: Optional[List[int]] = None,
            currencies: Optional[List[Currency]] = None,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            sort_by: Optional[SortFieldBankAccountBalance] = SortFieldBankAccountBalance.DATE,
            sort_order: Optional[SortOrder] = SortOrder.ASC
    ) -> List[BankAccountBalance]:
        """
        Get all bank account balances.
        
        Args:
            session: Database session
            bank_ids: IDs of the bank to filter by (optional)
            bank_account_ids: IDs of the bank account to filter by (optional)
            currencies: Currencies of the bank account balances to filter by (optional)
            start_date: Start date of the bank account balances to filter by (optional)
            end_date: End date of the bank account balances to filter by (optional)
            sort_by: Sort field (optional)
            sort_order: Sort order (optional)

        Returns:
            List of bank account balances
        """
        return self.bank_account_balance_repository.get_bank_account_balances(session, bank_ids, bank_account_ids, currencies, start_date, end_date, sort_by, sort_order)

    def get_bank_account_balance_by_id(self, bank_account_balance_id: int, session: Session) -> Optional[BankAccountBalance]:
        """
        Get a bank account balance by its ID.

        Args:
            bank_account_balance_id: ID of the bank account balance to retrieve
            session: Database session

        Returns:
            BankAccountBalance object if found, None otherwise
        """
        return self.bank_account_balance_repository.get_bank_account_balance_by_id(bank_account_balance_id, session)


    ################################################################################
    # Create Bank Account Balance
    ################################################################################

    def create_bank_account_balance(self, bank_account_id: int, bank_account_balance_data: Dict[str, Any], session: Session) -> BankAccountBalance:
        """
        Create a new bank account balance.

        Args:
            bank_account_id: ID of the bank account to add bank account balance to
            bank_account_balance_data: Dictionary containing bank account balance data
            session: Database session

        Returns:
            BankAccountBalance object
        """
        # Validate Bank Account exists
        bank_account = self.bank_account_repository.get_bank_account_by_id(bank_account_id, session)
        if not bank_account:
            raise ValueError(f"Bank account with ID {bank_account_id} not found")

        # Validate Bank Account Balance data
        errors = self.banking_validation_service.validate_bank_account_balance_creation(bank_account_id, bank_account_balance_data, session)
        if errors:
            raise ValueError(f"Validation errors for bank account balance creation for bank account ID {bank_account_id} on {bank_account_balance_data.get('date', 'unknown')}: {errors}")

        processed_data = {
            **bank_account_balance_data,
            'bank_account_id': bank_account_id,
        }

        bank_account_balance = self.bank_account_balance_repository.create_bank_account_balance(processed_data, session)
        if not bank_account_balance:
            raise ValueError(f"Failed to create bank account balance for bank account ID {bank_account_id} on date {processed_data.get('date', 'unknown')}")

        session.flush()

        # Update the balance adjustment, final balance and the fund event cash flow bank balance ids
        all_changes = []

        bank_account_balance_change = self._update_bank_account_balance(bank_account_id, session)
        if bank_account_balance_change:
            self.domain_update_event_service.add_domain_field_changes_to_list(all_changes, bank_account_balance_change)
            session.flush()
            session.refresh(bank_account_balance)
        
        adjustment_changes = self.bank_account_balance_adjustment_service.calculate_bank_account_balance_adjustment(bank_account_balance, session)
        if adjustment_changes:
            self.domain_update_event_service.add_domain_field_changes_to_list(all_changes, adjustment_changes)
            session.flush()
            session.refresh(bank_account_balance)

        if all_changes:
            valid_changes = [change.to_dict() for change in all_changes if change is not None]
            if valid_changes:
                domain_update_event = self.domain_update_event_service.create_domain_update_event(
                    session=session,
                    domain_object_type=DomainObjectType.BANK_ACCOUNT_BALANCE,
                    domain_object_id=bank_account_balance.id,
                    event_operation=EventOperation.CREATE,
                    event_data={"changes": valid_changes},
                )
            else:
                raise ValueError(f"Failed to calculate balance adjustment for bank account balance with ID {bank_account_balance.id}")

        return bank_account_balance


    ################################################################################
    # Delete Bank Account Balance
    ################################################################################

    def delete_bank_account_balance(self, bank_account_balance_id: int, session: Session) -> bool:
        """
        Delete a bank account balance.
        
        Args:
            bank_account_balance_id: ID of the bank account balance to delete
            session: Database session

        Returns:
            True if the bank account balance was deleted, False otherwise
        """
        bank_account_balance = self.bank_account_balance_repository.get_bank_account_balance_by_id(bank_account_balance_id, session)
        if not bank_account_balance:
            raise ValueError(f"Bank account balance with ID {bank_account_balance_id} not found")

        bank_account_id = bank_account_balance.bank_account_id

        success = self.bank_account_balance_repository.delete_bank_account_balance(bank_account_balance_id, session)
        if not success:
            raise ValueError(f"Failed to delete bank account balance with ID {bank_account_balance_id}")

        all_changes = []

        bank_account_balance_change = self._update_bank_account_balance(bank_account_id, session)
        if bank_account_balance_change:
            self.domain_update_event_service.add_domain_field_changes_to_list(all_changes, bank_account_balance_change)
            session.flush()
            session.refresh(bank_account_balance)

        # Update any fund event cash flows associated with this bank account balance
        from src.fund.services.fund_event_cash_flow_service import FundEventCashFlowService
        fund_event_cash_flow_service = FundEventCashFlowService()
        fund_event_cash_flows = fund_event_cash_flow_service.get_fund_event_cash_flows(session, adjusted_bank_account_balance_ids=[bank_account_balance_id])
        for fund_event_cash_flow in fund_event_cash_flows:
            if fund_event_cash_flow.adjusted_bank_account_balance_id:
                fund_event_cash_flow.adjusted_bank_account_balance_id = None
                self.domain_update_event_service.add_domain_field_changes_to_list(all_changes, DomainFieldChange(domain_object_id=fund_event_cash_flow.id, domain_object_type=DomainObjectType.FUND_EVENT_CASH_FLOW, field_name='adjusted_bank_account_balance_id', old_value=fund_event_cash_flow.adjusted_bank_account_balance_id, new_value=None))

        session.flush()
        if all_changes:
            valid_changes = [change.to_dict() for change in all_changes if change is not None]
            if valid_changes:
                domain_update_event = self.domain_update_event_service.create_domain_update_event(
                    session=session,
                    domain_object_type=DomainObjectType.BANK_ACCOUNT_BALANCE,
                    domain_object_id=bank_account_balance_id,
                    event_operation=EventOperation.DELETE,
                    event_data={"changes": valid_changes},
                )
            else:
                raise ValueError(f"Failed to create domain update event for bank account balance with ID {bank_account_balance_id}")

        return success


    def _update_bank_account_balance(self, bank_account_id: int, session: Session) -> Optional[DomainFieldChange]:
        """
        Update the current balance on the bank account.

        Args:
            session: Database session

        Returns:
            Optional[DomainFieldChange]: The updated bank account balance
        """
        # Get the current balance on the bank account
        bank_account = self.bank_account_repository.get_bank_account_by_id(bank_account_id, session)
        old_current_balance = bank_account.current_balance

        # Get the latest bank account balance's balance
        bank_account_balances = self.bank_account_balance_repository.get_bank_account_balances(session, bank_account_ids=[bank_account_id], sort_by=SortFieldBankAccountBalance.DATE, sort_order=SortOrder.DESC)
        if bank_account_balances:
            new_current_balance = bank_account_balances[0].balance_final
        else:
            new_current_balance = 0.0

        # Update the bank account balance
        if old_current_balance != new_current_balance:
            bank_account.current_balance = new_current_balance
            return(DomainFieldChange(domain_object_id=bank_account_id, domain_object_type=DomainObjectType.BANK_ACCOUNT, field_name='current_balance', old_value=old_current_balance, new_value=new_current_balance))

        return None