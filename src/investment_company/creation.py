"""
Investment company domain creation and management.

This module contains investment company creation and management functions.
"""

from sqlalchemy.orm import Session
from .models import InvestmentCompany


def create_investment_company(name, description=None, website=None, contact_email=None, contact_phone=None, session=None):
    """
    Create a new investment company.
    
    Args:
        name (str): Company name (must be unique)
        description (str, optional): Company description
        website (str, optional): Company website URL
        contact_email (str, optional): Contact email address
        contact_phone (str, optional): Contact phone number
        session (Session, optional): Database session
    
    Returns:
        InvestmentCompany: The created investment company
    """
    investment_company = InvestmentCompany(
        name=name,
        description=description,
        website=website,
        contact_email=contact_email,
        contact_phone=contact_phone
    )
    
    if session:
        session.add(investment_company)
        session.commit()
    
    return investment_company


def get_investment_company_by_name(name, session):
    """
    Get an investment company by name.
    
    Args:
        name (str): Company name
        session (Session): Database session
    
    Returns:
        InvestmentCompany or None: The investment company if found, None otherwise
    """
    return session.query(InvestmentCompany).filter(InvestmentCompany.name == name).first()


def get_all_investment_companies(session):
    """
    Get all investment companies.
    
    Args:
        session (Session): Database session
    
    Returns:
        list: List of all investment companies
    """
    return session.query(InvestmentCompany).all()


__all__ = [
    'create_investment_company',
    'get_investment_company_by_name',
    'get_all_investment_companies',
] 