"""
Fund Validation Service.
"""

from typing import Dict, List, Any
from sqlalchemy.orm import Session
from src.fund.models import Fund, FundEvent
from src.fund.enums.fund_enums import FundTrackingType
from src.fund.enums.fund_event_enums import EventType
from src.fund.repositories import FundEventRepository, FundTaxStatementRepository, FundRepository, FundEventCashFlowRepository
from src.shared.enums.shared_enums import SortOrder


class FundValidationService:
    """
    Fund Validation Service.

    This module provides the FundValidationService class, which handles fund business rule validation.
    The service provides clean separation of concerns for:
    - Fund deletion validation
    - Fund event creation validation
        - Capital call validation
        - Return of capital validation
        - Unit purchase validation
        - Unit sale validation
        - NAV update validation
        - Distribution validation
    - Fund tax statement deletion validation

    The service uses the FundEventRepository and FundTaxStatementRepository to perform CRUD operations.
    """
    
    def __init__(self):
        """
        Initialize the validation service with required repositories.

        Args:
            fund_event_repository: Fund event repository to use. If None, creates a new one.
            fund_tax_statement_repository: Fund tax statement repository to use. If None, creates a new one.
        """
        self.fund_event_repository = FundEventRepository()
        self.fund_tax_statement_repository = FundTaxStatementRepository()
        self.fund_repository = FundRepository()
        self.fund_event_cash_flow_repository = FundEventCashFlowRepository()
    
    def validate_fund_deletion(self, fund: Fund, session: Session) -> Dict[str, List[str]]:
        """
        Validate that the fund can be deleted.
        
        Args:
            fund: Fund to validate for deletion
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # BUSINESS RULE: Only allow deletion if fund has 0 fund events
        fund_events = self.fund_event_repository.get_fund_events(session, fund_ids=[fund.id])
        if len(fund_events) > 0:
            errors['fund_events'] = [
                f'Cannot delete fund with {len(fund_events)} fund events. '
                f'Fund must have 0 events to be deleted.'
            ]
        
        # BUSINESS RULE: Prevent deletion of funds with tax statements
        tax_statements = self.fund_tax_statement_repository.get_fund_tax_statements(fund_ids=[fund.id], session=session)
        if len(tax_statements) > 0:
            errors['tax_statements'] = [
                f'Cannot delete fund with {len(tax_statements)} tax statements. '
                f'Fund must have 0 tax statements to be deleted.'
            ]
        
        return errors

    def validate_fund_event_creation(self, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate fund event creation.
        
        Args:
            event_data: Event data
            session: Database session
        """
        # Get the fund to check its tracking type
        fund = self.fund_repository.get_fund_by_id(event_data['fund_id'], session)
        if not fund:
            raise ValueError(f"Fund with ID {event_data['fund_id']} not found")

        event_type = event_data['event_type']
        if event_type == EventType.CAPITAL_CALL:
            return self.validate_capital_call(fund, event_data, session)
        elif event_type == EventType.RETURN_OF_CAPITAL:
            return self.validate_return_of_capital(fund, event_data, session)
        elif event_type == EventType.UNIT_PURCHASE:
            return self.validate_unit_purchase(fund, event_data, session)
        elif event_type == EventType.UNIT_SALE:
            return self.validate_unit_sale(fund, event_data, session)
        elif event_type == EventType.NAV_UPDATE:
            return self.validate_nav_update(fund, event_data, session)
        elif event_type == EventType.DISTRIBUTION:
            return self.validate_distribution(event_data, session)
        else:
            raise ValueError(f"Invalid event type: {event_type}")
    
    def validate_capital_call(self, fund: Fund, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate capital call creation.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # BUSINESS RULE: Capital calls only for cost-based funds
        if fund.tracking_type != FundTrackingType.COST_BASED:
            errors['fund_type'] = ["Capital calls are only applicable for cost-based funds"]
        
        prev_fund_events = self.fund_event_repository.get_fund_events(session,
                                fund_ids=[fund.id],
                                event_types=[EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL],
                                end_event_date=event_data['event_date'],
                                sort_order=SortOrder.ASC)

        # BUSINESS RULE: Cannot call more than remaining commitment
        if fund.commitment_amount is not None:
            if prev_fund_events:
                prev_capital_call = prev_fund_events[-1]
                if event_data['amount'] > fund.commitment_amount - prev_capital_call.current_equity_balance:
                    errors['amount'] = ["Cannot call more capital than remaining commitment"]
            else:
                if event_data['amount'] > fund.commitment_amount:
                    errors['amount'] = ["Cannot call more capital than total commitment for first capital call"]

        # BUSINESS RULE: We must validate that the future equity balance never goes above the commitment amount as a result of this capital call
        future_fund_events = self.fund_event_repository.get_fund_events(session,
                                fund_ids=[fund.id],
                                event_types=[EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL],
                                start_event_date=event_data['event_date'],
                                sort_order=SortOrder.ASC)
            
        if future_fund_events:
            # Calculate starting equity balance for future validation
            if prev_fund_events:
                updated_equity_balance = prev_fund_events[-1].current_equity_balance + event_data['amount']
            else:
                updated_equity_balance = event_data['amount']
                
            for event in future_fund_events:
                if event.event_type == EventType.CAPITAL_CALL:
                    updated_equity_balance += event.amount
                elif event.event_type == EventType.RETURN_OF_CAPITAL:
                    updated_equity_balance -= event.amount
                if updated_equity_balance > fund.commitment_amount:
                    errors['future_amount'] = ["As a result of this capital call, the future equity balance would go above the commitment amount"]
                    break

        return errors
    
    def validate_return_of_capital(self, fund: Fund, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate return of capital creation.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # BUSINESS RULE: Returns only for cost-based funds
        if fund.tracking_type != FundTrackingType.COST_BASED:
            errors['fund_type'] = ["Returns of capital are only applicable for cost-based funds"]

        prev_fund_events = self.fund_event_repository.get_fund_events(session,
                                fund_ids=[fund.id],
                                event_types=[EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL],
                                end_event_date=event_data['event_date'],
                                sort_order=SortOrder.ASC)

        if prev_fund_events:
            prev_return_of_capital = prev_fund_events[-1]
            if event_data['amount'] > prev_return_of_capital.current_equity_balance:
                errors['amount'] = ["Cannot return more capital than remaining equity as of the event date"]
        else:
            errors['amount'] = ["We first need to do a capital call before we can return of capital"]
        
        # BUSINESS RULE: We must validate that the future equity balance never goes below 0 as a result of this return of capital
        future_fund_events = self.fund_event_repository.get_fund_events(session,
                                fund_ids=[fund.id],
                                event_types=[EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL],
                                start_event_date=event_data['event_date'],
                                sort_order=SortOrder.ASC)
        
        if future_fund_events:
            # Calculate starting equity balance for future validation
            if prev_fund_events:
                updated_equity_balance = prev_fund_events[-1].current_equity_balance - event_data['amount']
            else:
                updated_equity_balance = -event_data['amount']  # No previous events, so negative
                
            for event in future_fund_events:
                if event.event_type == EventType.CAPITAL_CALL:
                    updated_equity_balance += event.amount
                elif event.event_type == EventType.RETURN_OF_CAPITAL:
                    updated_equity_balance -= event.amount
                if updated_equity_balance < 0:
                    errors['future_amount'] = ["As a result of this return of capital, the future equity balance would go below 0"]
                    break
        
        return errors
    
    def validate_unit_purchase(self, fund: Fund, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate unit purchase business rules.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}

        # BUSINESS RULE: Unit purchases only for NAV-based funds
        if fund.tracking_type != FundTrackingType.NAV_BASED:
            errors['fund_type'] = ["Unit purchases are only applicable for NAV-based funds"]
        
        return errors
    
    def validate_unit_sale(self, fund: Fund, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate unit sale business rules.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}

        # BUSINESS RULE: Unit sales only for NAV-based funds
        if fund.tracking_type != FundTrackingType.NAV_BASED:
            errors['fund_type'] = ["Unit sales are only applicable for NAV-based funds"]

        prev_fund_events = self.fund_event_repository.get_fund_events(session,
                                fund_ids=[fund.id],
                                event_types=[EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
                                end_event_date=event_data['event_date'],
                                sort_order=SortOrder.ASC)

        # BUSINESS RULE: We must validate that the units sold is less than the units owned
        if prev_fund_events:
            prev_unit_sale = prev_fund_events[-1]
            if event_data['units_sold'] > prev_unit_sale.units_owned:
                errors['units_sold'] = ["Cannot sell more units than available units owned as of the event date"]
        else:
            errors['units_sold'] = ["We first need to do a unit purchase before we can sell units"]

        future_fund_events = self.fund_event_repository.get_fund_events(session,
                                fund_ids=[fund.id],
                                event_types=[EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
                                start_event_date=event_data['event_date'],
                                sort_order=SortOrder.ASC)

        # BUSINESS RULE: We must validate that the future units owned never goes below 0 as a result of this sale
        if future_fund_events:
            # Calculate starting units owned for future validation
            if prev_fund_events:
                updated_units_owned = prev_fund_events[-1].units_owned - event_data['units_sold']
            else:
                updated_units_owned = -event_data['units_sold']  # No previous events, so negative
                
            for event in future_fund_events:
                if event.event_type == EventType.UNIT_PURCHASE:
                    updated_units_owned += event.units_purchased
                elif event.event_type == EventType.UNIT_SALE:
                    updated_units_owned -= event.units_sold
                if updated_units_owned < 0:
                    errors['future_units_sold'] = ["As a result of this sale, the future units owned would go below 0"]
                    break
        
        return errors
    
    def validate_nav_update(self, fund: Fund, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate NAV update business rules.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}

        # BUSINESS RULE: NAV updates only for NAV-based funds
        if fund.tracking_type != FundTrackingType.NAV_BASED:
            errors['fund_type'] = ["NAV updates are only applicable for NAV-based funds"]

        prev_fund_events = self.fund_event_repository.get_fund_events(session,
                                fund_ids=[fund.id],
                                event_types=[EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
                                end_event_date=event_data['event_date'],
                                sort_order=SortOrder.ASC)

        # BUSINESS RULE: We need to own units before we can update the NAV
        if prev_fund_events:
            prev_unit_event = prev_fund_events[-1]
            if prev_unit_event.units_owned == 0:
                errors['units_owned'] = ["We first need to do own units before we can update the NAV"]
        else:
            errors['units_owned'] = ["We first need to do a unit purchase before we can update the NAV"]

        
        return errors
    
    def validate_distribution(self, event_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate distribution event parameters.
        
        Args:
            event_data: Event data
            session: Database session
            
        Returns:
            Dict[str, List[str]]: Validation errors by field
        """
        errors = {}
    
        # No business logic validation for distributions. The other validation is done in the middleware.
        
        return errors

    def validate_fund_event_deletion(self, event: FundEvent, session: Session) -> Dict[str, List[str]]:
        """
        Validate fund event deletion.
        
        Args:
            event: Event to validate for deletion
            session: Database session
        """
        errors = {}

        # Validate the event doesn't have an associated fund event cash flow
        fund_event_cash_flows = self.fund_event_cash_flow_repository.get_fund_event_cash_flows(session, fund_event_ids=[event.id])
        if fund_event_cash_flows:
            errors['fund_event_cash_flows'] = ["Cannot delete event with associated fund event cash flows"]
        
        return errors


    def validate_fund_event_cash_flow_creation(self, fund_event_id: int, fund_event_cash_flow_data: Dict[str, Any], session: Session) -> Dict[str, List[str]]:
        """
        Validate fund event cash flow creation.
        
        Args:
            fund_event_id: ID of the fund event
            fund_event_cash_flow_data: Event data
            session: Database session
        """
        errors = {}

        # Validate Bank Account exists
        from src.banking.repositories.bank_account_repository import BankAccountRepository
        bank_account_repository = BankAccountRepository()
        bank_account = bank_account_repository.get_bank_account_by_id(fund_event_cash_flow_data['bank_account_id'], session)
        if not bank_account:
            errors['bank_account'] = [f"Bank account with ID {fund_event_cash_flow_data['bank_account_id']} not found"]

        # Validate Fund Event exists
        fund_event = self.fund_event_repository.get_fund_event_by_id(fund_event_id, session)
        if not fund_event:
            errors['fund_event'] = [f"Fund event with ID {fund_event_id} not found"]
        else:
            # Validate Fund Event Cash Flow Balance
            if fund_event.cash_flow_balance_amount + fund_event_cash_flow_data['amount'] > fund_event.amount:
                errors['amount'] = ["Cash flow is too large. It will take the balance amount above the event amount"]

        return errors


    def validate_fund_tax_statement_deletion(self, fund_tax_statement_id: int, session: Session) -> Dict[str, List[str]]:
        """
        Validate fund tax statement deletion.
        
        Args:
            fund_tax_statement_id: ID of the fund tax statement to delete
            session: Database session
        """
        errors = {}
        
        # For no we won't do any validation. In the future we could validate that the fund tax statement has no fund events associated with it.
        return errors