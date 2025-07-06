"""
Investment company domain creation and management.

This module contains investment company utility functions and management operations.
"""

from sqlalchemy.orm import Session
from .models import InvestmentCompany
from ..shared.utils import with_database_session


@with_database_session
def get_investment_company_by_name(name, session=None):
    """
    Get an investment company by name.
    
    Args:
        name (str): Company name
        session (Session, optional): Database session (handled by @with_database_session)
    
    Returns:
        InvestmentCompany or None: The investment company if found, None otherwise
    """
    return session.query(InvestmentCompany).filter(InvestmentCompany.name == name).first()


@with_database_session
def get_all_investment_companies(session=None):
    """
    Get all investment companies.
    
    Args:
        session (Session, optional): Database session (handled by @with_database_session)
    
    Returns:
        list: List of all investment companies
    """
    return session.query(InvestmentCompany).all()


__all__ = [
    'get_investment_company_by_name',
    'get_all_investment_companies',
] 