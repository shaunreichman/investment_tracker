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

from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy.orm import Session
from datetime import date
import logging

from src.fund.repositories import FundRepository, FundEventRepository, TaxStatementRepository
from src.fund.events.registry import FundEventHandlerRegistry
from src.fund.enums import FundStatus, FundType, EventType, DistributionType, TaxPaymentType, GroupType, FundEventOperation, SortOrder
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.services.fund_event_service import FundEventService

if TYPE_CHECKING:
    from src.fund.models import Fund, FundEvent


class FundService:
    """
    Service layer for fund operations.
    
    This service coordinates between the API layer, business logic services,
    and data access layer. It provides a clean interface for handling
    fund-related business operations.
    
    Attributes:
        fund_repository (FundRepository): Repository for fund data access
        fund_event_repository (FundEventRepository): Repository for fund event data access
        tax_statement_repository (TaxStatementRepository): Repository for tax statement data access
        registry (FundEventHandlerRegistry): Registry for event handlers
        fund_event_service (FundEventService): Service for fund event operations
        validation_service (FundValidationService): Service for fund validation operations
        logger (Logger): Logger for logging operations
    """
    
    def __init__(self):
        """Initialize the fund service with all required components."""
        self.fund_repository = FundRepository()
        self.fund_event_repository = FundEventRepository()
        self.tax_statement_repository = TaxStatementRepository()
        self.registry = FundEventHandlerRegistry()
        self.fund_event_service = FundEventService()
        self.validation_service = FundValidationService()
        self.logger = logging.getLogger(__name__)

    def create_fund(self, fund_data: Dict[str, Any], session: Session) -> 'Fund':
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
        required_fields = ['name', 'entity_id', 'investment_company_id']
        for field in required_fields:
            if field not in fund_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Convert string enum values to enum objects
        processed_data = fund_data.copy()
        if 'fund_type' in processed_data and isinstance(processed_data['fund_type'], str):
            # For backward compatibility, allow any string value for fund_type
            # The old system used String(100) column, not enum
            pass  # Keep as string
        if 'tracking_type' in processed_data and isinstance(processed_data['tracking_type'], str):
            # tracking_type should be a valid FundType enum
            try:
                processed_data['tracking_type'] = FundType(processed_data['tracking_type'])
            except ValueError:
                raise ValueError(f"Invalid tracking_type: {processed_data['tracking_type']}. Must be one of: {[t.value for t in FundType]}")
        
        # Create the fund
        fund = self.fund_repository.create(processed_data, session)
        
        # Return domain object
        return fund
    
    def update_fund(self, fund_id: int, fund_data: Dict[str, Any], 
                   session: Session) -> Optional['Fund']:
        """
        Update an existing fund.
        
        Args:
            fund_id: ID of the fund to update
            fund_data: Dictionary containing updated fund data
            session: Database session
            
        Returns:
            Fund: The updated fund object, or None if not found
        """
        # Update the fund
        fund = self.fund_repository.update(fund_id, fund_data, session)
        if not fund:
            return None
        
        # Return domain object
        return fund
    
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
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return False
        
        # ENTERPRISE VALIDATION: Validate deletion
        validation_errors = self.validation_service.validate_fund_deletion(fund, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")
        
        # Delete the fund
        return self.fund_repository.delete(fund_id, session)
    
    def get_fund(self, fund_id: int, session: Session) -> Optional['Fund']:
        """
        Get a fund by its ID including all events.
        
        Args:
            fund_id: ID of the fund to retrieve
            session: Database session
            
        Returns:
            Fund: The fund object with events, or None if not found
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None
        
        # Get fund events using the repository
        events = self.fund_event_repository.get_by_fund(fund_id, session)
        
        # Attach events to fund object (or use proper relationship)
        # Note: This assumes the Fund model has a way to attach events
        # If not, the controller can fetch events separately
        fund.events = events
        
        return fund
    
    def get_funds(self, session: Session, 
                  status: Optional[FundStatus] = None,
                  fund_type: Optional[FundType] = None) -> List['Fund']:
        """
        Get funds with filtering.
        
        Args:
            session: Database session
            status: Optional fund status filter
            fund_type: Optional fund type filter            
        Returns:
            List of Fund objects
        """
        if status:
            # Filter by status
            return self.fund_repository.get_funds_by_status(status, session)
        elif fund_type:
            # Filter by fund type
            return self.fund_repository.get_funds_by_type(fund_type, session)
        else:
            # Get all funds
            return self.fund_repository.get_all_funds(session)
    
    def get_fund_events(self, fund_id: int, session: Session,
                       event_types: Optional[List[EventType]] = None) -> List['FundEvent']:
        """
        Get events for a specific fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            event_types: Optional list of event types to filter by
            
        Returns:
            List of FundEvent objects
        """
        events = self.fund_event_repository.get_by_fund(
            fund_id, session, event_types
        )
        
        # Return domain objects
        return events
    
    def get_fund_event(self, fund_id: int, event_id: int, session: Session) -> Optional['FundEvent']:
        """
        Get a specific fund event by ID.
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event
            session: Database session
            
        Returns:
            FundEvent object if found, None otherwise
        """
        # First verify the fund exists
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None
        
        # Get the specific event
        event = self.fund_event_repository.get_by_id(event_id, session)
        if not event or event.fund_id != fund_id:
            return None
        
        return event
