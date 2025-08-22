"""
Banking API Controller.

This controller handles HTTP requests for banking operations,
providing RESTful endpoints for bank and bank account management.

Key responsibilities:
- Bank CRUD endpoints
- Bank account CRUD endpoints
- Banking validation and error handling
- Input sanitization and type validation
"""

from typing import List, Optional, Dict, Any
from flask import request, jsonify, current_app
from sqlalchemy.orm import Session

from src.banking.models import Bank, BankAccount
from src.banking.services.bank_service import BankService
from src.banking.services.bank_account_service import BankAccountService
from src.banking.services.banking_validation_service import BankingValidationService


class BankingController:
    """
    Controller for banking operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for banking operations. It delegates business logic to the domain
    models and handles request/response formatting.
    
    Attributes:
        None - Direct domain model usage for simplicity
    """
    
    def __init__(self):
        """Initialize the banking controller."""
        self.bank_service = BankService()
        self.bank_account_service = BankAccountService()
        self.validation_service = BankingValidationService()
    
    def get_banks(self, session: Session) -> tuple:
        """
        Get all banks with summary data.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get all banks using service
            banks = self.bank_service.get_all_banks(session)
            
            # Format response data
            banks_data = []
            for bank in banks:
                bank_data = {
                    "id": bank.id,
                    "name": bank.name,
                    "country": bank.country,
                    "swift_bic": bank.swift_bic
                }
                banks_data.append(bank_data)
            
            return jsonify(banks_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting banks: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def create_bank_with_data(self, session: Session, data: Dict[str, Any]) -> tuple:
        """
        Create a new bank with pre-validated data.
        
        Args:
            session: Database session
            data: Pre-validated bank data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Validate required fields
            required_fields = ['name', 'country']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Create new bank using service
            new_bank = self.bank_service.create_bank(
                name=data['name'],
                country=data['country'],
                swift_bic=data.get('swift_bic'),
                session=session
            )
            
            # Return created bank data
            bank_data = {
                "id": new_bank.id,
                "name": new_bank.name,
                "country": new_bank.country,
                "swift_bic": new_bank.swift_bic
            }
            
            return jsonify(bank_data), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            session.rollback()
            current_app.logger.error(f"Error creating bank: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def update_bank_with_data(self, bank_id: int, session: Session, data: Dict[str, Any]) -> tuple:
        """
        Update a bank with pre-validated data.
        
        Args:
            bank_id: ID of the bank to update
            session: Database session
            data: Pre-validated bank data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Update bank using service
            bank = self.bank_service.update_bank(bank_id, data, session)
            
            # Return updated bank data
            bank_data = {
                "id": bank.id,
                "name": bank.name,
                "country": bank.country,
                "swift_bic": bank.swift_bic
            }
            
            return jsonify(bank_data), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except RuntimeError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            session.rollback()
            current_app.logger.error(f"Error updating bank: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def delete_bank(self, bank_id: int, session: Session) -> tuple:
        """
        Delete a bank.
        
        Args:
            bank_id: ID of the bank to delete
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Delete bank using service
            self.bank_service.delete_bank(bank_id, session)
            
            return jsonify({"message": "Bank deleted successfully"}), 200
            
        except RuntimeError as e:
            if "not found" in str(e).lower():
                return jsonify({"error": "Bank not found"}), 404
            else:
                return jsonify({"error": str(e)}), 400
        except Exception as e:
            session.rollback()
            current_app.logger.error(f"Error deleting bank: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_bank_accounts(self, session: Session) -> tuple:
        """
        Get all bank accounts with summary data.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get all bank accounts using service
            accounts = self.bank_account_service.get_all_bank_accounts(session)
            
            # Format response data
            accounts_data = []
            for account in accounts:
                account_data = {
                    "id": account.id,
                    "account_name": account.account_name,
                    "account_number": account.account_number,
                    "currency": account.currency,
                    "is_active": account.is_active,
                    "bank": {
                        "id": account.bank.id,
                        "name": account.bank.name,
                        "country": account.bank.country,
                        "swift_bic": account.bank.swift_bic
                    },
                    "entity_id": account.entity_id
                }
                accounts_data.append(account_data)
            
            return jsonify(accounts_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting bank accounts: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def create_bank_account_with_data(self, session: Session, data: Dict[str, Any]) -> tuple:
        """
        Create a new bank account with pre-validated data.
        
        Args:
            session: Database session
            data: Pre-validated bank account data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Validate required fields
            required_fields = ['entity_id', 'bank_id', 'account_name', 'account_number', 'currency']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Create new bank account using service
            new_account = self.bank_account_service.create_bank_account(
                entity_id=data['entity_id'],
                bank_id=data['bank_id'],
                account_name=data['account_name'],
                account_number=data['account_number'],
                currency=data['currency'],
                is_active=data.get('is_active', True),
                session=session
            )
            
            # Get bank information for response
            bank = self.bank_service.get_bank_by_id(data['bank_id'], session)
            
            # Return created account data
            account_data = {
                "id": new_account.id,
                "account_name": new_account.account_name,
                "account_number": new_account.account_number,
                "currency": new_account.currency,
                "is_active": new_account.is_active,
                "bank": {
                    "id": bank.id,
                    "name": bank.name,
                    "country": bank.country,
                    "swift_bic": bank.swift_bic
                },
                "entity_id": new_account.entity_id
            }
            
            return jsonify(account_data), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            session.rollback()
            current_app.logger.error(f"Error creating bank account: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def update_bank_account_with_data(self, account_id: int, session: Session, data: Dict[str, Any]) -> tuple:
        """
        Update a bank account with pre-validated data.
        
        Args:
            account_id: ID of the account to update
            session: Database session
            data: Pre-validated bank account data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Update account using service
            account = self.bank_account_service.update_bank_account(account_id, data, session)
            
            # Return updated account data
            account_data = {
                "id": account.id,
                "account_name": account.account_name,
                "account_number": account.account_number,
                "currency": account.currency,
                "is_active": account.is_active,
                "bank": {
                    "id": account.bank.id,
                    "name": account.bank.name,
                    "country": account.bank.country,
                    "swift_bic": account.bank.swift_bic
                },
                "entity_id": account.entity_id
            }
            
            return jsonify(account_data), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except RuntimeError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            session.rollback()
            current_app.logger.error(f"Error updating bank account: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def delete_bank_account(self, account_id: int, session: Session) -> tuple:
        """
        Delete a bank account.
        
        Args:
            account_id: ID of the account to delete
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Delete account using service
            self.bank_account_service.delete_bank_account(account_id, session)
            
            return jsonify({"message": "Bank account deleted successfully"}), 200
            
        except RuntimeError as e:
            if "not found" in str(e).lower():
                return jsonify({"error": "Bank account not found"}), 404
            else:
                return jsonify({"error": str(e)}), 400
        except Exception as e:
            session.rollback()
            current_app.logger.error(f"Error deleting bank account: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_bank_account_balance(self, account_id: int, session: Session) -> tuple:
        """
        Get current balance for a bank account.
        
        Args:
            account_id: ID of the account
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Check if account exists using service
            account = self.bank_account_service.get_bank_account_by_id(account_id, session)
            if not account:
                return jsonify({"error": "Bank account not found"}), 404
            
            # For now, return basic account info - balance tracking would be implemented
            # when the transaction system is built
            balance_data = {
                "account_id": account.id,
                "account_number": account.account_number,
                "currency": account.currency,
                "message": "Balance tracking not yet implemented - transaction system required",
                "balance": None
            }
            
            return jsonify(balance_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting bank account balance: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def get_bank_account_transactions(self, account_id: int, session: Session) -> tuple:
        """
        Get transaction history for a bank account.
        
        Args:
            account_id: ID of the account
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Check if account exists using service
            account = self.bank_account_service.get_bank_account_by_id(account_id, session)
            if not account:
                return jsonify({"error": "Bank account not found"}), 404
            
            # For now, return basic account info - transaction history would be implemented
            # when the transaction system is built
            transaction_data = {
                "account_id": account.id,
                "account_number": account.account_number,
                "currency": account.currency,
                "message": "Transaction history not yet implemented - transaction system required",
                "transactions": []
            }
            
            return jsonify(transaction_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting bank account transactions: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
