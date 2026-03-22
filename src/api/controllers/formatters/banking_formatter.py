"""
Formatters for Banking objects.

- Provide consistent response structure
"""

from typing import Dict, Any
from src.banking.models import Bank, BankAccount, BankAccountBalance

def format_bank(bank: Bank) -> Dict[str, Any]:
    """
    Format a Bank object for HTTP response.

    Args:
        bank: Bank object to format

    Returns:
        Dictionary formatted for HTTP response
    """
    return {
        'id': bank.id,
        'name': bank.name,
        'country': bank.country.value if bank.country else None,
        'swift_bic': bank.swift_bic,
        'bank_type': bank.bank_type.value if bank.bank_type else None,
        'created_at': bank.created_at.isoformat() if bank.created_at else None,
        'updated_at': bank.updated_at.isoformat() if bank.updated_at else None,
        'status': bank.status.value if bank.status else None
    }

def format_bank_account(bank_account: BankAccount) -> Dict[str, Any]:
    """
    Format a BankAccount object for HTTP response.

    Args:
        bank_account: BankAccount object to format

    Returns:
        Dictionary formatted for HTTP response
    """
    return {
        'id': bank_account.id,
        'entity_id': bank_account.entity_id,
        'bank_id': bank_account.bank_id,
        'account_name': bank_account.account_name,
        'account_number': bank_account.account_number,
        'currency': bank_account.currency.value if bank_account.currency else None,
        'account_type': bank_account.account_type.value if bank_account.account_type else None,
        'status': bank_account.status.value if bank_account.status else None,
        'current_balance': bank_account.current_balance,
        'created_at': bank_account.created_at.isoformat() if bank_account.created_at else None,
        'updated_at': bank_account.updated_at.isoformat() if bank_account.updated_at else None
    }

def format_bank_account_balance(bank_account_balance: BankAccountBalance) -> Dict[str, Any]:
    """
    Format a BankAccountBalance object for HTTP response.

    Args:
        bank_account_balance: BankAccountBalance object to format

    Returns:
        Dictionary formatted for HTTP response
    """
    return {
        'id': bank_account_balance.id,
        'bank_account_id': bank_account_balance.bank_account_id,
        'currency': bank_account_balance.currency.value if bank_account_balance.currency else None,
        'date': bank_account_balance.date.isoformat() if bank_account_balance.date else None,
        'balance_statement': bank_account_balance.balance_statement,
        'balance_adjustment': bank_account_balance.balance_adjustment,
        'balance_final': bank_account_balance.balance_final,
        'created_at': bank_account_balance.created_at.isoformat() if bank_account_balance.created_at else None,
        'updated_at': bank_account_balance.updated_at.isoformat() if bank_account_balance.updated_at else None
    }


def format_bank_comprehensive(bank: Bank, include_bank_accounts: bool = False, include_bank_account_balances: bool = False) -> Dict[str, Any]:
    """
    Format a Bank object with comprehensive data.

    Args:
        bank: Bank object to format
        include_bank_accounts: Whether to include bank accounts
        include_bank_account_balances: Whether to include bank account balances (requires include_bank_accounts=True)

    Returns:
        Dictionary formatted for HTTP response
        
    Raises:
        ValueError: If include_bank_account_balances is True but include_bank_accounts is False
    """
    # Validate parameter dependencies
    if include_bank_account_balances and not include_bank_accounts:
        raise ValueError("include_bank_account_balances requires include_bank_accounts to be True")
    
    bank_data = format_bank(bank)

    # Add accounts if they exist
    if include_bank_accounts:
        bank_accounts_data = [format_bank_account_comprehensive(account, include_bank_account_balances) for account in bank.bank_accounts]
        bank_data['bank_accounts'] = bank_accounts_data
    else:
        bank_data['bank_accounts'] = []

    return bank_data


def format_bank_account_comprehensive(bank_account: BankAccount, include_bank_account_balances: bool = False) -> Dict[str, Any]:
    """
    Format a BankAccount object with comprehensive data.

    Args:
        bank_account: BankAccount object to format
        include_bank_account_balances: Whether to include bank account balances

    Returns:
        Dictionary formatted for HTTP response
    """
    bank_account_data = format_bank_account(bank_account)

    # Add bank account balances if they exist
    if include_bank_account_balances:
        bank_account_data['bank_account_balances'] = [format_bank_account_balance(balance) for balance in bank_account.bank_account_balances]
    else:
        bank_account_data['bank_account_balances'] = []

    return bank_account_data