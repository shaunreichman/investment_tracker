"""
Company Repository.

This repository provides data access operations for InvestmentCompany entities,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Investment company CRUD operations
- Company querying and filtering
- Company relationship management
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.investment_company.models import InvestmentCompany
from src.fund.models import Fund
from src.fund.enums import FundStatus
from src.investment_company.enums import CompanyStatus, CompanyType


class CompanyRepository:
    """
    Repository for investment company data access operations.
    
    This repository handles all database operations for investment companies including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    company data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the company repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def get_by_id(self, company_id: int, session: Session) -> Optional[InvestmentCompany]:
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
    
    def get_by_name(self, name: str, session: Session) -> Optional[InvestmentCompany]:
        """
        Get a company by its name.
        
        Args:
            name: Name of the company to retrieve
            session: Database session
            
        Returns:
            InvestmentCompany object if found, None otherwise
        """
        cache_key = f"company:name:{name}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        company = session.query(InvestmentCompany).filter(InvestmentCompany.name == name).first()
        
        # Cache the result
        if company:
            self._cache[cache_key] = company
        
        return company
    
    def get_all(self, session: Session) -> List[InvestmentCompany]:
        """
        Get all investment companies.
        
        Args:
            session: Database session
            
        Returns:
            List of all investment companies
        """
        cache_key = "companies:all"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        companies = session.query(InvestmentCompany).all()
        
        # Cache the result
        self._cache[cache_key] = companies
        
        return companies
    
    def create(self, company_data: Dict[str, Any], session: Session) -> InvestmentCompany:
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
        # Validate required fields
        if 'name' not in company_data or not company_data['name']:
            raise ValueError("Company name is required")
        
        # Check for existing company with same name
        existing = self.get_by_name(company_data['name'], session)
        if existing:
            raise ValueError(f"Investment company with name '{company_data['name']}' already exists")
        
        # Create the company
        company = InvestmentCompany(**company_data)
        session.add(company)
        session.flush()  # Get the ID without committing
        
        # Clear cache
        self._clear_cache()
        
        return company
    
    def update(self, company_id: int, company_data: Dict[str, Any], session: Session) -> Optional[InvestmentCompany]:
        """
        Update an existing investment company.
        
        Args:
            company_id: ID of the company to update
            company_data: Dictionary containing updated company data
            session: Database session
            
        Returns:
            Updated InvestmentCompany object if found, None otherwise
        """
        company = self.get_by_id(company_id, session)
        if not company:
            return None
        
        # Update fields
        for key, value in company_data.items():
            if hasattr(company, key):
                setattr(company, key, value)
        
        # Update timestamp
        from datetime import datetime, timezone
        company.updated_at = datetime.now(timezone.utc)
        
        session.flush()
        
        # Clear cache
        self._clear_cache()
        
        return company
    
    def delete(self, company_id: int, session: Session) -> bool:
        """
        Delete an investment company.
        
        Args:
            company_id: ID of the company to delete
            session: Database session
            
        Returns:
            True if company was deleted, False if not found
        """
        company = self.get_by_id(company_id, session)
        if not company:
            return False
        
        session.delete(company)
        session.flush()
        
        # Clear cache
        self._clear_cache()
        
        return True
    
    def get_companies_with_fund_counts(self, session: Session) -> List[Dict[str, Any]]:
        """
        Get companies with optimized fund count queries.
        
        Args:
            session: Database session
            
        Returns:
            List of companies with fund count information
        """
        cache_key = "companies:with_fund_counts"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with optimized JOIN
        companies_data = session.query(
            InvestmentCompany,
            func.count(Fund.id).label('total_funds'),
            func.sum(Fund.commitment_amount).label('total_commitments'),
            func.sum(Fund.current_equity_balance).label('total_equity')
        ).outerjoin(Fund).group_by(InvestmentCompany.id).all()
        
        # Format results
        result = []
        for company, total_funds, total_commitments, total_equity in companies_data:
            result.append({
                "id": company.id,
                "name": company.name,
                "description": company.description,
                "website": company.website,
                "company_type": company.company_type,
                "business_address": company.business_address,
                "fund_count": total_funds or 0,
                "total_commitments": float(total_commitments) if total_commitments else 0.0,
                "total_equity_balance": float(total_equity) if total_equity else 0.0,
                "created_at": company.created_at.isoformat() if company.created_at else None,
                "updated_at": company.updated_at.isoformat() if company.updated_at else None
            })
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_companies_with_summary(self, session: Session) -> List[Dict[str, Any]]:
        """
        Get all companies with summary data including fund counts and totals.
        
        Args:
            session: Database session
            
        Returns:
            List of dictionaries containing company data with summary information
        """
        cache_key = "companies:with_summary"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get all companies with their relationships
        companies = session.query(InvestmentCompany).options(
            session.query(InvestmentCompany).load_only(
                InvestmentCompany.id, InvestmentCompany.name, InvestmentCompany.description,
                InvestmentCompany.website, InvestmentCompany.company_type, InvestmentCompany.status,
                InvestmentCompany.business_address, InvestmentCompany.created_at, InvestmentCompany.updated_at
            )
        ).all()
        
        result = []
        for company in companies:
            # Calculate summary data
            total_funds = len(company.funds) if company.funds else 0
            total_commitments = sum(fund.commitment_amount or 0.0 for fund in company.funds)
            total_equity = sum(fund.current_equity_balance or 0.0 for fund in company.funds)
            
            result.append({
                "id": company.id,
                "name": company.name,
                "description": company.description,
                "website": company.website,
                "company_type": company.company_type.value if company.company_type else None,
                "status": company.status.value if company.status else None,
                "business_address": company.business_address,
                "fund_count": total_funds or 0,
                "total_commitments": float(total_commitments) if total_commitments else 0.0,
                "total_equity_balance": float(total_equity) if total_equity else 0.0,
                "created_at": company.created_at.isoformat() if company.created_at else None,
                "updated_at": company.updated_at.isoformat() if company.updated_at else None
            })
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_companies_by_type(self, company_type: str, session: Session) -> List[InvestmentCompany]:
        """
        Get companies by company type.
        
        Args:
            company_type: Type of company to filter by
            session: Database session
            
        Returns:
            List of companies matching the type
        """
        cache_key = f"companies:type:{company_type}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        companies = session.query(InvestmentCompany).filter(InvestmentCompany.company_type == company_type).all()
        
        # Cache the result
        self._cache[cache_key] = companies
        
        return companies
    
    def get_companies_by_status(self, status: str, session: Session) -> List[InvestmentCompany]:
        """
        Get companies by status.
        
        Args:
            status: Status to filter by
            session: Database session
            
        Returns:
            List of companies matching the status
        """
        cache_key = f"companies:status:{status}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        companies = session.query(InvestmentCompany).filter(InvestmentCompany.status == status).all()
        
        # Cache the result
        self._cache[cache_key] = companies
        
        return companies
    
    def search_companies(self, search_term: str, session: Session) -> List[InvestmentCompany]:
        """
        Search companies by name or description.
        
        Args:
            search_term: Search term to look for
            session: Database session
            
        Returns:
            List of companies matching the search term
        """
        cache_key = f"companies:search:{search_term}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with search
        search_pattern = f"%{search_term}%"
        companies = session.query(InvestmentCompany).filter(
            or_(
                InvestmentCompany.name.ilike(search_pattern),
                InvestmentCompany.description.ilike(search_pattern),
                InvestmentCompany.company_type.ilike(search_pattern)
            )
        ).all()
        
        # Cache the result
        self._cache[cache_key] = companies
        
        return companies
    
    def get_companies_with_active_funds(self, session: Session) -> List[InvestmentCompany]:
        """
        Get companies that have active funds.
        
        Args:
            session: Database session
            
        Returns:
            List of companies with active funds
        """
        cache_key = "companies:with_active_funds"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        companies = session.query(InvestmentCompany).join(Fund).filter(Fund.status == FundStatus.ACTIVE).distinct().all()
        
        # Cache the result
        self._cache[cache_key] = companies
        
        return companies
    
    def _clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
    
    def _clear_company_cache(self, company_id: int) -> None:
        """Clear cache for a specific company."""
        cache_keys_to_remove = [
            f"company:{company_id}",
            "companies:all",
            "companies:with_fund_counts",
            "companies:with_active_funds"
        ]
        
        for key in cache_keys_to_remove:
            if key in self._cache:
                del self._cache[key]
