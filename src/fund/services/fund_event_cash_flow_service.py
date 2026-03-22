"""
Fund Event Cash Flow Service.
"""

from src.fund.repositories import FundEventCashFlowRepository
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from src.fund.models import FundEventCashFlow
from src.fund.enums.fund_event_enums import EventType
from src.fund.enums.fund_event_cash_flow_enums import SortFieldFundEventCashFlow
from src.shared.enums.shared_enums import SortOrder, Currency
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.shared.enums.shared_enums import EventOperation
from src.fund.repositories.fund_event_repository import FundEventRepository
from src.fund.services.fund_validation_service import FundValidationService
from src.shared.models import DomainFieldChange
from src.shared.exceptions import ValidationException


class FundEventCashFlowService:
    """
    Fund Event Cash Flow Service.

    This module provides the FundEventCashFlowService class, which handles fund event cash flow operations and business logic.
    The service provides clean separation of concerns for:
    - Fund event cash flow retrieval
    - Fund event cash flow creation
    - Fund event cash flow deletion

    The service uses the FundEventCashFlowRepository to perform CRUD operations.
    The service is used by the FundEventCashFlowController to handle fund event cash flow operations.
    """

    def __init__(self):
        """
        Initialize the fund event cash flow service with all required components.

        Args:
            fund_event_cash_flow_repository: Fund event cash flow repository to use. If None, creates a new one.
        """
        self.fund_event_cash_flow_repository = FundEventCashFlowRepository()
        self.fund_event_repository = FundEventRepository()
        self.fund_validation_service = FundValidationService()


    ################################################################################
    # Get Fund Event Cash Flows
    ################################################################################

    def get_fund_event_cash_flows(self, session: Session,
            fund_ids: Optional[List[int]] = None,
            fund_event_ids: Optional[List[int]] = None,
            bank_account_ids: Optional[List[int]] = None,
            different_month: Optional[bool] = None,
            adjusted_bank_account_balance_ids: Optional[List[int]] = None,
            currencies: Optional[List[Currency]] = None,
            start_transfer_date: Optional[date] = None,
            end_transfer_date: Optional[date] = None,
            start_fund_event_date: Optional[date] = None,
            end_fund_event_date: Optional[date] = None,
            sort_by: Optional[SortFieldFundEventCashFlow] = SortFieldFundEventCashFlow.TRANSFER_DATE,
            sort_order: Optional[SortOrder] = SortOrder.ASC
    ) -> List[FundEventCashFlow]:
        """
        Get all fund event cash flows for a specific fund.

        Args:
            session: Database session
            fund_ids: List of fund IDs to filter by
            fund_event_ids: List of event IDs to filter by
            bank_account_ids: List of bank account IDs to filter by
            different_month: Whether the transfer date is in a different month to the fund event date
            adjusted_bank_account_balance_ids: List of bank account balance IDs to filter by
            currencies: List of currencies to filter by
            start_transfer_date: Start date of the transfer date to filter by
            end_transfer_date: End date of the transfer date to filter by
            start_fund_event_date: Start date of the fund event date to filter by
            end_fund_event_date: End date of the fund event date to filter by
            sort_by: Field to sort by
            sort_order: Sort order (ascending or descending)
            
        Returns:
            List of FundEventCashFlow objects
        """
        return self.fund_event_cash_flow_repository.get_fund_event_cash_flows(session, fund_ids, fund_event_ids, bank_account_ids, different_month, adjusted_bank_account_balance_ids, currencies, start_transfer_date, end_transfer_date, start_fund_event_date, end_fund_event_date, sort_by, sort_order)


    def get_fund_event_cash_flow_by_id(self, fund_event_cash_flow_id: int, session: Session) -> Optional[FundEventCashFlow]:
        """
        Get a fund event cash flow by its ID.

        Args:
            fund_event_cash_flow_id: ID of the cash flow to retrieve
            session: Database session
            
        Returns:
            FundEventCashFlow object if found, None otherwise
        """
        cash_flow = self.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id(fund_event_cash_flow_id, session)
        if not cash_flow:
            return None
        
        return cash_flow
    

    ################################################################################
    # Create Fund Event Cash Flow
    ################################################################################

    def create_fund_event_cash_flow(self, fund_event_id: int, fund_event_cash_flow_data: Dict[str, Any], session: Session) -> FundEventCashFlow:
        """
        Create a new fund event cash flow.

        Args:
            fund_event_id: ID of the fund event
            fund_event_cash_flow_data: Dictionary containing cash flow data
            session: Database session
            
        Returns:
            FundEventCashFlow object
        """
        # Validate Fund Event Cash Flow
        validation_errors = self.fund_validation_service.validate_fund_event_cash_flow_creation(fund_event_id, fund_event_cash_flow_data, session)
        if validation_errors:
            raise ValidationException(
                message="Validation errors for fund event cash flow creation",
                details=validation_errors
            )

        # Validate Fund Event exists
        fund_event = self.fund_event_repository.get_fund_event_by_id(fund_event_id, session)
        
        processed_data = {
            **fund_event_cash_flow_data,
            'fund_event_id': fund_event_id,
            'fund_event_date': fund_event.event_date,
            'different_month': fund_event_cash_flow_data['transfer_date'].month != fund_event.event_date.month
        }

        fund_event_cash_flow = self.fund_event_cash_flow_repository.create_fund_event_cash_flow(processed_data, session)
        if not fund_event_cash_flow:
            raise ValueError(f"Failed to create fund event cash flow for fund event ID {fund_event_id} with bank account ID {processed_data.get('bank_account_id', 'unknown')}")

        session.flush()

        self._handle_fund_event_cash_flow_secondary_impact(session=session, fund_event_id=fund_event_id, event_operation=EventOperation.CREATE, fund_event_cash_flow_id=fund_event_cash_flow.id)
        
        return fund_event_cash_flow
    

    ################################################################################
    # Delete Fund Event Cash Flow
    ################################################################################

    def delete_fund_event_cash_flow(self, fund_event_cash_flow_id: int, session: Session) -> bool:
        """
        Delete a fund event cash flow.

        Args:
            fund_event_cash_flow_id: ID of the cash flow to delete
            session: Database session
            
        Returns:
            True if cash flow event was deleted, False if not found
        """
        fund_event_cash_flow = self.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id(fund_event_cash_flow_id, session)
        if not fund_event_cash_flow:
            raise ValueError(f"Fund event cash flow with ID {fund_event_cash_flow_id} not found")

        bank_account_id = fund_event_cash_flow.bank_account_id
        cash_flow_date = fund_event_cash_flow.transfer_date
        
        success = self.fund_event_cash_flow_repository.delete_fund_event_cash_flow(fund_event_cash_flow_id, session)
        if not success:
            raise ValueError(f"Failed to delete fund event cash flow with ID {fund_event_cash_flow_id}")

        self._handle_fund_event_cash_flow_secondary_impact(session=session, fund_event_id=fund_event_cash_flow.fund_event_id, event_operation=EventOperation.DELETE, fund_event_cash_flow_id=fund_event_cash_flow_id, bank_account_id=bank_account_id, cash_flow_date=cash_flow_date)

        return True


    def _handle_fund_event_cash_flow_secondary_impact(self, session: Session,
                fund_event_id: int,
                event_operation: EventOperation,
                fund_event_cash_flow_id: int,
                bank_account_id: int = None,
                cash_flow_date: date = None):
        """
        Update the secondary impact of a fund event cash flow.

        Args:
            session: Database session
            fund_event_id: ID of the fund event
            event_operation: Operation to perform
            fund_event_cash_flow_id: ID of the cash flow to update
            bank_account_id: ID of the bank account (only provided when deleting a cash flow)
            cash_flow_date: Date of the transfer (only provided when deleting a cash flow)
        """
        # 1. VALIDATE THE INPUTS
        # When creating a fund event cash flow, we must not pass either bank_account_id or cash_flow_date
        if event_operation == EventOperation.CREATE and (bank_account_id or cash_flow_date):
            raise ValueError(f"When creating a fund event cash flow, we must not pass either the bank_account_id or cash_flow_date")
        # When deleting a fund event cash flow, we must provide both the bank_account_id and cash_flow_date
        elif event_operation == EventOperation.DELETE and not (bank_account_id and cash_flow_date):
            raise ValueError(f"When deleting a fund event cash flow, we must provide both the bank_account_id and cash_flow_date")

        all_changes: list[DomainFieldChange] = []

        # 2. GET THE FUND EVENT
        fund_event = self.fund_event_repository.get_fund_event_by_id(fund_event_id, session)
        if not fund_event:
            raise ValueError(f"Fund event with ID {fund_event_id} not found")

        # 2.1 Calculate the expected total cash flow amount after accounting for the withholding tax
        expected_total_cash_flow_amount = fund_event.amount
        if fund_event.event_type == EventType.DISTRIBUTION and fund_event.has_withholding_tax:
            expected_total_cash_flow_amount -= fund_event.tax_withholding

        # 2.2 Update the expected total cash flow amount
        old_is_cash_flow_complete = fund_event.is_cash_flow_complete
        old_cash_flow_balance_amount = fund_event.cash_flow_balance_amount
        fund_event_cash_flows = self.fund_event_cash_flow_repository.get_fund_event_cash_flows(session, fund_event_ids=[fund_event.id])
        new_cash_flow_balance_amount = 0
        for fund_event_cash_flow in fund_event_cash_flows:
            new_cash_flow_balance_amount += fund_event_cash_flow.amount

        if new_cash_flow_balance_amount == expected_total_cash_flow_amount:
            new_is_cash_flow_complete = True
        else:
            new_is_cash_flow_complete = False

        if old_is_cash_flow_complete != new_is_cash_flow_complete:
            fund_event.is_cash_flow_complete = new_is_cash_flow_complete
            all_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.FUND_EVENT, domain_object_id=fund_event.id, field_name='is_cash_flow_complete', old_value=old_is_cash_flow_complete, new_value=new_is_cash_flow_complete))
        if old_cash_flow_balance_amount != new_cash_flow_balance_amount:
            fund_event.cash_flow_balance_amount = new_cash_flow_balance_amount
            all_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.FUND_EVENT, domain_object_id=fund_event.id, field_name='cash_flow_balance_amount', old_value=old_cash_flow_balance_amount, new_value=new_cash_flow_balance_amount))

        session.flush()
        session.refresh(fund_event)

        # 3. UPDATE BANK ACCOUNT BALANCE
        # 3.1 Get the bank_account
        if event_operation == EventOperation.CREATE:
            fund_event_cash_flow = self.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id(fund_event_cash_flow_id, session)
            if not fund_event_cash_flow:
                raise ValueError(f"Fund event cash flow with ID {fund_event_cash_flow_id} not found")
            bank_account_id = fund_event_cash_flow.bank_account_id
            cash_flow_date = fund_event_cash_flow.transfer_date

        # 3.2 Get the last day of the month
        from src.shared.calculators.last_day_of_the_month_calculator import LastDayOfTheMonthCalculator
        last_day_of_the_month_calculator = LastDayOfTheMonthCalculator()
        last_day_of_the_month = last_day_of_the_month_calculator.get_last_day_of_the_month(cash_flow_date)

        # 3.3 Get the bank account balance
        from src.banking.repositories.bank_account_balance_repository import BankAccountBalanceRepository
        bank_account_balance_repository = BankAccountBalanceRepository()
        bank_account_balances = bank_account_balance_repository.get_bank_account_balances(
            session,
            bank_account_ids=[bank_account_id],
            start_date=last_day_of_the_month,
            end_date=last_day_of_the_month
        )
        if not bank_account_balances:
            # The bank account balance has not been created yet
            bank_account_balance = None
        elif len(bank_account_balances) >= 2:
            raise ValidationException(
                message="Multiple bank account balances found for the same bank account and date",
                details={"bank_account_id": bank_account_id, "date": last_day_of_the_month}
            )
        else:
            bank_account_balance = bank_account_balances[0]
            # 3.4 Calculate the balance adjustment
            from src.banking.services.bank_account_balance_adjustment_service import BankAccountBalanceAdjustmentService
            bank_account_balance_adjustment_service = BankAccountBalanceAdjustmentService()
            adjustment_changes = bank_account_balance_adjustment_service.calculate_bank_account_balance_adjustment(bank_account_balance, session)
            if adjustment_changes:
                # 3.5 Add the changes to the all_changes list
                from src.shared.services.domain_update_event_service import DomainUpdateEventService
                domain_update_event_service = DomainUpdateEventService()
                domain_update_event_service.add_domain_field_changes_to_list(all_changes, adjustment_changes)
                # 3.6 Flush the changes to the database
                session.flush()
                session.refresh(bank_account_balance)

        # 4. STORE THE DOMAIN FUND EVENT CASH FLOW CONTAINING THE CHANGES
        if all_changes:
            valid_changes = [change.to_dict() for change in all_changes if change is not None]
            if valid_changes:
                from src.shared.services.domain_update_event_service import DomainUpdateEventService
                domain_update_event_service = DomainUpdateEventService()
                domain_update_event = domain_update_event_service.create_domain_update_event(
                    session=session,
                    domain_object_type=DomainObjectType.FUND_EVENT_CASH_FLOW,
                    domain_object_id=fund_event_cash_flow_id,
                    event_operation=event_operation,
                    event_data={"changes": valid_changes},
                )
            else:
                raise ValueError(f"Failed to calculate balance adjustment for fund event cash flow with ID {fund_event_cash_flow_id}")
        
        session.flush()