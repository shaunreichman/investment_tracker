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
from datetime import date

from src.fund.repositories import FundRepository, FundEventRepository, TaxStatementRepository
from src.fund.events.orchestrator import FundUpdateOrchestrator
from src.fund.events.registry import FundEventHandlerRegistry
from src.fund.enums import FundStatus, FundType, EventType


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
        orchestrator (FundUpdateOrchestrator): Orchestrator for fund update operations
        registry (FundEventHandlerRegistry): Registry for event handlers
    """
    
    def __init__(self):
        """Initialize the fund service with all required components."""
        self.fund_repository = FundRepository()
        self.fund_event_repository = FundEventRepository()
        self.tax_statement_repository = TaxStatementRepository()
        self.orchestrator = FundUpdateOrchestrator()
        self.registry = FundEventHandlerRegistry()
    
    def create_fund(self, fund_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
        """
        Create a new fund.
        
        Args:
            fund_data: Dictionary containing fund data
            session: Database session
            
        Returns:
            Dictionary containing the created fund information
            
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
        
        # Return fund information
        return {
            'id': fund.id,
            'name': fund.name,
            'status': fund.status.value if fund.status else None,
            'fund_type': fund.fund_type.value if hasattr(fund.fund_type, 'value') else fund.fund_type,
            'tracking_type': fund.tracking_type.value if hasattr(fund.tracking_type, 'value') else fund.tracking_type,
            'entity_id': fund.entity_id,
            'investment_company_id': fund.investment_company_id,
            'created_at': fund.created_at.isoformat() if fund.created_at else None
        }
    
    def update_fund(self, fund_id: int, fund_data: Dict[str, Any], 
                   session: Session) -> Optional[Dict[str, Any]]:
        """
        Update an existing fund.
        
        Args:
            fund_id: ID of the fund to update
            fund_data: Dictionary containing updated fund data
            session: Database session
            
        Returns:
            Dictionary containing the updated fund information, or None if not found
        """
        # Update the fund
        fund = self.fund_repository.update(fund_id, fund_data, session)
        if not fund:
            return None
        
        # Return updated fund information
        return {
            'id': fund.id,
            'name': fund.name,
            'status': fund.status.value if fund.status else None,
            'fund_type': fund.fund_type.value if hasattr(fund.fund_type, 'value') else fund.fund_type,
            'tracking_type': fund.tracking_type.value if hasattr(fund.tracking_type, 'value') else fund.tracking_type,
            'entity_id': fund.entity_id,
            'investment_company_id': fund.investment_company_id,
            'updated_at': fund.updated_at.isoformat() if fund.updated_at else None
        }
    
    def delete_fund(self, fund_id: int, session: Session) -> bool:
        """
        Delete a fund.
        
        Args:
            fund_id: ID of the fund to delete
            session: Database session
            
        Returns:
            True if fund was deleted, False if not found
        """
        return self.fund_repository.delete(fund_id, session)
    
    def get_fund(self, fund_id: int, session: Session) -> Optional[Dict[str, Any]]:
        """
        Get a fund by its ID including all events.
        
        Args:
            fund_id: ID of the fund to retrieve
            session: Database session
            
        Returns:
            Dictionary containing fund information and events, or None if not found
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None
        
        # Get fund events using the repository
        events = self.fund_event_repository.get_by_fund(fund_id, session)
        
        # Convert events to dictionaries
        event_list = []
        for event in events:
            event_dict = {
                'id': event.id,
                'event_type': event.event_type.value if event.event_type else None,
                'event_date': event.event_date.isoformat() if event.event_date else None,
                'amount': event.amount,
                'description': event.description,
                'reference_number': event.reference_number,
                'is_grouped': event.is_grouped,
                'group_id': event.group_id,
                'group_type': event.group_type.value if event.group_type else None,
                'group_position': event.group_position,
                'distribution_type': event.distribution_type.value if event.distribution_type else None,
                'has_withholding_tax': event.has_withholding_tax,
                'created_at': event.created_at.isoformat() if event.created_at else None
            }
            event_list.append(event_dict)
        
        return {
            'id': fund.id,
            'name': fund.name,
            'status': fund.status.value if fund.status else None,
            'fund_type': fund.fund_type.value if fund.fund_type else None,
            'entity_id': fund.entity_id,
            'investment_company_id': fund.investment_company_id,
            'description': fund.description,
            'created_at': fund.created_at.isoformat() if fund.created_at else None,
            'updated_at': fund.updated_at.isoformat() if fund.updated_at else None,
            'events': event_list
        }
    
    def get_funds(self, session: Session, 
                  skip: int = 0, 
                  limit: int = 100,
                  status: Optional[FundStatus] = None,
                  fund_type: Optional[FundType] = None,
                  search: Optional[str] = None) -> Dict[str, Any]:
        """
        Get funds with filtering, pagination, and search.
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional fund status filter
            fund_type: Optional fund type filter
            search: Optional search term
            
        Returns:
            Dictionary containing funds and pagination information
        """
        funds = []
        
        if search:
            # Use search functionality
            funds = self.fund_repository.search_funds(search, session)
        elif status:
            # Filter by status
            funds = self.fund_repository.get_funds_by_status(status, session)
        elif fund_type:
            # Filter by fund type
            funds = self.fund_repository.get_funds_by_type(fund_type, session)
        else:
            # Get all funds with pagination
            funds = self.fund_repository.get_all(session, skip, limit)
        
        # Convert to dictionaries
        fund_list = []
        for fund in funds:
            fund_list.append({
                'id': fund.id,
                'name': fund.name,
                'status': fund.status.value if fund.status else None,
                'fund_type': fund.fund_type.value if fund.fund_type else None,
                'entity_id': fund.entity_id,
                'investment_company_id': fund.investment_company_id,
                'created_at': fund.created_at.isoformat() if fund.created_at else None
            })
        
        return {
            'funds': fund_list,
            'total': len(fund_list),
            'skip': skip,
            'limit': limit
        }
    
    def add_fund_event(self, fund_id: int, event_data: Dict[str, Any], 
                      session: Session) -> Dict[str, Any]:
        """
        Add a fund event using the event handler system.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            Dictionary containing the created event information
            
        Raises:
            ValueError: If required fields are missing
            RuntimeError: If event processing fails
        """
        # Get the fund first
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            raise RuntimeError(f"Fund with ID {fund_id} not found")
        
        # Validate required fields
        required_fields = ['event_type', 'event_date']
        
        # Special handling for withholding tax distributions
        if (event_data.get('event_type') == 'DISTRIBUTION' and 
            event_data.get('distribution_type') == 'INTEREST' and
            any([
                event_data.get('interest_gross_amount') is not None,
                event_data.get('interest_net_amount') is not None,
                event_data.get('interest_withholding_tax_amount') is not None,
                event_data.get('interest_withholding_tax_rate') is not None
            ])):
            # For withholding tax distributions, amount is not required
            pass
        elif event_data.get('event_type') in ['UNIT_PURCHASE', 'UNIT_SALE', 'NAV_UPDATE']:
            # For NAV-based events, amount is not required
            pass
        else:
            # For all other events, amount is required
            required_fields.append('amount')
        
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Add fund_id to event data
        event_data['fund_id'] = fund_id
        
        # Ensure event_date is present
        if 'event_date' not in event_data:
            raise ValueError("Required field 'event_date' is missing")
        
        # Process the event through the orchestrator
        try:
            result = self.orchestrator.process_fund_event(event_data, session, fund)
            
            # Return event information
            response_data = {
                'id': result.id,
                'fund_id': fund_id,
                'event_type': event_data['event_type'],
                'event_date': event_data['event_date'].isoformat() if hasattr(event_data['event_date'], 'isoformat') else str(event_data['event_date']),
                'description': event_data.get('description'),
                'status': 'processed'
            }
            
            # Handle amount field based on event type
            if (event_data.get('event_type') == 'DISTRIBUTION' and 
                event_data.get('distribution_type') == 'INTEREST' and
                any([
                    event_data.get('interest_gross_amount') is not None,
                    event_data.get('interest_net_amount') is not None,
                    event_data.get('interest_withholding_tax_amount') is not None,
                    event_data.get('interest_withholding_tax_rate') is not None
                ])):
                # For withholding tax distributions, don't include amount
                pass
            elif event_data.get('event_type') in ['UNIT_PURCHASE', 'UNIT_SALE', 'NAV_UPDATE']:
                # For NAV-based events, don't include amount
                pass
            else:
                # For other events, include amount
                response_data['amount'] = float(event_data['amount'])
            
            return response_data
            
        except Exception as e:
            raise RuntimeError(f"Failed to process fund event: {str(e)}")
    
    def update_fund_event(self, fund_id: int, event_id: int, 
                         event_data: Dict[str, Any], session: Session) -> Optional[Dict[str, Any]]:
        """
        Update a fund event.
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event to update
            event_data: Dictionary containing updated event data
            session: Database session
            
        Returns:
            Dictionary containing the updated event information, or None if not found
        """
        # Update the event
        event = self.fund_event_repository.update(event_id, event_data, session)
        if not event:
            return None
        
        # Return updated event information
        return {
            'id': event.id,
            'fund_id': event.fund_id,
            'event_type': event.event_type,
            'event_date': event.event_date.isoformat() if event.event_date else None,
            'amount': str(event.amount) if event.amount else None,
            'updated_at': event.updated_at.isoformat() if event.updated_at else None
        }
    
    def delete_fund_event(self, fund_id: int, event_id: int, session: Session) -> bool:
        """
        Delete a fund event.
        
        Args:
            fund_id: ID of the fund
            event_id: ID of the event to delete
            session: Database session
            
        Returns:
            True if event was deleted, False if not found
        """
        return self.fund_event_repository.delete(event_id, session)
    
    def get_fund_events(self, fund_id: int, session: Session,
                       skip: int = 0, 
                       limit: int = 100,
                       event_types: Optional[List[EventType]] = None) -> Dict[str, Any]:
        """
        Get events for a specific fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            event_types: Optional list of event types to filter by
            
        Returns:
            Dictionary containing events and pagination information
        """
        events = self.fund_event_repository.get_by_fund(
            fund_id, session, event_types, skip, limit
        )
        
        # Convert to dictionaries
        event_list = []
        for event in events:
            event_list.append({
                'id': event.id,
                'fund_id': event.fund_id,
                'event_type': event.event_type,
                'event_date': event.event_date.isoformat() if event.event_date else None,
                'amount': str(event.amount) if event.amount else None,
                'created_at': event.created_at.isoformat() if event.created_at else None
            })
        
        return {
            'events': event_list,
            'total': len(event_list),
            'skip': skip,
            'limit': limit
        }
    
    def get_fund_event(self, fund_id: int, event_id: int, session: Session) -> Optional[Any]:
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
    
    def get_fund_summary(self, fund_id: int, session: Session) -> Optional[Dict[str, Any]]:
        """
        Get a comprehensive summary of a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Dictionary containing fund summary information, or None if not found
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None
        
        # Get event count
        event_count = self.fund_event_repository.get_event_count_by_fund(fund_id, session)
        
        # Get tax statement count
        tax_statement_count = self.tax_statement_repository.get_statement_count_by_fund(fund_id, session)
        
        return {
            'id': fund.id,
            'name': fund.name,
            'status': fund.status.value if fund.status else None,
            'fund_type': fund.fund_type.value if fund.fund_type else None,
            'entity_id': fund.entity_id,
            'investment_company_id': fund.investment_company_id,
            'event_count': event_count,
            'tax_statement_count': tax_statement_count,
            'created_at': fund.created_at.isoformat() if fund.created_at else None,
            'updated_at': fund.updated_at.isoformat() if fund.updated_at else None
        }
    
    def get_fund_metrics(self, fund_id: int, session: Session) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Dictionary containing fund metrics, or None if not found
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None
        
        # Get recent events for metrics calculation
        recent_events = self.fund_event_repository.get_by_fund(
            fund_id, session, limit=50
        )
        
        # Calculate basic metrics (this would be enhanced with actual business logic)
        total_events = len(recent_events)
        capital_events = [e for e in recent_events if e.event_type in [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]]
        distribution_events = [e for e in recent_events if e.event_type == EventType.DISTRIBUTION]
        
        return {
            'fund_id': fund_id,
            'total_events': total_events,
            'capital_events': len(capital_events),
            'distribution_events': len(distribution_events),
            'last_event_date': recent_events[-1].event_date.isoformat() if recent_events else None,
            'status': fund.status.value if fund.status else None
        }

    # ============================================================================
    # FUND EVENT METHODS - Added for Phase 1 circular import fix
    # ============================================================================
    
    def add_capital_call(self, fund_id: int, amount: float, call_date: date, 
                         description: str = None, reference_number: str = None, 
                         session: Session = None) -> Any:
        """
        Add capital call event through proper orchestration.
        
        Args:
            fund_id: ID of the fund
            amount: Capital call amount
            call_date: Date of the capital call
            description: Description of the capital call
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created capital call event
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            raise ValueError(f"Fund with ID {fund_id} not found")
        
        # Use orchestrator for event processing
        event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': amount,
            'event_date': call_date,
            'description': description or f"Capital call: ${amount:,.2f}",
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, fund)
    
    def add_return_of_capital(self, fund_id: int, amount: float, return_date: date,
                              description: str = None, reference_number: str = None,
                              session: Session = None) -> Any:
        """
        Add return of capital event through proper orchestration.
        
        Args:
            fund_id: ID of the fund
            amount: Return amount
            return_date: Date of the return
            description: Description of the return
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created return of capital event
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            raise ValueError(f"Fund with ID {fund_id} not found")
        
        # Use orchestrator for event processing
        event_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'amount': amount,
            'event_date': return_date,
            'description': description or f"Return of capital: ${amount:,.2f}",
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, fund)
    
    def add_distribution(self, fund_id: int, event_date: date, distribution_type: Any,
                         distribution_amount: float = None, has_withholding_tax: bool = False,
                         gross_interest_amount: float = None, net_interest_amount: float = None,
                         withholding_tax_amount: float = None, withholding_tax_rate: float = None,
                         description: str = None, reference_number: str = None,
                         session: Session = None) -> Any:
        """
        Add distribution event through proper orchestration.
        
        Args:
            fund_id: ID of the fund
            event_date: Distribution date
            distribution_type: Type of distribution
            distribution_amount: Simple distribution amount
            has_withholding_tax: Whether this distribution has withholding tax
            gross_interest_amount: Gross interest amount
            net_interest_amount: Net interest amount
            withholding_tax_amount: Tax amount withheld
            withholding_tax_rate: Tax rate percentage
            description: Event description
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent or tuple: Distribution event, or (distribution_event, tax_event) for withholding tax
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            raise ValueError(f"Fund with ID {fund_id} not found")
        
        # Use orchestrator for event processing
        event_data = {
            'event_type': EventType.DISTRIBUTION,
            'event_date': event_date,
            'distribution_type': distribution_type,
            'distribution_amount': distribution_amount,
            'has_withholding_tax': has_withholding_tax,
            'gross_interest_amount': gross_interest_amount,
            'net_interest_amount': net_interest_amount,
            'withholding_tax_amount': withholding_tax_amount,
            'withholding_tax_rate': withholding_tax_rate,
            'description': description,
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, fund)
    
    def add_nav_update(self, fund_id: int, nav_per_share: float, update_date: date,
                       description: str = None, reference_number: str = None,
                       session: Session = None) -> Any:
        """
        Add NAV update event through proper orchestration.
        
        Args:
            fund_id: ID of the fund
            nav_per_share: NAV per share value
            update_date: Date of the NAV update
            description: Description of the update
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created NAV update event
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            raise ValueError(f"Fund with ID {fund_id} not found")
        
        # Use orchestrator for event processing
        event_data = {
            'event_type': EventType.NAV_UPDATE,
            'nav_per_share': nav_per_share,
            'event_date': update_date,
            'description': description or f"NAV update: ${nav_per_share:.4f}",
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, fund)
    
    def add_unit_purchase(self, fund_id: int, units: float, price: float, date: date,
                          description: str = None, reference_number: str = None,
                          session: Session = None) -> Any:
        """
        Add unit purchase event through proper orchestration.
        
        Args:
            fund_id: ID of the fund
            units: Number of units purchased
            price: Price per unit
            date: Date of the purchase
            description: Description of the purchase
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created unit purchase event
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            raise ValueError(f"Fund with ID {fund_id} not found")
        
        # Use orchestrator for event processing
        event_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'units_purchased': units,
            'unit_price': price,
            'event_date': date,
            'description': description or f"Unit purchase: {units:.4f} units @ ${price:.4f}",
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, fund)
    
    def add_unit_sale(self, fund_id: int, units: float, price: float, date: date,
                      description: str = None, reference_number: str = None,
                      session: Session = None) -> Any:
        """
        Add unit sale event through proper orchestration.
        
        Args:
            fund_id: ID of the fund
            units: Number of units sold
            price: Price per unit
            date: Date of the sale
            description: Description of the sale
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created unit sale event
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            raise ValueError(f"Fund with ID {fund_id} not found")
        
        # Use orchestrator for event processing
        event_data = {
            'event_type': EventType.UNIT_SALE,
            'units_sold': units,
            'unit_price': price,
            'event_date': date,
            'description': description or f"Unit sale: {units:.4f} units @ ${price:.4f}",
            'reference_number': reference_number
        }
        
        return self.orchestrator.process_fund_event(event_data, session, fund)
    
    def get_fund_end_date(self, fund_id: int, session: Session) -> Optional[date]:
        """
        Get fund end date using status service.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            date or None: Fund end date if fund is completed or realized
        """
        fund = self.fund_repository.get_by_id(fund_id, session)
        if not fund:
            return None
        
        if fund.status not in [FundStatus.COMPLETED, FundStatus.REALIZED]:
            return None
        
        # Use status service for calculation
        from src.fund.services.fund_status_service import FundStatusService
        status_service = FundStatusService()
        return status_service.calculate_end_date(fund, session)
