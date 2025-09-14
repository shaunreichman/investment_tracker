"""
Formatters for Fund objects.

- Provide consistent response structure
"""

from typing import Dict, Any, Optional, List
from src.fund.models import Fund, FundEvent, FundEventCashFlow
from src.api.controllers.formatters.tax_formatter import format_tax_statement

def format_fund(fund: Fund) -> Dict[str, Any]:
    """
    Format a Fund object for HTTP response.
    
    Args:
        fund: The Fund domain object
        
    Returns:
        Dictionary formatted for HTTP response with improved ordering and consistent formatting
    """
    return {
        # Core identification fields
        'id': fund.id,
        'name': fund.name,
        
        # Fund classification
        'status': fund.status.value.upper() if fund.status else None,
        'fund_type': fund.fund_type.value.upper() if hasattr(fund.fund_type, 'value') else fund.fund_type,
        'tracking_type': fund.tracking_type.value.upper() if hasattr(fund.tracking_type, 'value') else fund.tracking_type,
        
        # Relationships
        'entity_id': fund.entity_id,
        'investment_company_id': fund.investment_company_id,
        
        # Basic fund information
        'currency': fund.currency,
        'description': fund.description,
        
        # Commitment and duration
        'commitment_amount': float(fund.commitment_amount) if fund.commitment_amount is not None else None,
        'expected_irr': float(fund.expected_irr) if fund.expected_irr is not None else None,
        'expected_duration_months': fund.expected_duration_months,
        'current_duration': fund.current_duration,
        
        # Equity and balance information
        'current_equity_balance': float(fund.current_equity_balance) if fund.current_equity_balance is not None else None,
        'average_equity_balance': float(fund.average_equity_balance) if fund.average_equity_balance is not None else None,
        
        # Profitability metrics (CALCULATED)
        'pnl': float(fund.pnl) if fund.pnl is not None else None,
        'realized_pnl': float(fund.realized_pnl) if fund.realized_pnl is not None else None,
        'unrealized_pnl': float(fund.unrealized_pnl) if fund.unrealized_pnl is not None else None,
        'realized_pnl_capital_gain': float(fund.realized_pnl_capital_gain) if fund.realized_pnl_capital_gain is not None else None,
        'unrealized_pnl_capital_gain': float(fund.unrealized_pnl_capital_gain) if fund.unrealized_pnl_capital_gain is not None else None,
        'realized_pnl_dividend': float(fund.realized_pnl_dividend) if fund.realized_pnl_dividend is not None else None,
        'realized_pnl_interest': float(fund.realized_pnl_interest) if fund.realized_pnl_interest is not None else None,
        'realized_pnl_distribution': float(fund.realized_pnl_distribution) if fund.realized_pnl_distribution is not None else None,
        
        # IRR storage fields (CALCULATED)
        'completed_irr_gross': float(fund.completed_irr_gross) if fund.completed_irr_gross is not None else None,
        'completed_irr_after_tax': float(fund.completed_irr_after_tax) if fund.completed_irr_after_tax is not None else None,
        'completed_irr_real': float(fund.completed_irr_real) if fund.completed_irr_real is not None else None,
        
        # NAV-based fund fields (CALCULATED)
        'current_units': float(fund.current_units) if fund.current_units is not None else None,
        'current_unit_price': float(fund.current_unit_price) if fund.current_unit_price is not None else None,
        'current_nav_total': float(fund.current_nav_total) if fund.current_nav_total is not None else None,
        
        # Cost-based fund fields (CALCULATED)
        'total_cost_basis': float(fund.total_cost_basis) if fund.total_cost_basis is not None else None,
        
        # Dates
        'start_date': fund.start_date.isoformat() if fund.start_date else None,
        'end_date': fund.end_date.isoformat() if fund.end_date else None,
        
        # Timestamps
        'created_at': fund.created_at.isoformat() if fund.created_at else None,
        'updated_at': fund.updated_at.isoformat() if fund.updated_at else None
    }


def format_event(event: FundEvent) -> Dict[str, Any]:
    """
    Format a FundEvent object for HTTP response.
    
    Args:
        event: The FundEvent domain object
        
    Returns:
        Dictionary formatted for HTTP response with improved ordering and consistent formatting
    """
    return {
        # Core identification fields
        'id': event.id,
        'fund_id': event.fund_id,
        
        # Event type and timing
        'event_type': event.event_type.value.upper() if event.event_type else None,
        'event_date': event.event_date.isoformat() if event.event_date else None,
        
        # Financial amounts
        'amount': float(event.amount) if event.amount is not None else None,
        'unit_price': float(event.unit_price) if event.unit_price is not None else None,
        'brokerage_fee': float(event.brokerage_fee) if event.brokerage_fee is not None else None,
        'tax_withholding': float(event.tax_withholding) if event.tax_withholding is not None else None,
        
        # Unit transactions
        'units_purchased': float(event.units_purchased) if event.units_purchased is not None else None,
        'units_sold': float(event.units_sold) if event.units_sold is not None else None,
        'units_owned': float(event.units_owned) if event.units_owned is not None else None,
        
        # NAV information
        'nav_per_share': float(event.nav_per_share) if event.nav_per_share is not None else None,
        'previous_nav_per_share': float(event.previous_nav_per_share) if event.previous_nav_per_share is not None else None,
        'nav_change_absolute': float(event.nav_change_absolute) if event.nav_change_absolute is not None else None,
        'nav_change_percentage': float(event.nav_change_percentage) if event.nav_change_percentage is not None else None,
        
        # Distribution and tax information
        'distribution_type': event.distribution_type.value.upper() if event.distribution_type else None,
        'tax_payment_type': event.tax_payment_type.value.upper() if event.tax_payment_type else None,
        'tax_statement_id': event.tax_statement_id,
        'has_withholding_tax': bool(event.has_withholding_tax) if event.has_withholding_tax is not None else None,
        
        # Grouping information
        'is_grouped': bool(event.is_grouped) if event.is_grouped is not None else False,
        'group_id': event.group_id,
        'group_type': event.group_type.value.upper() if event.group_type else None,
        'group_position': event.group_position,
        
        # Status and completion
        'is_cash_flow_complete': bool(event.is_cash_flow_complete) if event.is_cash_flow_complete is not None else None,
        'current_equity_balance': float(event.current_equity_balance) if event.current_equity_balance is not None else None,
        
        # Descriptive fields
        'description': event.description,
        'reference_number': event.reference_number,
        
        # Timestamps
        'created_at': event.created_at.isoformat() if event.created_at else None,
        'updated_at': event.updated_at.isoformat() if event.updated_at else None
    }


def format_cash_flow(cash_flow: FundEventCashFlow) -> Dict[str, Any]:
    """
    Format a FundEventCashFlow object for HTTP response.
    
    Args:
        cash_flow: The FundEventCashFlow domain object
        
    Returns:
        Dictionary formatted for HTTP response with improved ordering and consistent formatting
    """
    return {
        # Core identification fields
        'id': cash_flow.id,
        'fund_event_id': cash_flow.fund_event_id,
        'bank_account_id': cash_flow.bank_account_id,
        
        # Cash flow details
        'direction': cash_flow.direction.value.upper() if cash_flow.direction else None,
        'transfer_date': cash_flow.transfer_date.isoformat() if cash_flow.transfer_date else None,
        'currency': cash_flow.currency,
        'amount': float(cash_flow.amount) if cash_flow.amount is not None else None,
        
        # Descriptive fields
        'reference': cash_flow.reference,
        'description': cash_flow.description,
        
        # Bank account information (if available)
        'bank_name': cash_flow.bank_account.bank.name if hasattr(cash_flow, 'bank_account') and cash_flow.bank_account else None,
        'account_name': cash_flow.bank_account.account_name if hasattr(cash_flow, 'bank_account') and cash_flow.bank_account else None,
    }


def format_fund_comprehensive(
    fund: Fund, 
    include_events: bool = True, 
    include_cash_flows: bool = False,
    include_tax_statements: bool = False
) -> Dict[str, Any]:
    """
    Main formatter method for comprehensive fund data with optional events, cash flows, and tax statements.
    
    Args:
        fund: The Fund domain object
        include_events: Whether to include fund events in the response
        include_cash_flows: Whether to include cash flows for each event
        include_tax_statements: Whether to include tax statements for the fund
        
    Returns:
        Dictionary formatted for HTTP response with comprehensive fund data
    """
    # Start with basic fund data
    fund_data = format_fund(fund)
    
    # Add events if requested
    if include_events:
        if hasattr(fund, 'events') and fund.events:
            events_data = []
            for event in fund.events:
                event_data = format_event(event)
                
                # Add cash flows if requested
                if include_cash_flows:
                    if hasattr(event, 'cash_flows') and event.cash_flows:
                        event_data['cash_flows'] = [format_cash_flow(cf) for cf in event.cash_flows]
                    else:
                        event_data['cash_flows'] = []
                
                events_data.append(event_data)
            
            fund_data['events'] = events_data
        else:
            fund_data['events'] = []
    
    # Add tax statements if requested
    if include_tax_statements:
        if hasattr(fund, 'tax_statements') and fund.tax_statements:
            # Sort by financial year descending (most recent first)
            sorted_statements = sorted(fund.tax_statements, key=lambda s: s.financial_year, reverse=True)
            fund_data['tax_statements'] = [format_tax_statement(statement) for statement in sorted_statements]
        else:
            fund_data['tax_statements'] = []
    
    return fund_data