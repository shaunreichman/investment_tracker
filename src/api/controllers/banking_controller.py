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
from src.api.dto.api_response import ApiResponse
from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.dto.response_codes import ApiResponseCode
from src.api.controllers.formatters.banking_formatter import format_bank, format_bank_with_accounts
from src.banking.models import Bank, BankAccount

from src.banking.services.bank_service import BankService
from src.banking.services.bank_account_service import BankAccountService
from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.repositories.bank_repository import BankRepository
from src.banking.repositories.bank_account_repository import BankAccountRepository


class BankingController:
    """Enterprise-grade controller for banking operations with comprehensive features."""
    
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

    def get_bank(self, bank_id: int):
        """
        Get a bank by ID.
        
        Args:
            bank_id: ID of the bank to retrieve
            
        Returns:
            ControllerResponseDTO: DTO containing bank data and status
        """
        try:
            # Get database session
            session = self._get_session()
            
            # Get the bank (now returns domain object)
            bank = self.bank_service.get_bank(bank_id, session)
            
            if not bank:
                return ControllerResponseDTO(error="Bank not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
            
            # Format the response using formatter
            formatted_bank = format_bank(bank)

            return ControllerResponseDTO(data=formatted_bank, response_code=ApiResponseCode.SUCCESS)
            
        except Exception as e:
            current_app.logger.error(f"Error getting bank {bank_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
        finally:
            if 'session' in locals():
                session.close()       



    def create_bank(self, data: Dict[str, Any]):
        """Create a new bank with enhanced validation and response."""
        start_time = time.time()
        session = self._get_session()
        
        try:
            # Validate required fields
            required_fields = ['name', 'country']
            for field in required_fields:
                if field not in data or not data[field]:
                    return ControllerResponseDTO(
                        error=f"Missing required field: {field}",
                        response_code=ApiResponseCode.BAD_REQUEST
                    )
            
            # Create new bank using service
            new_bank = self.bank_service.create_bank(
                name=data['name'],
                country=data['country'],
                swift_bic=data.get('swift_bic'),
                session=session
            )
            
            # Commit transaction
            session.commit()
            
            # Format the response using formatter
            formatted_bank = format_bank(new_bank)
            
            self._log_operation("create_bank", start_time, True, bank_id=new_bank.id)
            return ControllerResponseDTO(data=formatted_bank, response_code=ApiResponseCode.CREATED)
            
        except Exception as e:
            self._log_operation("create_bank", start_time, False, error=str(e))
            current_app.logger.error(f"Error creating bank: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def update_bank(self, bank_id: int, data: Dict[str, Any]):
        """Update a bank with enhanced validation and response."""
        start_time = time.time()
        session = self._get_session()
        
        try:
            # Update bank using service
            bank = self.bank_service.update_bank(bank_id, data, session)
            
            if not bank:
                return ControllerResponseDTO(error="Bank not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
            
            # Commit transaction
            session.commit()
            
            # Format the response using formatter
            formatted_bank = format_bank(bank)
            
            self._log_operation("update_bank", start_time, True, bank_id=bank_id)
            return ControllerResponseDTO(data=formatted_bank, response_code=ApiResponseCode.SUCCESS)
            
        except Exception as e:
            self._log_operation("update_bank", start_time, False, bank_id=bank_id, error=str(e))
            current_app.logger.error(f"Error updating bank {bank_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def delete_bank(self, bank_id: int):
        """Delete a bank with enhanced response."""
        start_time = time.time()
        session = self._get_session()
        
        try:
            # Delete bank using service
            success = self.bank_service.delete_bank(bank_id, session)
            
            if not success:
                return ControllerResponseDTO(error="Bank not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
            
            # Commit transaction
            session.commit()
            
            self._log_operation("delete_bank", start_time, True, bank_id=bank_id)
            return ControllerResponseDTO(response_code=ApiResponseCode.SUCCESS)
            
        except Exception as e:
            self._log_operation("delete_bank", start_time, False, bank_id=bank_id, error=str(e))
            current_app.logger.error(f"Error deleting bank {bank_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def create_bank_account(self, data: Dict[str, Any]):
        """Create a new bank account with enhanced validation and response."""
        start_time = time.time()
        session = self._get_session()
        
        try:
            # Validate required fields
            required_fields = ['entity_id', 'bank_id', 'account_name', 'account_number', 'currency']
            for field in required_fields:
                if field not in data or not data[field]:
                    return ControllerResponseDTO(
                        error=f"Missing required field: {field}",
                        response_code=ApiResponseCode.BAD_REQUEST
                    )
            
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
            
            # Commit transaction
            session.commit()
            
            # Format the response using formatter
            formatted_account = format_bank_with_accounts(new_account.bank, [new_account])
            
            self._log_operation("create_bank_account", start_time, True, account_id=new_account.id)
            return ControllerResponseDTO(data=formatted_account['accounts'][0], response_code=ApiResponseCode.CREATED)
            
        except Exception as e:
            self._log_operation("create_bank_account", start_time, False, error=str(e))
            current_app.logger.error(f"Error creating bank account: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def update_bank_account(self, account_id: int, data: Dict[str, Any]):
        """Update a bank account with enhanced validation and response."""
        start_time = time.time()
        session = self._get_session()
        
        try:
            # Update account using service
            account = self.bank_account_service.update_bank_account(account_id, data, session)
            
            if not account:
                return ControllerResponseDTO(error="Bank account not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
            
            # Commit transaction
            session.commit()
            
            # Format the response using formatter
            formatted_account = format_bank_with_accounts(account.bank, [account])
            
            self._log_operation("update_bank_account", start_time, True, account_id=account_id)
            return ControllerResponseDTO(data=formatted_account['accounts'][0], response_code=ApiResponseCode.SUCCESS)
            
        except Exception as e:
            self._log_operation("update_bank_account", start_time, False, account_id=account_id, error=str(e))
            current_app.logger.error(f"Error updating bank account {account_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def delete_bank_account(self, account_id: int):
        """Delete a bank account with enhanced response."""
        start_time = time.time()
        session = self._get_session()
        
        try:
            # Delete account using service
            success = self.bank_account_service.delete_bank_account(account_id, session)
            
            if not success:
                return ControllerResponseDTO(error="Bank account not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
            
            # Commit transaction
            session.commit()
            
            self._log_operation("delete_bank_account", start_time, True, account_id=account_id)
            return ControllerResponseDTO(response_code=ApiResponseCode.SUCCESS)
            
        except Exception as e:
            self._log_operation("delete_bank_account", start_time, False, account_id=account_id, error=str(e))
            current_app.logger.error(f"Error deleting bank account {account_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
    
    def _get_session(self) -> Session:
        """
        Get the current database session from middleware.
        
        Returns:
            Database session from Flask's g context
        """
        from src.api.middleware.database_session import get_current_session
        return get_current_session()
