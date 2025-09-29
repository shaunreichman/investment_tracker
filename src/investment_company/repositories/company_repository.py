"""
Company Repository.

"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.investment_company.models import InvestmentCompany
from src.investment_company.enums.company_enums import CompanyStatus, CompanyType, SortFieldCompany
from src.shared.enums.shared_enums import SortOrder


class CompanyRepository:
    """
    Company Repository.

    This repository handles all database operations for companies including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    company data without direct database access.
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the company repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl


    ################################################################################
    # Get companies
    ################################################################################

    def get_companies(self, session: Session,
            company_type: Optional[CompanyType] = None,
            status: Optional[CompanyStatus] = None,
            name: Optional[str] = None,
            sort_by: Optional[SortFieldCompany] = SortFieldCompany.NAME,
            sort_order: Optional[SortOrder] = SortOrder.ASC,
    ) -> List[InvestmentCompany]:
        """
        Get all companies.

        Args:
            session: Database session
            company_type: Type of company to filter by
            status: Status to filter by
            name: Name to filter by
            sort_by: Field to sort by
            sort_order: Order to sort by

        Returns:
            List of companies
        """
        # Validate sort field
        if sort_by not in SortFieldCompany:
            raise ValueError(f"Invalid sort field: {sort_by}")
        
        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        cache_key = f"companies:company_type:{company_type}:status:{status}:name:{name}:sort_by:{sort_by}:sort_order:{sort_order}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        companies = session.query(InvestmentCompany)
        if company_type:
            companies = companies.filter(InvestmentCompany.company_type == company_type)
        if status:
            companies = companies.filter(InvestmentCompany.status == status)
        if name:
            companies = companies.filter(InvestmentCompany.name == name)
            
        # Apply sorting
        if sort_by == SortFieldCompany.NAME:
            companies = companies.order_by(InvestmentCompany.name.asc() if sort_order == SortOrder.ASC else InvestmentCompany.name.desc())
        elif sort_by == SortFieldCompany.STATUS:
            companies = companies.order_by(InvestmentCompany.status.asc() if sort_order == SortOrder.ASC else InvestmentCompany.status.desc())
        elif sort_by == SortFieldCompany.START_DATE:
            companies = companies.order_by(InvestmentCompany.start_date.asc() if sort_order == SortOrder.ASC else InvestmentCompany.start_date.desc())
        elif sort_by == SortFieldCompany.CREATED_AT:
            companies = companies.order_by(InvestmentCompany.created_at.asc() if sort_order == SortOrder.ASC else InvestmentCompany.created_at.desc())
        elif sort_by == SortFieldCompany.UPDATED_AT:
            companies = companies.order_by(InvestmentCompany.updated_at.asc() if sort_order == SortOrder.ASC else InvestmentCompany.updated_at.desc())
            
        companies = companies.all()

        # Cache the result
        self._cache[cache_key] = companies

        return companies
    
    def get_company_by_id(self, company_id: int, session: Session) -> Optional[InvestmentCompany]:
        """
        Get a company by its ID.
        
        Args:
            company_id: ID of the company to retrieve
            session: Database session
            
        Returns:
            InvestmentCompany object if found, None otherwise
        """
        cache_key = f"company:{company_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        company = session.query(InvestmentCompany).filter(InvestmentCompany.id == company_id).first()
        
        # Cache the result
        if company:
            self._cache[cache_key] = company
        
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
        
        # Clear cache
        self._clear_company_caches()
        
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
        
        # Clear cache
        self._clear_company_caches()
        
        return True


    ################################################################################
    # Clear Cache
    ################################################################################
    
    def _clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
    
    def _clear_company_caches(self) -> None:
        """Clear all company-related caches."""
        keys_to_remove = [key for key in self._cache.keys() if key.startswith('company')]
        for key in keys_to_remove:
            del self._cache[key]

    def _clear_company_cache(self, company_id: int, company_type: Optional[CompanyType] = None, status: Optional[CompanyStatus] = None, name: Optional[str] = None, sort_by: Optional[SortFieldCompany] = None, sort_order: Optional[SortOrder] = None) -> None:
        """Clear cache for a specific company."""
        keys_to_remove = [key for key in self._cache.keys() if key.startswith('company')]
        cache_keys_to_remove = [
            f"company:{company_id}",
            f"companies:company_type:{company_type}:status:{status}:name:{name}:sort_by:{sort_by}:sort_order:{sort_order}",
        ]
        
        for key in cache_keys_to_remove:
            if key in self._cache:
                del self._cache[key]
