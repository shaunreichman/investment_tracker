"""
Enhanced Banking API Controller.

This controller provides enterprise-grade REST API endpoints for banking operations,
with standardized response formats, comprehensive error handling, and performance optimization.
"""

from typing import List, Optional, Dict, Any, Tuple
from flask import request, jsonify, current_app
from sqlalchemy.orm import Session
from datetime import datetime
import time

from src.banking.models import Bank, BankAccount
from src.banking.services.bank_service import BankService
from src.banking.services.bank_account_service import BankAccountService
from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.repositories.bank_repository import BankRepository
from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.api.dto.banking import (
    BankingErrorCode,
    BankResponse,
    BankAccountResponse,
    BankAccountBalanceResponse,
    BankAccountTransactionsResponse,
    BankingListResponse,
    BankingSuccessResponse,
    BankingErrorResponse,
    create_success_response,
    create_error_response,
    create_list_response
)


class EnhancedBankingController:
    """Enhanced controller for banking operations with enterprise-grade features."""
    
    def __init__(self):
        """Initialize the enhanced banking controller."""
        self.bank_service = BankService()
        self.bank_account_service = BankAccountService()
        self.validation_service = BankingValidationService()
        self.bank_repository = BankRepository()
        self.bank_account_repository = BankAccountRepository()
    
    def _log_operation(self, operation: str, start_time: float, success: bool, **kwargs):
        """Log operation performance and results."""
        duration = (time.time() - start_time) * 1000
        status = "SUCCESS" if success else "FAILED"
        
        current_app.logger.info(
            f"Banking API {operation}: {status} in {duration:.2f}ms",
            extra={
                "operation": operation,
                "duration_ms": duration,
                "success": success,
                **kwargs
            }
        )
    
    def _handle_error(self, error: Exception, operation: str) -> Tuple[BankingErrorResponse, int]:
        """Handle errors and return standardized error responses."""
        if isinstance(error, ValueError):
            return create_error_response(
                BankingErrorCode.VALIDATION_ERROR,
                str(error)
            ), 400
        elif isinstance(error, RuntimeError):
            if "not found" in str(error).lower():
                return create_error_response(
                    BankingErrorCode.BANK_NOT_FOUND if "bank" in operation.lower() else BankingErrorCode.BANK_ACCOUNT_NOT_FOUND,
                    str(error)
                ), 404
            else:
                return create_error_response(
                    BankingErrorCode.VALIDATION_ERROR,
                    str(error)
                ), 400
        else:
            current_app.logger.error(f"Unexpected error in {operation}: {str(error)}")
            return create_error_response(
                BankingErrorCode.INTERNAL_ERROR,
                "Internal server error"
            ), 500

    def get_banks(self, session: Session, page: int = 1, page_size: int = 50) -> Tuple[BankingSuccessResponse, int]:
        """Get all banks with pagination and summary data."""
        start_time = time.time()
        
        try:
            # Get banks with pagination using repository
            banks, total_count = self.bank_repository.get_banks_paginated(
                session, page=page, page_size=page_size
            )
            
            # Convert to DTOs
            bank_responses = []
            for bank in banks:
                bank_response = BankResponse(
                    id=bank.id,
                    name=bank.name,
                    country=bank.country,
                    swift_bic=bank.swift_bic,
                    created_at=bank.created_at,
                    updated_at=bank.updated_at
                )
                bank_responses.append(bank_response)
            
            # Create paginated response
            list_response = create_list_response(
                data=bank_responses,
                total_count=total_count,
                page=page,
                page_size=page_size
            )
            
            response = create_success_response(
                data=list_response,
                message=f"Retrieved {len(bank_responses)} banks"
            )
            
            self._log_operation("get_banks", start_time, True, count=len(bank_responses))
            return response, 200
            
        except Exception as e:
            self._log_operation("get_banks", start_time, False, error=str(e))
            error_response, status_code = self._handle_error(e, "get_banks")
            return error_response, status_code

    def create_bank(self, session: Session, data: Dict[str, Any]) -> Tuple[BankingSuccessResponse, int]:
        """Create a new bank with enhanced validation and response."""
        start_time = time.time()
        
        try:
            # Validate required fields
            required_fields = ['name', 'country']
            for field in required_fields:
                if field not in data or not data[field]:
                    return create_error_response(
                        BankingErrorCode.MISSING_REQUIRED_FIELD,
                        f"Missing required field: {field}"
                    ), 400
            
            # Create new bank using service
            new_bank = self.bank_service.create_bank(
                name=data['name'],
                country=data['country'],
                swift_bic=data.get('swift_bic'),
                session=session
            )
            
            # Create response DTO
            bank_response = BankResponse(
                id=new_bank.id,
                name=new_bank.name,
                country=new_bank.country,
                swift_bic=new_bank.swift_bic,
                created_at=new_bank.created_at,
                updated_at=new_bank.updated_at
            )
            
            response = create_success_response(
                data=bank_response,
                message="Bank created successfully"
            )
            
            self._log_operation("create_bank", start_time, True, bank_id=new_bank.id)
            return response, 201
            
        except Exception as e:
            self._log_operation("create_bank", start_time, False, error=str(e))
            error_response, status_code = self._handle_error(e, "create_bank")
            return error_response, status_code

    def update_bank(self, bank_id: int, session: Session, data: Dict[str, Any]) -> Tuple[BankingSuccessResponse, int]:
        """Update a bank with enhanced validation and response."""
        start_time = time.time()
        
        try:
            # Update bank using service
            bank = self.bank_service.update_bank(bank_id, data, session)
            
            # Create response DTO
            bank_response = BankResponse(
                id=bank.id,
                name=bank.name,
                country=bank.country,
                swift_bic=bank.swift_bic,
                created_at=bank.created_at,
                updated_at=bank.updated_at
            )
            
            response = create_success_response(
                data=bank_response,
                message="Bank updated successfully"
            )
            
            self._log_operation("update_bank", start_time, True, bank_id=bank_id)
            return response, 200
            
        except Exception as e:
            self._log_operation("update_bank", start_time, False, bank_id=bank_id, error=str(e))
            error_response, status_code = self._handle_error(e, "update_bank")
            return error_response, status_code

    def delete_bank(self, bank_id: int, session: Session) -> Tuple[BankingSuccessResponse, int]:
        """Delete a bank with enhanced response."""
        start_time = time.time()
        
        try:
            # Delete bank using service
            self.bank_service.delete_bank(bank_id, session)
            
            response = create_success_response(
                message="Bank deleted successfully"
            )
            
            self._log_operation("delete_bank", start_time, True, bank_id=bank_id)
            return response, 200
            
        except Exception as e:
            self._log_operation("delete_bank", start_time, False, bank_id=bank_id, error=str(e))
            error_response, status_code = self._handle_error(e, "delete_bank")
            return error_response, status_code

    def get_bank_accounts(self, session: Session, page: int = 1, page_size: int = 50) -> Tuple[BankingSuccessResponse, int]:
        """Get all bank accounts with pagination and summary data."""
        start_time = time.time()
        
        try:
            # Get bank accounts with pagination using repository
            accounts, total_count = self.bank_account_repository.get_bank_accounts_paginated(
                session, page=page, page_size=page_size
            )
            
            # Convert to DTOs
            account_responses = []
            for account in accounts:
                bank_response = BankResponse(
                    id=account.bank.id,
                    name=account.bank.name,
                    country=account.bank.country,
                    swift_bic=account.bank.swift_bic,
                    created_at=account.bank.created_at,
                    updated_at=account.bank.updated_at
                )
                
                account_response = BankAccountResponse(
                    id=account.id,
                    account_name=account.account_name,
                    account_number=account.account_number,
                    currency=account.currency,
                    is_active=account.is_active,
                    entity_id=account.entity_id,
                    bank=bank_response,
                    created_at=account.created_at,
                    updated_at=account.updated_at
                )
                account_responses.append(account_response)
            
            # Create paginated response
            list_response = create_list_response(
                data=account_responses,
                total_count=total_count,
                page=page,
                page_size=page_size
            )
            
            response = create_success_response(
                data=list_response,
                message=f"Retrieved {len(account_responses)} bank accounts"
            )
            
            self._log_operation("get_bank_accounts", start_time, True, count=len(account_responses))
            return response, 200
            
        except Exception as e:
            self._log_operation("get_bank_accounts", start_time, False, error=str(e))
            error_response, status_code = self._handle_error(e, "get_bank_accounts")
            return error_response, status_code

    def create_bank_account(self, session: Session, data: Dict[str, Any]) -> Tuple[BankingSuccessResponse, int]:
        """Create a new bank account with enhanced validation and response."""
        start_time = time.time()
        
        try:
            # Validate required fields
            required_fields = ['entity_id', 'bank_id', 'account_name', 'account_number', 'currency']
            for field in required_fields:
                if field not in data or not data[field]:
                    return create_error_response(
                        BankingErrorCode.MISSING_REQUIRED_FIELD,
                        f"Missing required field: {field}"
                    ), 400
            
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
            
            # Create response DTOs
            bank_response = BankResponse(
                id=bank.id,
                name=bank.name,
                country=bank.country,
                swift_bic=bank.swift_bic,
                created_at=bank.created_at,
                updated_at=bank.updated_at
            )
            
            account_response = BankAccountResponse(
                id=new_account.id,
                account_name=new_account.account_name,
                account_number=new_account.account_number,
                currency=new_account.currency,
                is_active=new_account.is_active,
                entity_id=new_account.entity_id,
                bank=bank_response,
                created_at=new_account.created_at,
                updated_at=new_account.updated_at
            )
            
            response = create_success_response(
                data=account_response,
                message="Bank account created successfully"
            )
            
            self._log_operation("create_bank_account", start_time, True, account_id=new_account.id)
            return response, 201
            
        except Exception as e:
            self._log_operation("create_bank_account", start_time, False, error=str(e))
            error_response, status_code = self._handle_error(e, "create_bank_account")
            return error_response, status_code

    def update_bank_account(self, account_id: int, session: Session, data: Dict[str, Any]) -> Tuple[BankingSuccessResponse, int]:
        """Update a bank account with enhanced validation and response."""
        start_time = time.time()
        
        try:
            # Update account using service
            account = self.bank_account_service.update_bank_account(account_id, data, session)
            
            # Create response DTOs
            bank_response = BankResponse(
                id=account.bank.id,
                name=account.bank.name,
                country=account.bank.country,
                swift_bic=account.bank.swift_bic,
                created_at=account.bank.created_at,
                updated_at=account.bank.updated_at
            )
            
            account_response = BankAccountResponse(
                id=account.id,
                account_name=account.account_name,
                account_number=account.account_number,
                currency=account.currency,
                is_active=account.is_active,
                entity_id=account.entity_id,
                bank=bank_response,
                created_at=account.created_at,
                updated_at=account.updated_at
            )
            
            response = create_success_response(
                data=account_response,
                message="Bank account updated successfully"
            )
            
            self._log_operation("update_bank_account", start_time, True, account_id=account_id)
            return response, 200
            
        except Exception as e:
            self._log_operation("update_bank_account", start_time, False, account_id=account_id, error=str(e))
            error_response, status_code = self._handle_error(e, "update_bank_account")
            return error_response, status_code

    def delete_bank_account(self, account_id: int, session: Session) -> Tuple[BankingSuccessResponse, int]:
        """Delete a bank account with enhanced response."""
        start_time = time.time()
        
        try:
            # Delete account using service
            self.bank_account_service.delete_bank_account(account_id, session)
            
            response = create_success_response(
                message="Bank account deleted successfully"
            )
            
            self._log_operation("delete_bank_account", start_time, True, account_id=account_id)
            return response, 200
            
        except Exception as e:
            self._log_operation("delete_bank_account", start_time, False, account_id=account_id, error=str(e))
            error_response, status_code = self._handle_error(e, "delete_bank_account")
            return error_response, status_code

    def get_bank_account_balance(self, account_id: int, session: Session) -> Tuple[BankingSuccessResponse, int]:
        """Get current balance for a bank account with enhanced response."""
        start_time = time.time()
        
        try:
            # Check if account exists using service
            account = self.bank_account_service.get_bank_account_by_id(account_id, session)
            if not account:
                return create_error_response(
                    BankingErrorCode.BANK_ACCOUNT_NOT_FOUND,
                    "Bank account not found"
                ), 404
            
            # Create response DTO
            balance_response = BankAccountBalanceResponse(
                account_id=account.id,
                account_number=account.account_number,
                currency=account.currency,
                balance=None,  # Balance tracking not yet implemented
                last_updated=datetime.utcnow(),
                message="Balance tracking not yet implemented - transaction system required"
            )
            
            response = create_success_response(
                data=balance_response,
                message="Account balance information retrieved"
            )
            
            self._log_operation("get_bank_account_balance", start_time, True, account_id=account_id)
            return response, 200
            
        except Exception as e:
            self._log_operation("get_bank_account_balance", start_time, False, account_id=account_id, error=str(e))
            error_response, status_code = self._handle_error(e, "get_bank_account_balance")
            return error_response, status_code

    def get_bank_account_transactions(self, account_id: int, session: Session, page: int = 1, page_size: int = 50) -> Tuple[BankingSuccessResponse, int]:
        """Get transaction history for a bank account with enhanced response."""
        start_time = time.time()
        
        try:
            # Check if account exists using service
            account = self.bank_account_service.get_bank_account_by_id(account_id, session)
            if not account:
                return create_error_response(
                    BankingErrorCode.BANK_ACCOUNT_NOT_FOUND,
                    "Bank account not found"
                ), 404
            
            # Create response DTO
            transactions_response = BankAccountTransactionsResponse(
                account_id=account.id,
                account_number=account.account_number,
                currency=account.currency,
                transactions=[],  # Transaction history not yet implemented
                total_count=0,
                page=page,
                page_size=page_size
            )
            
            response = create_success_response(
                data=transactions_response,
                message="Transaction history not yet implemented - transaction system required"
            )
            
            self._log_operation("get_bank_account_transactions", start_time, True, account_id=account_id)
            return response, 200
            
        except Exception as e:
            self._log_operation("get_bank_account_transactions", start_time, False, account_id=account_id, error=str(e))
            error_response, status_code = self._handle_error(e, "get_bank_account_transactions")
            return error_response, status_code
