"""
Formatters for Banking objects.

- Provide consistent response structure
"""

from typing import Dict, Any
from src.banking.models import Bank, BankAccount

def format_bank(bank: Bank) -> Dict[str, Any]:
    """
    Format a Bank object for HTTP response.
    """
    return {
        'id': bank.id,
        'name': bank.name,
        'country': bank.country,
        'swift_bic': bank.swift_bic,
        'created_at': bank.created_at.isoformat() if bank.created_at else None,
        'updated_at': bank.updated_at.isoformat() if bank.updated_at else None
    }

def format_bank_account(bank_account: BankAccount) -> Dict[str, Any]:
    """
    Format a BankAccount object for HTTP response.
    """
    return {
        'id': bank_account.id,
        'account_name': bank_account.account_name,
        'account_number': bank_account.account_number,
        'currency': bank_account.currency,
        'status': bank_account.status,
        'created_at': bank_account.created_at.isoformat() if bank_account.created_at else None,
        'updated_at': bank_account.updated_at.isoformat() if bank_account.updated_at else None
    }

def format_bank_comprehensive(bank: Bank, inlcude_bank_accounts: bool = False) -> Dict[str, Any]:
    """
    Format a Bank object with comprehensive data.
    """
    bank_data = format_bank(bank)

    # Add accounts if they exist
    if inlcude_bank_accounts:
        bank_data['accounts'] = [format_bank_account(account) for account in bank.accounts]
    else:
        bank_data['accounts'] = []

    return bank_data

