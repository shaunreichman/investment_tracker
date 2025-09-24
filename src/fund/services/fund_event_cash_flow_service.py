"""
Service layer for fund event cash flow operations.

This service coordinates between the API layer, business logic services,
and data access layer. It provides a clean interface for handling
fund event cash flow-related business operations.
"""

from src.fund.repositories import FundEventCashFlowRepository
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from src.fund.models import FundEventCashFlow
from src.fund.enums import SortFieldFundEventCashFlow, CashFlowDirection
from src.shared.enums.shared_enums import SortOrder

import logging

class FundEventCashFlowService:
    """
    Service layer for fund event cash flow operations.
    """

    def __init__(self):
        """
        Initialize the fund event cash flow service with all required components.
        """
        self.fund_event_cash_flow_repository = FundEventCashFlowRepository()
        self.logger = logging.getLogger(__name__)


    ################################################################################
    # Get Fund Event Cash Flows
    ################################################################################

    def get_fund_event_cash_flows(self, session: Session,
            fund_id: int = None,
            event_id: int = None,
            bank_account_id: int = None,
            sort_by: SortFieldFundEventCashFlow = SortFieldFundEventCashFlow.TRANSFER_DATE,
            sort_order: SortOrder = SortOrder.ASC
    ) -> List[FundEventCashFlow]:
        """
        Get all fund event cash flows for a specific fund.

        Args:
            session: Database session
            fund_id: ID of the fund to filter by
            event_id: ID of the event to filter by
            bank_account_id: ID of the bank account to filter by
            sort_by: Field to sort by
            sort_order: Sort order (ascending or descending)
            
        Returns:
            List of FundEventCashFlow objects
        """
        return self.fund_event_cash_flow_repository.get_fund_event_cash_flows(session, fund_id, event_id, bank_account_id, sort_by, sort_order)


    def get_fund_event_cash_flow_by_id(self, cash_flow_event_id: int, session: Session) -> Optional[FundEventCashFlow]:
        """
        Get a fund event cash flow by its ID.

        Args:
            cash_flow_event_id: ID of the cash flow to retrieve
            session: Database session
            
        Returns:
            FundEventCashFlow object if found, None otherwise
        """
        cash_flow = self.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id(cash_flow_event_id, session)
        if not cash_flow:
            return None
        
        return cash_flow
    

    ################################################################################
    # Create Fund Event Cash Flow
    ################################################################################

    def create_fund_event_cash_flow(self, cash_flow_data: Dict[str, Any], session: Session) -> FundEventCashFlow:
        """
        Create a new fund event cash flow.

        Args:
            cash_flow_data: Dictionary containing cash flow data
            session: Database session
            
        Returns:
            FundEventCashFlow object
        """
        # Validate required fields
        required_fields = ['fund_event_id', 'bank_account_id', 'amount', 'transfer_date', 'direction']
        for field in required_fields:
            if field not in cash_flow_data:
                raise ValueError(f"Required field '{field}' is missing")

        # Validate Bank Account exists
        bank_account = self.bank_account_repository.get_bank_account_by_id(cash_flow_data['bank_account_id'], session)
        if not bank_account:
            raise ValueError(f"Bank account not found")

        # Validate Fund Event exists
        fund_event = self.fund_event_repository.get_fund_event_by_id(cash_flow_data['fund_event_id'], session)
        if not fund_event:
            raise ValueError(f"Fund event not found")
        
        # Convert string enum values to enum objects
        processed_data = cash_flow_data.copy()
        if 'direction' in processed_data and isinstance(processed_data['direction'], str):
            processed_data['direction'] = CashFlowDirection(processed_data['direction'])
        
        cash_flow_event = self.fund_event_cash_flow_repository.create_fund_event_cash_flow(processed_data, session)
        if not cash_flow_event:
            raise ValueError(f"Failed to create fund event cash flow")
        
        return cash_flow_event
    

    ################################################################################
    # Delete Fund Event Cash Flow
    ################################################################################

    def delete_fund_event_cash_flow(self, cash_flow_event_id: int, session: Session) -> bool:
        """
        Delete a fund event cash flow.

        Args:
            cash_flow_event_id: ID of the cash flow to delete
            session: Database session
            
        Returns:
            True if cash flow event was deleted, False if not found
        """
        cash_flow_event = self.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id(cash_flow_event_id, session)
        if not cash_flow_event:
            return False
        
        return self.fund_event_cash_flow_repository.delete_fund_event_cash_flow(cash_flow_event_id, session)