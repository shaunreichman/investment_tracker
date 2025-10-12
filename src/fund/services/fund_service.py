"""
Fund Service.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date

from src.fund.repositories.fund_repository import FundRepository
from src.fund.enums.fund_enums import FundStatus, FundTrackingType, SortFieldFund, FundTaxStatementFinancialYearType, TAX_JURISDICTION_TO_FINANCIAL_YEAR_TYPE_MAP
from src.shared.enums.shared_enums import SortOrder, EventOperation
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.models import Fund
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.shared.services.domain_update_event_service import DomainUpdateEventService
from src.company.services.company_fund_event_secondary_service import CompanyFundEventSecondaryService

class FundService:
    """
    Service layer for fund operations.

    This module provides the FundService class, which handles fund operations and business logic.
    The service provides clean separation of concerns for:
    - Fund retrieval
    - Fund creation
    - Fund deletion with dependency checking

    The service uses the FundRepository to perform CRUD operations and the FundValidationService to validate funds.
    The service is used by the FundController to handle fund operations.
    """
    
    def __init__(self):
        """Initialize the fund service with all required components.

        Args:
            None
        """
        self.fund_repository = FundRepository()
        self.fund_validation_service = FundValidationService()
        self.company_fund_event_secondary_service = CompanyFundEventSecondaryService()
        self.domain_update_event_service = DomainUpdateEventService()


    ################################################################################
    # Get Fund
    ################################################################################

    def get_funds(self, session: Session,
                    company_ids: Optional[List[int]] = None,
                    entity_ids: Optional[List[int]] = None,
                    fund_statuses: Optional[List[FundStatus]] = None,
                    fund_tracking_types: Optional[List[FundTrackingType]] = None,
                    start_start_date: Optional[date] = None,
                    end_start_date: Optional[date] = None,
                    start_end_date: Optional[date] = None,
                    end_end_date: Optional[date] = None,
                    sort_by: Optional[SortFieldFund] = SortFieldFund.START_DATE,
                    sort_order: Optional[SortOrder] = SortOrder.ASC,
                    include_fund_events: Optional[bool] = False,
                    include_fund_event_cash_flows: Optional[bool] = False,
                    include_fund_tax_statements: Optional[bool] = False
    ) -> List[Fund]:
        """
        Get funds with filtering.
        
        Args:
            session: Database session
            company_ids: Optional list of company IDs filter
            entity_ids: Optional list of entity IDs filter
            fund_statuses: Optional list of fund status filter
            fund_tracking_types: Optional list of fund tracking type filter
            start_start_date: Optional start start date filter
            end_start_date: Optional end start date filter
            start_end_date: Optional end end date filter
            end_end_date: Optional end end date filter
            sort_by: Field to sort by
            sort_order: Sort order (ascending or descending)
            include_fund_events: Optional flag to eager load events relationship (optional)
            include_fund_event_cash_flows: Optional flag to eager load cash flows relationship (optional)
            include_fund_tax_statements: Optional flag to eager load tax statements relationship (optional)
            
        Returns:
            List of Fund objects
        """
        return self.fund_repository.get_funds(session, company_ids, entity_ids, fund_statuses, fund_tracking_types, start_start_date, end_start_date, start_end_date, end_end_date, sort_by, sort_order, include_fund_events, include_fund_event_cash_flows, include_fund_tax_statements)

    def get_fund_by_id(self, fund_id: int, session: Session, include_fund_events: Optional[bool] = False, include_fund_event_cash_flows: Optional[bool] = False, include_fund_tax_statements: Optional[bool] = False) -> Optional[Fund]:
        """
        Get a fund by its ID.
        
        Args:
            fund_id: ID of the fund to retrieve
            session: Database session
            include_fund_events: Optional flag to eager load events relationship (optional)
            include_fund_event_cash_flows: Optional flag to eager load cash flows relationship (optional)
            include_fund_tax_statements: Optional flag to eager load tax statements relationship (optional)

        Returns:
            Fund: The fund object, or None if not found
        """
        fund = self.fund_repository.get_fund_by_id(fund_id, session, include_fund_events, include_fund_event_cash_flows, include_fund_tax_statements)
        if not fund:
            return None
 
        return fund
    

    ################################################################################
    # Create Fund
    ################################################################################

    def create_fund(self, fund_data: Dict[str, Any], session: Session) -> Fund:
        """
        Create a new fund.
        
        Args:
            fund_data: Dictionary containing fund data
            session: Database session
            
        Returns:
            Fund: The created fund object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        processed_data = fund_data.copy()

        # Set the tax statement financial year type based on the tax jurisdiction
        processed_data['tax_statement_financial_year_type'] = TAX_JURISDICTION_TO_FINANCIAL_YEAR_TYPE_MAP[processed_data['tax_jurisdiction']]
        
        # Set the fund status to ACTIVE on creation
        processed_data['status'] = FundStatus.ACTIVE

        # Create the fund
        fund = self.fund_repository.create_fund(processed_data, session)
        if not fund:
            raise ValueError(f"Failed to create fund with name '{processed_data.get('name', 'unknown')}'")

        # Update the company
        all_changes = self.company_fund_event_secondary_service.update_company_after_fund_creation(fund.company_id, fund.commitment_amount, session)
        if all_changes:
            valid_changes = [change.to_dict() for change in all_changes if change is not None]
            domain_update_event = self.domain_update_event_service.create_domain_update_event(
                session=session,
                domain_object_type=DomainObjectType.FUND,
                domain_object_id=fund.id,
                event_operation=EventOperation.CREATE,
                event_data={"changes": valid_changes}
            )
            session.flush()
        
        return fund
    

    ################################################################################
    # Delete Fund
    ################################################################################

    def delete_fund(self, fund_id: int, session: Session) -> bool:
        """
        Delete a fund with enterprise-grade validation.
        
        Args:
            fund_id: ID of the fund to delete
            session: Database session
            
        Returns:
            True if fund was deleted, False if not found
            
        Raises:
            ValueError: If deletion validation fails
        """
        # Get existing fund
        fund = self.fund_repository.get_fund_by_id(fund_id, session)
        if not fund:
            raise ValueError(f"Fund with ID {fund_id} not found")
        
        # ENTERPRISE VALIDATION: Validate deletion
        validation_errors = self.fund_validation_service.validate_fund_deletion(fund, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed for fund with ID {fund_id}: {validation_errors}")
        
        # Delete the fund
        success = self.fund_repository.delete_fund(fund_id, session)
        if not success:
            raise ValueError(f"Failed to delete fund with ID {fund_id}")

        # Update the company
        all_changes = self.company_fund_event_secondary_service.update_company_after_fund_deletion(fund.company_id, fund.commitment_amount, fund.status, session)
        if all_changes:
            valid_changes = [change.to_dict() for change in all_changes if change is not None]
            domain_update_event = self.domain_update_event_service.create_domain_update_event(
                session=session,
                domain_object_type=DomainObjectType.FUND,
                domain_object_id=fund_id,
                event_operation=EventOperation.DELETE,
                event_data={"changes": valid_changes}
            )
            session.flush()

        return success