"""
Formatters for API controllers.

- Provide consistent response structure
"""

from src.api.controllers.formatters.banking_formatter import format_bank, format_bank_account, format_bank_account_balance, format_bank_comprehensive, format_bank_account_comprehensive
from src.api.controllers.formatters.company_formatter import format_company, format_contact, format_company_comprehensive
from src.api.controllers.formatters.entity_formatter import format_entity
from src.api.controllers.formatters.fund_formatter import format_fund, format_fund_event, format_fund_event_cash_flow, format_fund_tax_statement, format_fund_comprehensive, format_fund_event_comprehensive
from src.api.controllers.formatters.rate_formatter import format_risk_free_rate

__all__ = [
    'format_bank',
    'format_bank_account',
    'format_bank_account_balance',
    'format_bank_comprehensive',
    'format_bank_account_comprehensive',
    'format_company',
    'format_contact',
    'format_company_comprehensive',
    'format_entity',
    'format_fund',
    'format_fund_event',
    'format_fund_event_cash_flow',
    'format_fund_tax_statement',
    'format_fund_comprehensive',
    'format_fund_event_comprehensive',
    'format_risk_free_rate',
]