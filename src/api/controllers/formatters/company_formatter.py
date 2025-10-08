"""
Formatters for Company objects.

- Provide consistent response structure
"""

from typing import Dict, Any
from src.investment_company.models import InvestmentCompany, Contact

def format_company(company: InvestmentCompany) -> Dict[str, Any]:
    """
    Format a Company object for HTTP response.

    Args:
        company: Company object to format

    Returns:
        Dictionary formatted for HTTP response
    """
    return {
        'id': company.id,
        'name': company.name,
        'description': company.description,
        'company_type': company.company_type.value if company.company_type else None,
        'status': company.status.value if company.status else None,
        'business_address': company.business_address,
        'website': company.website,
        'created_at': company.created_at.isoformat() if company.created_at else None,
        'updated_at': company.updated_at.isoformat() if company.updated_at else None
    }

def format_contact(contact: Contact) -> Dict[str, Any]:
    """
    Format a Contact object for HTTP response.

    Args:
        contact: Contact object to format

    Returns:
        Dictionary formatted for HTTP response
    """
    return {
        'id': contact.id,
        'name': contact.name,
        'title': contact.title,
        'direct_number': contact.direct_number,
        'direct_email': contact.direct_email,
        'notes': contact.notes,
        'created_at': contact.created_at.isoformat() if contact.created_at else None,
        'updated_at': contact.updated_at.isoformat() if contact.updated_at else None
    }

def format_company_comprehensive(company: InvestmentCompany, include_contacts: bool = False) -> Dict[str, Any]:
    """
    Format a Company object for HTTP response with comprehensive data.

    Args:
        company: Company object to format
        include_contacts: Whether to include contacts

    Returns:
        Dictionary formatted for HTTP response
    """

    company_data = format_company(company)

    # Add contacts if requested
    if include_contacts:
        if hasattr(company, 'contacts') and company.contacts:
            company_data['contacts'] = [format_contact(contact) for contact in company.contacts]
        else:
            company_data['contacts'] = []

    return company_data