"""
Fund Coordination Service.

This service handles fund creation coordination between company and fund domains,
implementing clean separation of concerns and enterprise-grade architecture.

Key responsibilities:
- Fund creation coordination with fund domain
- Cross-domain event publishing
- Fund validation and business rule coordination
- Portfolio update coordination
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import date
from sqlalchemy.orm import Session

from src.investment_company.models import InvestmentCompany
from src.fund.models import Fund
from src.entity.models import Entity

if TYPE_CHECKING:
    from src.fund.services.fund_service import FundService


class FundCoordinationService:
    """
    Service for coordinating fund operations between company and fund domains.
    
    This service handles the coordination aspects of fund creation without
    duplicating fund business logic. It ensures proper cross-domain
    communication and event publishing.
    
    Attributes:
        fund_service (FundService): Service for fund operations
    """
    
    def __init__(self, fund_service: 'FundService' = None):
        """Initialize the fund coordination service."""
        self.fund_service = fund_service
    
    # ============================================================================
    # FUND CREATION COORDINATION
    # ============================================================================
    
    def coordinate_fund_creation(self, company: InvestmentCompany, entity: Entity, 
                                fund_data: Dict[str, Any], session: Session) -> Fund:
        """
        Coordinate fund creation between company and fund domains.
        
        This method coordinates the creation of a fund while maintaining
        proper domain boundaries and single source of truth.
        
        Args:
            company: InvestmentCompany object
            entity: The entity that will invest in the fund
            fund_data: Fund creation data
            session: Database session
        
        Returns:
            Fund: The created fund
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate coordination prerequisites
        self._validate_fund_creation_prerequisites(company, entity, fund_data)
        
        # Prepare fund data with required fields
        complete_fund_data = fund_data.copy()
        complete_fund_data['entity_id'] = entity.id
        complete_fund_data['investment_company_id'] = company.id
        
        # Delegate fund creation to fund domain service (single source of truth)
        fund = self._create_fund_in_fund_domain(complete_fund_data, session)
        
        # Update company portfolio after fund creation
        self._update_company_portfolio_after_fund_creation(company, fund, session)
        
        # Publish cross-domain events for coordination
        self._publish_fund_creation_events(company, fund, session)
        
        return fund
    
    def _validate_fund_creation_prerequisites(self, company: InvestmentCompany, 
                                            entity: Entity, fund_data: Dict[str, Any]) -> None:
        """
        Validate prerequisites for fund creation coordination.
        
        Args:
            company: InvestmentCompany object
            entity: The entity that will invest in the fund
            fund_data: Fund creation data
        
        Raises:
            ValueError: If prerequisites are not met
        """
        if company is None:
            raise ValueError("Company is required for fund creation coordination")
        
        if entity is None:
            raise ValueError("Entity is required for fund creation coordination")
        
        if not fund_data.get('name'):
            raise ValueError("Fund name is required")
        
        if not fund_data.get('fund_type'):
            raise ValueError("Fund type is required")
        
        if not fund_data.get('tracking_type'):
            raise ValueError("Tracking type is required")
    
    def _create_fund_in_fund_domain(self, fund_data: Dict[str, Any], session: Session) -> Fund:
        """
        Create fund in the fund domain (single source of truth).
        
        Args:
            fund_data: Fund creation data
            session: Database session
        
        Returns:
            Fund: The created fund
        """
        if not self.fund_service:
            from src.fund.services.fund_service import FundService
            self.fund_service = FundService()
        
        fund_result = self.fund_service.create_fund(fund_data, session)
        
        # Get the created fund from the result
        return self._get_fund_by_id(fund_result['id'], session)
    
    def _get_fund_by_id(self, fund_id: int, session: Session) -> Fund:
        """
        Get fund by ID from the fund domain.
        
        Args:
            fund_id: Fund ID
            session: Database session
            
        Returns:
            Fund: The fund instance
        """
        from src.fund.repositories.fund_repository import FundRepository
        fund_repository = FundRepository()
        return fund_repository.get_by_id(fund_id, session)
    
    def _update_company_portfolio_after_fund_creation(self, company: InvestmentCompany, 
                                                     fund: Fund, session: Session) -> None:
        """
        Update company portfolio after fund creation.
        
        Args:
            company: InvestmentCompany object
            fund: The created fund
            session: Database session
        """
        # This method coordinates with CompanyPortfolioService for portfolio updates
        # without duplicating portfolio logic
        from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
        from src.investment_company.services.company_calculation_service import CompanyCalculationService
        calculation_service = CompanyCalculationService()
        portfolio_service = CompanyPortfolioService(calculation_service=calculation_service)
        
        # Trigger portfolio summary recalculation
        portfolio_service._trigger_portfolio_summary_recalculation(company, session)
    
    def _publish_fund_creation_events(self, company: InvestmentCompany, 
                                     fund: Fund, session: Session) -> None:
        """
        Publish cross-domain events for fund creation coordination.
        
        Args:
            company: InvestmentCompany object
            fund: The created fund
            session: Database session
        """
        from src.investment_company.events.domain.portfolio_updated_event import PortfolioUpdatedEvent
        from src.investment_company.events.registry import CompanyEventHandlerRegistry
        
        # Create portfolio updated event
        event = PortfolioUpdatedEvent(
            company_id=company.id,
            event_date=date.today(),
            fund_id=fund.id,
            operation='added'
        )
        
        # Publish event through registry
        registry = CompanyEventHandlerRegistry()
        event_data = {
            'event_type': 'PORTFOLIO_UPDATED',
            'company_id': company.id,
            'event_date': event.event_date.isoformat(),
            'fund_id': fund.id,
            'operation': 'added'
        }
        registry.handle_event(event_data, session, company)
    
    # ============================================================================
    # FUND VALIDATION COORDINATION
    # ============================================================================
    
    def validate_fund_creation_business_rules(self, company: InvestmentCompany, 
                                            entity: Entity, fund_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fund creation business rules across domains.
        
        Args:
            company: InvestmentCompany object
            entity: The entity that will invest in the fund
            fund_data: Fund creation data
            session: Database session
        
        Returns:
            Dict containing validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate company-level business rules
        company_validation = self._validate_company_business_rules(company, fund_data)
        if not company_validation['is_valid']:
            validation_results['is_valid'] = False
            validation_results['errors'].extend(company_validation['errors'])
        
        # Validate entity-level business rules
        entity_validation = self._validate_entity_business_rules(entity, fund_data)
        if not entity_validation['is_valid']:
            validation_results['is_valid'] = False
            validation_results['errors'].extend(entity_validation['errors'])
        
        # Add warnings
        validation_results['warnings'].extend(company_validation.get('warnings', []))
        validation_results['warnings'].extend(entity_validation.get('warnings', []))
        
        return validation_results
    
    def _validate_company_business_rules(self, company: InvestmentCompany, 
                                       fund_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate company-level business rules for fund creation.
        
        Args:
            company: InvestmentCompany object
            fund_data: Fund creation data
        
        Returns:
            Dict containing validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check if company can create more funds
        if hasattr(company, 'max_funds') and company.max_funds:
            current_fund_count = len(company.funds) if company.funds else 0
            if current_fund_count >= company.max_funds:
                validation_results['is_valid'] = False
                validation_results['errors'].append(
                    f"Company has reached maximum fund limit of {company.max_funds}"
                )
        
        # Check company status
        if hasattr(company, 'status') and company.status:
            if company.status.value == 'INACTIVE':
                validation_results['warnings'].append(
                    "Company is inactive - fund creation may be restricted"
                )
        
        return validation_results
    
    def _validate_entity_business_rules(self, entity: Entity, 
                                      fund_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate entity-level business rules for fund creation.
        
        Args:
            entity: Entity object
            fund_data: Fund creation data
        
        Returns:
            Dict containing validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check entity status
        if hasattr(entity, 'status') and entity.status:
            if entity.status.value == 'INACTIVE':
                validation_results['warnings'].append(
                    "Entity is inactive - fund creation may be restricted"
                )
        
        # Check entity ABN (if applicable)
        if hasattr(entity, 'abn') and entity.abn is not None:
            if len(entity.abn) < 11:
                validation_results['warnings'].append(
                    "Entity ABN appears invalid - please verify"
                )
        
        return validation_results
