"""
Banking Integration Handler for Fund System.

This handler responds to banking events that affect fund operations,
particularly FundEventCashFlow records that reference bank accounts.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.models.fund_event_cash_flow import FundEventCashFlow
from src.banking.events.domain.base_event import BankingDomainEvent


class BankingIntegrationHandler(BaseFundEventHandler):
    """
    Handles banking events that affect fund operations.
    
    This handler ensures that banking changes properly update
    related fund cash flow records and maintain data consistency.
    """
    
    def __init__(self):
        """Initialize the banking integration handler."""
        super().__init__()
        self.handler_name = "BankingIntegrationHandler"
    
    def handle_bank_account_deleted(self, event: BankingDomainEvent, session: Session) -> Dict[str, Any]:
        """
        Handle bank account deletion events.
        
        When a bank account is deleted, we need to:
        1. Check if there are any active fund cash flows referencing it
        2. Either prevent deletion or mark cash flows as inactive
        3. Update related fund calculations if necessary
        
        Args:
            event: Banking domain event containing account deletion details
            session: Database session for operations
            
        Returns:
            Dict containing processing results and any warnings
        """
        try:
            # Extract account ID from event
            account_id = event.account_id if hasattr(event, 'account_id') else None
            if not account_id:
                raise ValueError("Bank account deletion event missing account_id")
            
            # Check for active cash flows referencing this account
            active_cash_flows = session.query(FundEventCashFlow).filter(
                and_(
                    FundEventCashFlow.bank_account_id == account_id,
                    FundEventCashFlow.is_active == True
                )
            ).all()
            
            if active_cash_flows:
                # Found active cash flows - this is a business rule violation
                raise RuntimeError(
                    f"Cannot delete bank account {account_id}: "
                    f"Found {len(active_cash_flows)} active fund cash flows"
                )
            
            # Check for any cash flows (active or inactive)
            all_cash_flows = session.query(FundEventCashFlow).filter(
                FundEventCashFlow.bank_account_id == account_id
            ).all()
            
            if all_cash_flows:
                # Mark all cash flows as inactive (soft delete approach)
                for cash_flow in all_cash_flows:
                    cash_flow.is_active = False
                    cash_flow.updated_at = self._get_current_timestamp()
                
                session.commit()
                
                return {
                    "success": True,
                    "action": "marked_cash_flows_inactive",
                    "cash_flows_affected": len(all_cash_flows),
                    "message": f"Marked {len(all_cash_flows)} cash flows as inactive for deleted account {account_id}"
                }
            else:
                return {
                    "success": True,
                    "action": "no_cash_flows_found",
                    "cash_flows_affected": 0,
                    "message": f"No cash flows found for deleted account {account_id}"
                }
                
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to handle bank account deletion: {str(e)}")
    
    def handle_bank_account_currency_changed(self, event: BankingDomainEvent, session: Session) -> Dict[str, Any]:
        """
        Handle bank account currency change events.
        
        When a bank account currency changes, we need to:
        1. Check if there are any cash flows with mismatched currencies
        2. Update currency validation for future cash flows
        3. Flag any existing mismatches for review
        
        Args:
            event: Banking domain event containing currency change details
            session: Database session for operations
            
        Returns:
            Dict containing processing results and any warnings
        """
        try:
            # Extract account details from event
            account_id = event.account_id if hasattr(event, 'account_id') else None
            new_currency = event.new_currency if hasattr(event, 'new_currency') else None
            
            if not account_id or not new_currency:
                raise ValueError("Currency change event missing account_id or new_currency")
            
            # Check for cash flows with currency mismatches
            mismatched_cash_flows = session.query(FundEventCashFlow).filter(
                and_(
                    FundEventCashFlow.bank_account_id == account_id,
                    FundEventCashFlow.currency != new_currency
                )
            ).all()
            
            if mismatched_cash_flows:
                # Found currency mismatches - flag for review
                return {
                    "success": True,
                    "action": "currency_mismatch_detected",
                    "cash_flows_affected": len(mismatched_cash_flows),
                    "warnings": [
                        f"Found {len(mismatched_cash_flows)} cash flows with currency mismatch. "
                        f"Account now uses {new_currency}, but cash flows use different currencies. "
                        "Review required for data consistency."
                    ],
                    "message": f"Currency change processed for account {account_id}, mismatches flagged for review"
                }
            else:
                return {
                    "success": True,
                    "action": "currency_change_processed",
                    "cash_flows_affected": 0,
                    "message": f"Currency change processed for account {account_id}, no mismatches found"
                }
                
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to handle currency change: {str(e)}")
    
    def handle_bank_account_status_changed(self, event: BankingDomainEvent, session: Session) -> Dict[str, Any]:
        """
        Handle bank account status change events.
        
        When a bank account status changes (active/inactive), we need to:
        1. Update related cash flow processing rules
        2. Flag any active cash flows for accounts that become inactive
        3. Update fund calculations if necessary
        
        Args:
            event: Banking domain event containing status change details
            session: Database session for operations
            
        Returns:
            Dict containing processing results and any warnings
        """
        try:
            # Extract account details from event
            account_id = event.account_id if hasattr(event, 'account_id') else None
            new_status = event.new_status if hasattr(event, 'new_status') else None
            
            if not account_id or new_status is None:
                raise ValueError("Status change event missing account_id or new_status")
            
            if not new_status:  # Account became inactive
                # Check for active cash flows on inactive account
                active_cash_flows = session.query(FundEventCashFlow).filter(
                    and_(
                        FundEventCashFlow.bank_account_id == account_id,
                        FundEventCashFlow.is_active == True
                    )
                ).all()
                
                if active_cash_flows:
                    return {
                        "success": True,
                        "action": "account_deactivated_with_active_cash_flows",
                        "cash_flows_affected": len(active_cash_flows),
                        "warnings": [
                            f"Account {account_id} deactivated with {len(active_cash_flows)} active cash flows. "
                            "Future cash flows will be blocked, but existing ones remain active."
                        ],
                        "message": f"Account {account_id} status change processed"
                    }
                else:
                    return {
                        "success": True,
                        "action": "account_deactivated_no_cash_flows",
                        "cash_flows_affected": 0,
                        "message": f"Account {account_id} status change processed"
                    }
            else:  # Account became active
                return {
                    "success": True,
                    "action": "account_activated",
                    "cash_flows_affected": 0,
                    "message": f"Account {account_id} activated, ready for cash flow processing"
                }
                
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to handle status change: {str(e)}")
    
    def _get_current_timestamp(self):
        """Get current timestamp for updates."""
        from datetime import datetime
        return datetime.utcnow()
