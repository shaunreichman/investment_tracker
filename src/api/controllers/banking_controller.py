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
        pass
    
    def get_banks(self, session: Session) -> tuple:
        """
        Get all banks with summary data.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get all banks
            banks = session.query(Bank).all()
            
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
            
            # Validate country format (2-letter ISO code)
            if not data['country'].isalpha() or len(data['country']) != 2:
                return jsonify({"error": "Country must be a 2-letter ISO code"}), 400
            
            # Check if bank already exists with same name and country
            existing_bank = session.query(Bank).filter(
                Bank.name == data['name'],
                Bank.country == data['country'].upper()
            ).first()
            if existing_bank:
                return jsonify({"error": "Bank with this name already exists in this country"}), 409
            
            # Create new bank using domain method
            new_bank = Bank.create(
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
            # Check if bank exists
            bank = session.query(Bank).filter(Bank.id == bank_id).first()
            if not bank:
                return jsonify({"error": "Bank not found"}), 404
            
            # Validate country format if provided
            if 'country' in data and data['country']:
                if not data['country'].isalpha() or len(data['country']) != 2:
                    return jsonify({"error": "Country must be a 2-letter ISO code"}), 400
                
                # Check if bank with same name already exists in this country
                existing_bank = session.query(Bank).filter(
                    Bank.name == data['name'] if 'name' in data else bank.name,
                    Bank.country == data['country'].upper(),
                    Bank.id != bank_id
                ).first()
                if existing_bank:
                    return jsonify({"error": "Bank with this name already exists in this country"}), 409
            
            # Update bank fields
            if 'name' in data:
                bank.name = data['name'].strip()
            if 'country' in data:
                bank.country = data['country'].upper()
            if 'swift_bic' in data:
                bank.swift_bic = data['swift_bic']
            
            session.commit()
            
            # Return updated bank data
            bank_data = {
                "id": bank.id,
                "name": bank.name,
                "country": bank.country,
                "swift_bic": bank.swift_bic
            }
            
            return jsonify(bank_data), 200
            
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
            # Check if bank exists
            bank = session.query(Bank).filter(Bank.id == bank_id).first()
            if not bank:
                return jsonify({"error": "Bank not found"}), 404
            
            # Check if bank has associated accounts
            accounts = session.query(BankAccount).filter(BankAccount.bank_id == bank_id).count()
            if accounts > 0:
                return jsonify({"error": f"Cannot delete bank with {accounts} associated accounts"}), 400
            
            # Delete bank
            session.delete(bank)
            session.commit()
            
            return jsonify({"message": "Bank deleted successfully"}), 200
            
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
            # Get all bank accounts with bank information
            accounts = session.query(BankAccount).join(Bank).all()
            
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
            
            # Validate entity exists
            from src.entity.models import Entity
            entity = session.query(Entity).filter(Entity.id == data['entity_id']).first()
            if not entity:
                return jsonify({"error": "Entity not found"}), 404
            
            # Validate bank exists
            bank = session.query(Bank).filter(Bank.id == data['bank_id']).first()
            if not bank:
                return jsonify({"error": "Bank not found"}), 404
            
            # Validate currency format
            if not data['currency'].isalpha() or len(data['currency']) != 3:
                return jsonify({"error": "Currency must be a 3-letter ISO code"}), 400
            
            # Create new bank account using domain method
            new_account = BankAccount.create(
                entity_id=data['entity_id'],
                bank_id=data['bank_id'],
                account_name=data['account_name'],
                account_number=data['account_number'],
                currency=data['currency'],
                is_active=data.get('is_active', True),
                session=session
            )
            
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
            # Check if account exists
            account = session.query(BankAccount).filter(BankAccount.id == account_id).first()
            if not account:
                return jsonify({"error": "Bank account not found"}), 404
            
            # Validate currency format if provided
            if 'currency' in data and data['currency']:
                if not data['currency'].isalpha() or len(data['currency']) != 3:
                    return jsonify({"error": "Currency must be a 3-letter ISO code"}), 400
            
            # Update account fields
            if 'account_name' in data:
                account.account_name = data['account_name'].strip()
            if 'account_number' in data:
                account.account_number = data['account_number'].strip()
            if 'currency' in data:
                account.currency = data['currency'].upper()
            if 'is_active' in data:
                account.is_active = data['is_active']
            
            session.commit()
            
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
            # Check if account exists
            account = session.query(BankAccount).filter(BankAccount.id == account_id).first()
            if not account:
                return jsonify({"error": "Bank account not found"}), 404
            
            # Delete account
            session.delete(account)
            session.commit()
            
            return jsonify({"message": "Bank account deleted successfully"}), 200
            
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
            # Check if account exists
            account = session.query(BankAccount).filter(BankAccount.id == account_id).first()
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
            # Check if account exists
            account = session.query(BankAccount).filter(BankAccount.id == account_id).first()
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
