"""
Fund Tax Statement Repository.
"""

from typing import Dict, Any, List, Optional
from datetime import date
from sqlalchemy.orm import Session

from src.fund.models import FundTaxStatement
from src.fund.enums.fund_tax_statement_enums import SortFieldFundTaxStatement
from src.shared.enums.shared_enums import SortOrder

class FundTaxStatementRepository:
    """
    Fund Tax Statement Repository.

    This repository handles all database operations for fund tax statements including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    fund tax statement data without direct database access.
    """

    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the fund tax statement repository.

        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl


    ################################################################################
    # Get Fund Tax Statement
    ################################################################################

    def get_fund_tax_statements(self, session: Session,
                                fund_id: Optional[int] = None,
                                entity_id: Optional[int] = None,
                                financial_year: Optional[str] = None,
                                start_tax_payment_date: Optional[date] = None,
                                end_tax_payment_date: Optional[date] = None,
                                sort_by: SortFieldFundTaxStatement = SortFieldFundTaxStatement.FINANCIAL_YEAR,
                                sort_order: SortOrder = SortOrder.ASC) -> List[FundTaxStatement]:
        """
        Get all fund tax statements.

        Args:
            session: Database session
            fund_id: ID of the fund to filter by (optional)
            entity_id: ID of the entity to filter by (optional)
            financial_year: Financial year to filter by (optional)
            start_tax_payment_date: Start tax payment date to filter by (optional)
            end_tax_payment_date: End tax payment date to filter by (optional)
            sort_by: Field to sort by (optional)
            sort_order: Order to sort by (optional)

        Returns:
            List[FundTaxStatement]: List of fund tax statements
        """
        cache_key = f"fund_tax_statements:fund_id:{fund_id}:entity_id:{entity_id}:financial_year:{financial_year}:sort_by:{sort_by.value}:sort_order:{sort_order.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Validate sort field
        if sort_by not in SortFieldFundTaxStatement:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")
        
        # Query database
        query = session.query(FundTaxStatement)

        if fund_id:
            query = query.filter(FundTaxStatement.fund_id == fund_id)
        if entity_id:
            query = query.filter(FundTaxStatement.entity_id == entity_id)
        if financial_year:
            query = query.filter(FundTaxStatement.financial_year == financial_year)
        if start_tax_payment_date:
            query = query.filter(FundTaxStatement.tax_payment_date >= start_tax_payment_date)
        if end_tax_payment_date:
            query = query.filter(FundTaxStatement.tax_payment_date <= end_tax_payment_date)

        # Sort the results
        if sort_by == SortFieldFundTaxStatement.FINANCIAL_YEAR:
            query = query.order_by(FundTaxStatement.financial_year.asc() if sort_order == SortOrder.ASC else FundTaxStatement.financial_year.desc())
        elif sort_by == SortFieldFundTaxStatement.TAX_PAYMENT_DATE:
            query = query.order_by(FundTaxStatement.tax_payment_date.asc() if sort_order == SortOrder.ASC else FundTaxStatement.tax_payment_date.desc())
        elif sort_by == SortFieldFundTaxStatement.CREATED_AT:
            query = query.order_by(FundTaxStatement.created_at.asc() if sort_order == SortOrder.ASC else FundTaxStatement.created_at.desc())
        elif sort_by == SortFieldFundTaxStatement.UPDATED_AT:
            query = query.order_by(FundTaxStatement.updated_at.asc() if sort_order == SortOrder.ASC else FundTaxStatement.updated_at.desc())

        # Execute the query
        fund_tax_statements = query.all()

        # Cache the result
        self._cache[cache_key] = fund_tax_statements

        return fund_tax_statements

    def get_fund_tax_statement_by_id(self, fund_tax_statement_id: int, session: Session) -> Optional[FundTaxStatement]:
        """
        Get a fund tax statement by ID.

        Args:
            fund_tax_statement_id: ID of the fund tax statement to retrieve
            session: Database session

        Returns:
            FundTaxStatement object if found, None otherwise
        """
        cache_key = f"fund_tax_statement:{fund_tax_statement_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        fund_tax_statement = session.query(FundTaxStatement).filter(FundTaxStatement.id == fund_tax_statement_id).first()
        
        # Cache the result
        if fund_tax_statement:
            self._cache[cache_key] = fund_tax_statement
        
        return fund_tax_statement


    ################################################################################
    # Create Fund Tax Statement
    ################################################################################
    
    def create_fund_tax_statement(self, fund_tax_statement_data: Dict[str, Any], session: Session) -> FundTaxStatement:
        """
        Create a new fund tax statement.

        Args:
            fund_tax_statement_data: Dictionary containing fund tax statement data
            session: Database session

        Returns:
            FundTaxStatement: The created fund tax statement
        """
        # Create fund tax statement object
        fund_tax_statement = FundTaxStatement(**fund_tax_statement_data)
        session.add(fund_tax_statement)
        session.flush()  # Get the ID without committing
        
        # Cache the result
        self._cache[f"fund_tax_statement:{fund_tax_statement.id}"] = fund_tax_statement
        
        return fund_tax_statement
    

    ################################################################################
    # Delete Fund Tax Statement
    ################################################################################

    def delete_fund_tax_statement(self, fund_tax_statement_id: int, session: Session) -> bool:
        """
        Delete a fund tax statement.

        Args:
            fund_tax_statement_id: ID of the fund tax statement to delete
            session: Database session
        """
        fund_tax_statement = self.get_fund_tax_statement_by_id(fund_tax_statement_id, session)
        if not fund_tax_statement:
            return False
        
        # Delete the fund tax statement
        session.delete(fund_tax_statement)

        # Clear cache
        self._clear_fund_tax_statement_cache(fund_tax_statement_id)
        
        return True


    ################################################################################
    # Clear Cache
    ################################################################################
    
    def _clear_fund_tax_statement_cache(self, fund_tax_statement_id: int) -> None:
        """Clear cache for a specific fund tax statement."""
        cache_key = f"fund_tax_statement:{fund_tax_statement_id}"
        self._cache.pop(cache_key, None)