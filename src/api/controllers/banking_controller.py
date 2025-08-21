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
    
    def create_bank(self, session: Session) -> tuple:
        """
        Create a new bank.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
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
            
            # Create bank
            bank = Bank(
                name=data['name'].strip(),
                routing_number=data['routing_number'],
                is_active=data.get('is_active', True)
            )
            
            session.add(bank)
            session.commit()
            
            # Format response data
            response_data = {
                "id": bank.id,
                "name": bank.name,
                "routing_number": bank.routing_number,
                "is_active": bank.is_active,
                "created_date": bank.created_date.isoformat() if bank.created_date else None,
                "updated_date": bank.updated_date.isoformat() if bank.updated_date else None,
                "message": "Bank created successfully"
            }
            
            return jsonify(response_data), 201
            
        except Exception as e:
            current_app.logger.error(f"Error creating bank: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({"error": "Internal server error"}), 500
    
    def update_bank(self, bank_id: int, session: Session) -> tuple:
        """
        Update a bank.
        
        Args:
            bank_id: ID of the bank to update
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Get the bank
            bank = session.query(Bank).filter(Bank.id == bank_id).first()
            if not bank:
                return jsonify({"error": "Bank not found"}), 404
            
            # Update allowed fields
            if 'name' in data:
                bank.name = data['name'].strip()
            if 'routing_number' in data:
                # Validate routing number format
                if not data['routing_number'].isdigit() or len(data['routing_number']) != 9:
                    return jsonify({"error": "Routing number must be exactly 9 digits"}), 400
                
                # Check if routing number already exists on another bank
                existing_bank = session.query(Bank).filter(
                    Bank.routing_number == data['routing_number'],
                    Bank.id != bank_id
                ).first()
                if existing_bank:
                    return jsonify({"error": "Bank with this routing number already exists"}), 409
                
                bank.routing_number = data['routing_number']
            if 'is_active' in data:
                bank.is_active = bool(data['is_active'])
            
            session.commit()
            
            # Format response data
            response_data = {
                "id": bank.id,
                "name": bank.name,
                "routing_number": bank.routing_number,
                "is_active": bank.is_active,
                "created_date": bank.created_date.isoformat() if bank.created_date else None,
                "updated_date": bank.updated_date.isoformat() if bank.updated_date else None,
                "message": "Bank updated successfully"
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error updating bank {bank_id}: {str(e)}")
            if 'session' in locals():
                session.rollback()
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
            # Get the bank
            bank = session.query(Bank).filter(Bank.id == bank_id).first()
            if not bank:
                return jsonify({"error": "Bank not found"}), 404
            
            # Check if bank has accounts
            accounts = session.query(BankAccount).filter(BankAccount.bank_id == bank_id).count()
            if accounts > 0:
                return jsonify({"error": f"Cannot delete bank with {accounts} associated accounts"}), 400
            
            session.delete(bank)
            session.commit()
            
            return jsonify({"message": "Bank deleted successfully"}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error deleting bank {bank_id}: {str(e)}")
            if 'session' in locals():
                session.rollback()
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
            # Get all bank accounts with bank and entity info
            accounts = session.query(BankAccount).join(Bank).join(Entity).all()
            
            # Format response data
            accounts_data = []
            for account in accounts:
                account_data = {
                    "id": account.id,
                    "entity_id": account.entity_id,
                    "entity_name": account.entity.name if account.entity else None,
                    "bank_id": account.bank_id,
                    "bank_name": account.bank.name if account.bank else None,
                    "account_name": account.account_name,
                    "account_number": account.account_number,
                    "currency": account.currency,
                    "is_active": account.is_active,
                    "created_date": account.created_date.isoformat() if account.created_date else None,
                    "updated_date": account.updated_date.isoformat() if account.updated_date else None
                }
                accounts_data.append(account_data)
            
            return jsonify(accounts_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting bank accounts: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def create_bank_account(self, session: Session) -> tuple:
        """
        Create a new bank account.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate required fields
            required_fields = ['entity_id', 'bank_id', 'account_name', 'account_number']
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
            if 'currency' in data and len(data['currency']) != 3:
                return jsonify({"error": "Currency must be a 3-letter ISO code"}), 400
            
            # Check if account already exists
            existing_account = session.query(BankAccount).filter(
                BankAccount.bank_id == data['bank_id'],
                BankAccount.account_number == data['account_number']
            ).first()
            if existing_account:
                return jsonify({"error": "Bank account with this number already exists at this bank"}), 409
            
            # Create bank account
            account = BankAccount(
                entity_id=data['entity_id'],
                bank_id=data['bank_id'],
                account_name=data['account_name'].strip(),
                account_number=data['account_number'].strip(),
                currency=data.get('currency', 'USD').upper(),
                is_active=data.get('is_active', True)
            )
            
            session.add(account)
            session.commit()
            
            # Format response data
            response_data = {
                "id": account.id,
                "entity_id": account.entity_id,
                "entity_name": account.entity.name if account.entity else None,
                "bank_id": account.bank_id,
                "bank_name": account.bank.name if account.bank else None,
                "account_name": account.account_name,
                "account_number": account.account_number,
                "currency": account.currency,
                "is_active": account.is_active,
                "message": "Bank account created successfully"
            }
            
            return jsonify(response_data), 201
            
        except Exception as e:
            current_app.logger.error(f"Error creating bank account: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({"error": "Internal server error"}), 500
    
    def update_bank_account(self, account_id: int, session: Session) -> tuple:
        """
        Update a bank account.
        
        Args:
            account_id: ID of the account to update
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Get the account
            account = session.query(BankAccount).filter(BankAccount.id == account_id).first()
            if not account:
                return jsonify({"error": "Bank account not found"}), 404
            
            # Update allowed fields
            if 'account_name' in data:
                account.account_name = data['account_name'].strip()
            if 'is_active' in data:
                account.is_active = bool(data['is_active'])
            if 'currency' in data:
                # Validate currency format
                if len(data['currency']) != 3:
                    return jsonify({"error": "Currency must be a 3-letter ISO code"}), 400
                account.currency = data['currency'].upper()
            
            session.commit()
            
            # Format response data
            response_data = {
                "id": account.id,
                "entity_id": account.entity_id,
                "entity_name": account.entity.name if account.entity else None,
                "bank_id": account.bank_id,
                "bank_name": account.bank.name if account.bank else None,
                "account_name": account.account_name,
                "account_number": account.account_number,
                "currency": account.currency,
                "is_active": account.is_active,
                "message": "Bank account updated successfully"
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error updating bank account {account_id}: {str(e)}")
            if 'session' in locals():
                session.rollback()
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
            # Get the account
            account = session.query(BankAccount).filter(BankAccount.id == account_id).first()
            if not account:
                return jsonify({"error": "Bank account not found"}), 404
            
            session.delete(account)
            session.commit()
            
            return jsonify({"message": "Bank account deleted successfully"}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error deleting bank account {account_id}: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({"error": "Internal server error"}), 500
