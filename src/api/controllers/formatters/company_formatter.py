"""
Formatters for Company objects.

- Provide consistent response structure
"""

from typing import Dict, Any
from src.company.models import Company, Contact

def format_company(company: Company) -> Dict[str, Any]:
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
        'created_at': company.created_at.isoformat() if company.created_at else None,
        'updated_at': company.updated_at.isoformat() if company.updated_at else None,
        'business_address': company.business_address,
        'website': company.website,
        'total_funds': company.total_funds,
        'total_funds_active': company.total_funds_active,
        'total_funds_completed': company.total_funds_completed,
        'total_funds_realized': company.total_funds_realized,
        'total_commitment_amount': company.total_commitment_amount,
        'current_equity_balance': company.current_equity_balance,
        'average_equity_balance': company.average_equity_balance,
        'completed_irr_gross': company.completed_irr_gross,
        'completed_irr_after_tax': company.completed_irr_after_tax,
        'completed_irr_real': company.completed_irr_real,
        'pnl': company.pnl,
        'realized_pnl': company.realized_pnl,
        'unrealized_pnl': company.unrealized_pnl,
        'realized_pnl_capital_gain': company.realized_pnl_capital_gain,
        'unrealized_pnl_capital_gain': company.unrealized_pnl_capital_gain,
        'realized_pnl_dividend': company.realized_pnl_dividend,
        'realized_pnl_interest': company.realized_pnl_interest,
        'realized_pnl_distribution': company.realized_pnl_distribution,
        'status': company.status.value if company.status else None,
        'start_date': company.start_date.isoformat() if company.start_date else None,
        'end_date': company.end_date.isoformat() if company.end_date else None,
        'current_duration': company.current_duration
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

def format_company_comprehensive(company: Company, include_contacts: bool = False) -> Dict[str, Any]:
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