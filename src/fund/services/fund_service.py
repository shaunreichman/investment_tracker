"""
Fund Service.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.fund.repositories.fund_repository import FundRepository
from src.fund.enums.fund_enums import FundStatus, FundTrackingType, SortFieldFund, FundTaxStatementFinancialYearType
from src.shared.enums.shared_enums import SortOrder
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.models import Fund

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
            fund_repository: Fund repository to use. If None, creates a new one.
            fund_validation_service: Fund validation service to use. If None, creates a new one.
        """
        self.fund_repository = FundRepository()
        self.fund_validation_service = FundValidationService()


    ################################################################################
    # Get Fund
    ################################################################################

    def get_funds(self, session: Session,
                    company_id: Optional[int] = None,
                    entity_id: Optional[int] = None,
                    fund_status: Optional[FundStatus] = None,
                    fund_tracking_type: Optional[FundTrackingType] = None,
                    sort_by: SortFieldFund = SortFieldFund.START_DATE,
                    sort_order: SortOrder = SortOrder.ASC) -> List[Fund]:
        """
        Get funds with filtering.
        
        Args:
            session: Database session
            company_id: Optional company ID filter
            entity_id: Optional entity ID filter
            fund_status: Optional fund status filter
            fund_tracking_type: Optional fund tracking type filter
            sort_by: Field to sort by
            sort_order: Sort order (ascending or descending)
            
        Returns:
            List of Fund objects
        """
        return self.fund_repository.get_funds(session, company_id, entity_id, fund_status, fund_tracking_type, sort_by, sort_order)

    def get_fund_by_id(self, fund_id: int, session: Session) -> Optional[Fund]:
        """
        Get a fund by its ID including all events.
        
        Args:
            fund_id: ID of the fund to retrieve
            session: Database session
            
        Returns:
            Fund: The fund object with events, or None if not found
        """
        fund = self.fund_repository.get_fund_by_id(fund_id, session)
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
        processed_data['tax_statement_financial_year_type'] = FundTaxStatementFinancialYearType.TAX_JURISDICTION_TO_FINANCIAL_YEAR_TYPE_MAP[processed_data['tax_jurisdiction']]
        
        # Set the fund status to ACTIVE on creation
        processed_data['status'] = FundStatus.ACTIVE

        # Create the fund
        fund = self.fund_repository.create_fund(processed_data, session)
        if not fund:
            raise ValueError(f"Failed to create fund")

        # Update the company
        from src.investment_company.services.company_service import CompanyService
        company_service = CompanyService()
        company = company_service.get_company_by_id(company_id=fund.investment_company_id, session=session)
        if not company:
            raise ValueError(f"Company not found")
        
        # Update the company
        company.total_funds += 1
        company.total_funds_active += 1
        company.total_commitment_amount += fund.commitment_amount
        
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
            raise ValueError(f"Fund not found")
        
        # ENTERPRISE VALIDATION: Validate deletion
        validation_errors = self.fund_validation_service.validate_fund_deletion(fund, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")
        
        # Delete the fund
        success = self.fund_repository.delete_fund(fund_id, session)
        if not success:
            raise ValueError(f"Failed to delete fund")

        # Update the company
        from src.investment_company.services.company_service import CompanyService
        company_service = CompanyService()
        company = company_service.get_company_by_id(company_id=fund.investment_company_id, session=session)
        if not company:
            raise ValueError(f"Company not found")
        company.total_funds -= 1
        company.total_funds_active -= 1
        company.total_commitment_amount -= fund.commitment_amount

        return success