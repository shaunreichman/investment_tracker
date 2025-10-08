"""
Company Repository.

"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload

from src.investment_company.models import InvestmentCompany
from src.investment_company.enums.company_enums import CompanyStatus, CompanyType, SortFieldCompany
from src.shared.enums.shared_enums import SortOrder


class CompanyRepository:
    """
    Company Repository.

    This repository handles all database operations for companies including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    company data without direct database access.
    """
    
    def __init__(self):
        """
        Initialize the company repository.
        
        Args:
            None
        """
        pass


    ################################################################################
    # Get companies
    ################################################################################

    def get_companies(self, session: Session,
            company_types: Optional[List[CompanyType]] = None,
            statuses: Optional[List[CompanyStatus]] = None,
            names: Optional[List[str]] = None,
            sort_by: Optional[SortFieldCompany] = SortFieldCompany.NAME,
            sort_order: Optional[SortOrder] = SortOrder.ASC,
            include_contacts: Optional[bool] = False,
    ) -> List[InvestmentCompany]:
        """
        Get all companies.

        Args:
            session: Database session
            company_types: Types of company to filter by
            statuses: Statuses to filter by
            names: Names to filter by
            sort_by: Field to sort by
            sort_order: Order to sort by
            include_contacts: Whether to eager load contacts relationship

        Returns:
            List of companies
        """
        # Validate sort field
        if sort_by not in SortFieldCompany:
            raise ValueError(f"Invalid sort field: {sort_by}")
        
        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        # Query database
        query = session.query(InvestmentCompany)
        
        # Add eager loading for relationships if requested
        if include_contacts:
            query = query.options(selectinload(InvestmentCompany.contacts))
        
        if company_types:
            query = query.filter(InvestmentCompany.company_type.in_([c.value for c in company_types]))
        if statuses:
            query = query.filter(InvestmentCompany.status.in_([s.value for s in statuses]))
        if names:
            query = query.filter(InvestmentCompany.name.in_(names))
            
        # Apply sorting
        if sort_by == SortFieldCompany.NAME:
            query = query.order_by(InvestmentCompany.name.asc() if sort_order == SortOrder.ASC else InvestmentCompany.name.desc())
        elif sort_by == SortFieldCompany.STATUS:
            query = query.order_by(InvestmentCompany.status.asc() if sort_order == SortOrder.ASC else InvestmentCompany.status.desc())
        elif sort_by == SortFieldCompany.START_DATE:
            query = query.order_by(InvestmentCompany.start_date.asc() if sort_order == SortOrder.ASC else InvestmentCompany.start_date.desc())
        elif sort_by == SortFieldCompany.CREATED_AT:
            query = query.order_by(InvestmentCompany.created_at.asc() if sort_order == SortOrder.ASC else InvestmentCompany.created_at.desc())
        elif sort_by == SortFieldCompany.UPDATED_AT:
            query = query.order_by(InvestmentCompany.updated_at.asc() if sort_order == SortOrder.ASC else InvestmentCompany.updated_at.desc())
            
        companies = query.all()

        return companies
    
    def get_company_by_id(self, company_id: int, session: Session, include_contacts: Optional[bool] = False) -> Optional[InvestmentCompany]:
        """
        Get a company by its ID.
        
        Args:
            company_id: ID of the company to retrieve
            session: Database session
            include_contacts: Whether to eager load contacts relationship
            
        Returns:
            InvestmentCompany object if found, None otherwise
        """
        # Query database
        query = session.query(InvestmentCompany).filter(InvestmentCompany.id == company_id)
        
        # Add eager loading for relationships if requested
        if include_contacts:
            query = query.options(selectinload(InvestmentCompany.contacts))
        
        company = query.first()
        
        return company


    ################################################################################
    # Create Company
    ################################################################################
    
    def create_company(self, company_data: Dict[str, Any], session: Session) -> InvestmentCompany:
        """
        Create a new investment company.
        
        Args:
            company_data: Dictionary containing company data
            session: Database session
            
        Returns:
            The created InvestmentCompany object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """        
        company = InvestmentCompany(**company_data)
        session.add(company)
        session.flush()
        
        return company
    
    
    ################################################################################
    # Delete Company
    ################################################################################
    
    def delete_company(self, company_id: int, session: Session) -> bool:
        """
        Delete an investment company.
        
        Args:
            company_id: ID of the company to delete
            session: Database session
            
        Returns:
            True if company was deleted, False if not found
        """
        company = self.get_company_by_id(company_id, session)
        if not company:
            return False
        
        session.delete(company)
        session.flush()
        
        return True