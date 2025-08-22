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
                    "routing_number": bank.routing_number,
                    "is_active": bank.is_active,
                    "created_date": bank.created_date.isoformat() if bank.created_date else None,
                    "updated_date": bank.updated_date.isoformat() if bank.updated_date else None
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
            required_fields = ['name', 'routing_number']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Validate routing number format (9 digits)
            if not data['routing_number'].isdigit() or len(data['routing_number']) != 9:
                return jsonify({"error": "Routing number must be exactly 9 digits"}), 400
            
            # Check if bank already exists
            existing_bank = session.query(Bank).filter(Bank.routing_number == data['routing_number']).first()
            if existing_bank:
                return jsonify({"error": "Bank with this routing number already exists"}), 409
            
            # Create new bank
            new_bank = Bank(
                name=data['name'],
                routing_number=data['routing_number'],
                is_active=data.get('is_active', True)
            )
            
            session.add(new_bank)
            session.commit()
            
            # Return created bank data
            bank_data = {
                "id": new_bank.id,
                "name": new_bank.name,
                "routing_number": new_bank.routing_number,
                "is_active": new_bank.is_active,
                "created_date": new_bank.created_date.isoformat() if new_bank.created_date else None,
                "updated_date": new_bank.updated_date.isoformat() if new_bank.updated_date else None
            }
            
            return jsonify(bank_data), 201
            
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
            
            # Validate routing number format if provided
            if 'routing_number' in data and data['routing_number']:
                if not data['routing_number'].isdigit() or len(data['routing_number']) != 9:
                    return jsonify({"error": "Routing number must be exactly 9 digits"}), 400
                
                # Check if routing number already exists for another bank
                existing_bank = session.query(Bank).filter(
                    Bank.routing_number == data['routing_number'],
                    Bank.id != bank_id
                ).first()
                if existing_bank:
                    return jsonify({"error": "Bank with this routing number already exists"}), 409
            
            # Update bank fields
            if 'name' in data:
                bank.name = data['name']
            if 'routing_number' in data:
                bank.routing_number = data['routing_number']
            if 'is_active' in data:
                bank.is_active = data['is_active']
            
            session.commit()
            
            # Return updated bank data
            bank_data = {
                "id": bank.id,
                "name": bank.name,
                "routing_number": bank.routing_number,
                "is_active": bank.is_active,
                "created_date": bank.created_date.isoformat() if bank.created_date else None,
                "updated_date": bank.updated_date.isoformat() if bank.updated_date else None
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
                    "account_number": account.account_number,
                    "currency": account.currency,
                    "balance": float(account.balance) if account.balance else 0.0,
                    "is_active": account.is_active,
                    "bank": {
                        "id": account.bank.id,
                        "name": account.bank.name,
                        "routing_number": account.bank.routing_number
                    },
                    "entity_id": account.entity_id,
                    "created_date": account.created_date.isoformat() if account.created_date else None,
                    "updated_date": account.updated_date.isoformat() if account.updated_date else None
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
            required_fields = ['entity_id', 'bank_id', 'account_number', 'currency']
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
            
            # Check if account already exists at this bank
            existing_account = session.query(BankAccount).filter(
                BankAccount.account_number == data['account_number'],
                BankAccount.bank_id == data['bank_id']
            ).first()
            if existing_account:
                return jsonify({"error": "Bank account with this number already exists at this bank"}), 409
            
            # Create new bank account
            new_account = BankAccount(
                entity_id=data['entity_id'],
                bank_id=data['bank_id'],
                account_number=data['account_number'],
                currency=data['currency'],
                balance=data.get('balance', 0.0),
                is_active=data.get('is_active', True)
            )
            
            session.add(new_account)
            session.commit()
            
            # Return created account data
            account_data = {
                "id": new_account.id,
                "account_number": new_account.account_number,
                "currency": new_account.currency,
                "balance": float(new_account.balance) if new_account.balance else 0.0,
                "is_active": new_account.is_active,
                "bank": {
                    "id": bank.id,
                    "name": bank.name,
                    "routing_number": bank.routing_number
                },
                "entity_id": new_account.entity_id,
                "created_date": new_account.created_date.isoformat() if new_account.created_date else None,
                "updated_date": new_account.updated_date.isoformat() if new_account.updated_date else None
            }
            
            return jsonify(account_data), 201
            
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
            if 'account_number' in data:
                account.account_number = data['account_number']
            if 'currency' in data:
                account.currency = data['currency']
            if 'balance' in data:
                account.balance = data['balance']
            if 'is_active' in data:
                account.is_active = data['is_active']
            
            session.commit()
            
            # Return updated account data
            account_data = {
                "id": account.id,
                "account_number": account.account_number,
                "currency": account.currency,
                "balance": float(account.balance) if account.balance else 0.0,
                "is_active": account.is_active,
                "bank": {
                    "id": account.bank.id,
                    "name": account.bank.name,
                    "routing_number": account.bank.routing_number
                },
                "entity_id": account.entity_id,
                "created_date": account.created_date.isoformat() if account.created_date else None,
                "updated_date": account.updated_date.isoformat() if account.updated_date else None
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
            
            balance_data = {
                "account_id": account.id,
                "account_number": account.account_number,
                "currency": account.currency,
                "balance": float(account.balance) if account.balance else 0.0,
                "last_updated": account.updated_date.isoformat() if account.updated_date else None
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
                "message": "Transaction history not yet implemented",
                "transactions": []
            }
            
            return jsonify(transaction_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting bank account transactions: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
