"""
Formatters for Fund objects.

- Provide consistent response structure
"""

from typing import Dict, Any
from src.fund.models import Fund, FundEvent

def format_fund(fund: Fund) -> Dict[str, Any]:
    """
    Format a Fund object for HTTP response.
    
    Args:
        fund: The Fund domain object
        
    Returns:
        Dictionary formatted for HTTP response
    """
    return {
        'id': fund.id,
        'name': fund.name,
        'status': fund.status.value if fund.status else None,
        'fund_type': fund.fund_type.value if hasattr(fund.fund_type, 'value') else fund.fund_type,
        'tracking_type': fund.tracking_type.value if hasattr(fund.tracking_type, 'value') else fund.tracking_type,
        'entity_id': fund.entity_id,
        'investment_company_id': fund.investment_company_id,
        'description': fund.description,
        'commitment_amount': fund.commitment_amount,
        'current_equity_balance': fund.current_equity_balance,
        'average_equity_balance': fund.average_equity_balance,
        'total_cost_basis': fund.total_cost_basis,
        'start_date': fund.start_date.isoformat() if fund.start_date else None,
        'end_date': fund.end_date.isoformat() if fund.end_date else None,
        'created_at': fund.created_at.isoformat() if fund.created_at else None,
        'updated_at': fund.updated_at.isoformat() if fund.updated_at else None
    }

def format_fund_with_events(fund: Fund) -> Dict[str, Any]:
    """
    Format a Fund object with events for HTTP response.
    
    Args:
        fund: The Fund domain object with events attached
        
    Returns:
        Dictionary formatted for HTTP response including events
    """
    fund_data = format_fund(fund)
    
    # Add events if they exist
    if hasattr(fund, 'events') and fund.events:
        fund_data['events'] = [format_event(event) for event in fund.events]
    else:
        fund_data['events'] = []
    
    return fund_data

def format_event(event: FundEvent) -> Dict[str, Any]:
    """
    Format a FundEvent object for HTTP response.
    
    Args:
        event: The FundEvent domain object
        
    Returns:
        Dictionary formatted for HTTP response
    """
    return {
        'id': event.id,
        'fund_id': event.fund_id,
        'event_type': event.event_type.value if event.event_type else None,
        'event_date': event.event_date.isoformat() if event.event_date else None,
        'amount': float(event.amount) if event.amount is not None else None,
        'description': event.description,
        'reference_number': event.reference_number,
        'nav_per_share': float(event.nav_per_share) if event.nav_per_share is not None else None,
        'previous_nav_per_share': float(event.previous_nav_per_share) if event.previous_nav_per_share is not None else None,
        'nav_change_absolute': float(event.nav_change_absolute) if event.nav_change_absolute is not None else None,
        'nav_change_percentage': float(event.nav_change_percentage) if event.nav_change_percentage is not None else None,
        'units_owned': float(event.units_owned) if event.units_owned is not None else None,
        'distribution_type': event.distribution_type.value if event.distribution_type else None,
        'tax_withholding': float(event.tax_withholding) if event.tax_withholding is not None else None,
        'has_withholding_tax': event.has_withholding_tax,
        'tax_payment_type': event.tax_payment_type.value if event.tax_payment_type else None,
        'tax_statement_id': event.tax_statement_id,
        'units_purchased': float(event.units_purchased) if event.units_purchased is not None else None,
        'units_sold': float(event.units_sold) if event.units_sold is not None else None,
        'unit_price': float(event.unit_price) if event.unit_price is not None else None,
        'brokerage_fee': float(event.brokerage_fee) if event.brokerage_fee is not None else None,
        'current_equity_balance': float(event.current_equity_balance) if event.current_equity_balance is not None else None,
        'is_cash_flow_complete': event.is_cash_flow_complete,
        'is_grouped': event.is_grouped,
        'group_id': event.group_id,
        'group_type': event.group_type.value if event.group_type else None,
        'group_position': event.group_position,
        'created_at': event.created_at.isoformat() if event.created_at else None,
        'updated_at': event.updated_at.isoformat() if event.updated_at else None
    }