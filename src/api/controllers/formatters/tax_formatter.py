"""
Formatters for Tax objects.

- Provide consistent response structure for tax-related data
"""

from typing import Dict, Any
from src.tax.models import TaxStatement


def format_tax_statement(tax_statement: TaxStatement) -> Dict[str, Any]:
    """
    Format a TaxStatement object for HTTP response.
    
    Args:
        tax_statement: The TaxStatement domain object
        
    Returns:
        Dictionary formatted for HTTP response with improved ordering and consistent formatting
    """
    return {
        # Core identification fields
        'id': tax_statement.id,
        'fund_id': tax_statement.fund_id,
        'entity_id': tax_statement.entity_id,
        'financial_year': tax_statement.financial_year,
        
        # Dates
        'statement_date': tax_statement.statement_date.isoformat() if tax_statement.statement_date else None,
        'tax_payment_date': tax_statement.tax_payment_date.isoformat() if tax_statement.tax_payment_date else None,
        
        # Interest income fields
        'interest_income_amount': float(tax_statement.interest_income_amount) if tax_statement.interest_income_amount is not None else None,
        'interest_income_tax_rate': float(tax_statement.interest_income_tax_rate) if tax_statement.interest_income_tax_rate is not None else None,
        'interest_tax_amount': float(tax_statement.interest_tax_amount) if tax_statement.interest_tax_amount is not None else None,
        'interest_received_in_cash': float(tax_statement.interest_received_in_cash) if tax_statement.interest_received_in_cash is not None else None,
        'interest_receivable_this_fy': float(tax_statement.interest_receivable_this_fy) if tax_statement.interest_receivable_this_fy is not None else None,
        'interest_receivable_prev_fy': float(tax_statement.interest_receivable_prev_fy) if tax_statement.interest_receivable_prev_fy is not None else None,
        'interest_non_resident_withholding_tax_from_statement': float(tax_statement.interest_non_resident_withholding_tax_from_statement) if tax_statement.interest_non_resident_withholding_tax_from_statement is not None else None,
        'interest_non_resident_withholding_tax_already_withheld': float(tax_statement.interest_non_resident_withholding_tax_already_withheld) if tax_statement.interest_non_resident_withholding_tax_already_withheld is not None else None,
        
        # Dividend income fields
        'dividend_franked_income_amount': float(tax_statement.dividend_franked_income_amount) if tax_statement.dividend_franked_income_amount is not None else None,
        'dividend_unfranked_income_amount': float(tax_statement.dividend_unfranked_income_amount) if tax_statement.dividend_unfranked_income_amount is not None else None,
        'dividend_franked_income_tax_rate': float(tax_statement.dividend_franked_income_tax_rate) if tax_statement.dividend_franked_income_tax_rate is not None else None,
        'dividend_unfranked_income_tax_rate': float(tax_statement.dividend_unfranked_income_tax_rate) if tax_statement.dividend_unfranked_income_tax_rate is not None else None,
        'dividend_franked_tax_amount': float(tax_statement.dividend_franked_tax_amount) if tax_statement.dividend_franked_tax_amount is not None else None,
        'dividend_unfranked_tax_amount': float(tax_statement.dividend_unfranked_tax_amount) if tax_statement.dividend_unfranked_tax_amount is not None else None,
        'dividend_franked_income_amount_from_tax_statement_flag': bool(tax_statement.dividend_franked_income_amount_from_tax_statement_flag) if tax_statement.dividend_franked_income_amount_from_tax_statement_flag is not None else None,
        'dividend_unfranked_income_amount_from_tax_statement_flag': bool(tax_statement.dividend_unfranked_income_amount_from_tax_statement_flag) if tax_statement.dividend_unfranked_income_amount_from_tax_statement_flag is not None else None,
        
        # Capital gains fields
        'capital_gain_income_amount': float(tax_statement.capital_gain_income_amount) if tax_statement.capital_gain_income_amount is not None else None,
        'capital_gain_income_tax_rate': float(tax_statement.capital_gain_income_tax_rate) if tax_statement.capital_gain_income_tax_rate is not None else None,
        'capital_gain_tax_amount': float(tax_statement.capital_gain_tax_amount) if tax_statement.capital_gain_tax_amount is not None else None,
        'capital_gain_discount_amount': float(tax_statement.capital_gain_discount_amount) if tax_statement.capital_gain_discount_amount is not None else None,
        'capital_gain_income_amount_from_tax_statement_flag': bool(tax_statement.capital_gain_income_amount_from_tax_statement_flag) if tax_statement.capital_gain_income_amount_from_tax_statement_flag is not None else None,
        
        # EOFY debt interest deduction fields
        'eofy_debt_interest_deduction_sum_of_daily_interest': float(tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest) if tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest is not None else None,
        'eofy_debt_interest_deduction_rate': float(tax_statement.eofy_debt_interest_deduction_rate) if tax_statement.eofy_debt_interest_deduction_rate is not None else None,
        'eofy_debt_interest_deduction_total_deduction': float(tax_statement.eofy_debt_interest_deduction_total_deduction) if tax_statement.eofy_debt_interest_deduction_total_deduction is not None else None,
        
        # Status and metadata
        'non_resident': bool(tax_statement.non_resident) if tax_statement.non_resident is not None else None,
        'accountant': tax_statement.accountant,
        'notes': tax_statement.notes,
        
        # Timestamps
        'created_at': tax_statement.created_at.isoformat() if tax_statement.created_at else None,
        'updated_at': tax_statement.updated_at.isoformat() if tax_statement.updated_at else None
    }
