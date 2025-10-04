"""
Fund Event Cash Flow Service.
"""

from src.fund.repositories import FundEventCashFlowRepository
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from src.fund.models import FundEventCashFlow
from src.fund.enums.fund_event_enums import EventType
from src.fund.enums.fund_event_cash_flow_enums import SortFieldFundEventCashFlow
from src.shared.enums.shared_enums import SortOrder

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


    ################################################################################
    # Get Fund Event Cash Flows
    ################################################################################

    def get_fund_event_cash_flows(self, session: Session,
            fund_id: int = None,
            fund_event_id: int = None,
            bank_account_id: int = None,
            sort_by: SortFieldFundEventCashFlow = SortFieldFundEventCashFlow.TRANSFER_DATE,
            sort_order: SortOrder = SortOrder.ASC
    ) -> List[FundEventCashFlow]:
        """
        Get all fund event cash flows for a specific fund.

        Args:
            session: Database session
            fund_id: ID of the fund to filter by
            fund_event_id: ID of the event to filter by
            bank_account_id: ID of the bank account to filter by
            sort_by: Field to sort by
            sort_order: Sort order (ascending or descending)
            
        Returns:
            List of FundEventCashFlow objects
        """
        return self.fund_event_cash_flow_repository.get_fund_event_cash_flows(session, fund_id, fund_event_id, bank_account_id, sort_by, sort_order)


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
        # Validate Bank Account exists
        from src.banking.repositories.bank_account_repository import BankAccountRepository
        bank_account_repository = BankAccountRepository()
        bank_account = bank_account_repository.get_bank_account_by_id(fund_event_cash_flow_data['bank_account_id'], session)
        if not bank_account:
            raise ValueError(f"Bank account not found")

        # Validate Fund Event exists
        from src.fund.repositories.fund_event_repository import FundEventRepository
        fund_event_repository = FundEventRepository()
        fund_event = fund_event_repository.get_fund_event_by_id(fund_event_id, session)
        if not fund_event:
            raise ValueError(f"Fund event not found")

        expected_total_cash_flow_amount = fund_event.amount
        if fund_event.event_type == EventType.DISTRIBUTION and fund_event.has_withholding_tax:
            expected_total_cash_flow_amount -= fund_event.tax_withholding

        # Validate Fund Event Cash Flow Balance
        if fund_event.cash_flow_balance_amount + fund_event_cash_flow_data['amount'] > expected_total_cash_flow_amount:
            raise ValueError(f"Cash flow is too large. It will take the balance amount above the event amount")
        elif fund_event.cash_flow_balance_amount + fund_event_cash_flow_data['amount'] <= expected_total_cash_flow_amount:
            fund_event.cash_flow_balance_amount += fund_event_cash_flow_data['amount']
            if fund_event.cash_flow_balance_amount == expected_total_cash_flow_amount:
                fund_event.is_cash_flow_complete = True
        
        processed_data = {
            **fund_event_cash_flow_data,
            'fund_event_id': fund_event_id
        }

        fund_event_cash_flow = self.fund_event_cash_flow_repository.create_fund_event_cash_flow(processed_data, session)
        if not fund_event_cash_flow:
            raise ValueError(f"Failed to create fund event cash flow")
        
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
            raise ValueError(f"Fund event cash flow not found")
        
        success = self.fund_event_cash_flow_repository.delete_fund_event_cash_flow(fund_event_cash_flow_id, session)
        if not success:
            raise ValueError(f"Failed to delete fund event cash flow")

        # Update the fund event
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        fund_event = fund_event_service.get_fund_event_by_id(fund_event_cash_flow.fund_event_id, session)
        if not fund_event:
            raise ValueError(f"Fund event not found")
        if fund_event.is_cash_flow_complete:
            fund_event.is_cash_flow_complete = False
        fund_event.cash_flow_balance_amount -= fund_event_cash_flow.amount
        
        return True