"""
Fund API Service.

This service provides the business logic layer for fund operations,
coordinating between the API controllers and the domain models.

Key responsibilities:
- Fund CRUD operations
- Fund event processing
- Fund calculations and updates
- Business rule enforcement
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from src.fund.repositories import FundRepository, FundEventRepository
from src.fund.enums.fund_enums import FundStatus, FundTrackingType, FundInvestmentType, SortFieldFund, FundTaxStatementFinancialYearType
from src.shared.enums.shared_enums import SortOrder, Country, Currency
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.services.fund_event_service import FundEventService
from src.fund.models import Fund

class FundService:
    """
    Service layer for fund operations.
    
    This service coordinates between the API layer, business logic services,
    and data access layer. It provides a clean interface for handling
    fund-related business operations.
    
    Attributes:
        fund_repository (FundRepository): Repository for fund data access
        fund_event_repository (FundEventRepository): Repository for fund event data access
        fund_event_service (FundEventService): Service for fund event operations
        validation_service (FundValidationService): Service for fund validation operations
        logger (Logger): Logger for logging operations
    """
    
    def __init__(self):
        """Initialize the fund service with all required components."""
        self.fund_repository = FundRepository()
        self.fund_event_repository = FundEventRepository()
        self.fund_event_service = FundEventService()
        self.validation_service = FundValidationService()
        self.logger = logging.getLogger(__name__)


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
        # Validate required fields
        required_fields = ['name', 'entity_id', 'investment_company_id', 'tracking_type', 'tax_jurisdiction', 'currency']
        for field in required_fields:
            if field not in fund_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Convert string enum values to enum objects
        processed_data = fund_data.copy()
        if 'fund_investment_type' in processed_data and isinstance(processed_data['fund_investment_type'], str):
            # fund_type should be a valid FundTrackingType enum
            try:
                processed_data['fund_investment_type'] = FundInvestmentType(processed_data['fund_investment_type'])
            except ValueError:
                raise ValueError(f"Invalid fund_investment_type: {processed_data['fund_investment_type']}. Must be one of: {[t.value for t in FundInvestmentType]}")
        if 'tracking_type' in processed_data and isinstance(processed_data['tracking_type'], str):
            # tracking_type should be a valid FundTrackingType enum
            try:
                processed_data['tracking_type'] = FundTrackingType(processed_data['tracking_type'])
            except ValueError:
                raise ValueError(f"Invalid tracking_type: {processed_data['tracking_type']}. Must be one of: {[t.value for t in FundTrackingType]}")
        if 'tax_jurisdiction' in processed_data and isinstance(processed_data['tax_jurisdiction'], str):
            # tax_jurisdiction should be a valid Country enum
            try:
                processed_data['tax_jurisdiction'] = Country(processed_data['tax_jurisdiction'])
            except ValueError:
                raise ValueError(f"Invalid tax_jurisdiction: {processed_data['tax_jurisdiction']}. Must be one of: {[t.value for t in Country]}")
        if 'currency' in processed_data and isinstance(processed_data['currency'], str):
            # currency should be a valid Currency enum
            try:
                processed_data['currency'] = Currency(processed_data['currency'])
            except ValueError:
                raise ValueError(f"Invalid currency: {processed_data['currency']}. Must be one of: {[t.value for t in Currency]}")

        # Set the tax statement financial year type based on the tax jurisdiction
        processed_data['tax_statement_financial_year_type'] = FundTaxStatementFinancialYearType.TAX_JURISDICTION_TO_FINANCIAL_YEAR_TYPE_MAP[processed_data['tax_jurisdiction']]
        
        # Set the fund status to ACTIVE on creation
        processed_data['status'] = FundStatus.ACTIVE

        # Create the fund
        fund = self.fund_repository.create_fund(processed_data, session)
        if not fund:
            raise ValueError(f"Failed to create fund")
        
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
            return False
        
        # ENTERPRISE VALIDATION: Validate deletion
        validation_errors = self.validation_service.validate_fund_deletion(fund, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")
        
        # Delete the fund
        return self.fund_repository.delete_fund(fund_id, session)