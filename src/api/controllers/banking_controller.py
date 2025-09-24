"""
Enhanced Banking API Controller.

This controller provides enterprise-grade REST API endpoints for banking operations,
with standardized response formats, comprehensive error handling, and performance optimization.
"""

from flask import request, current_app
from sqlalchemy.orm import Session
from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.dto.response_codes import ApiResponseCode
from src.api.controllers.formatters.banking_formatter import format_bank, format_bank_account, format_bank_comprehensive

from src.banking.services.bank_service import BankService
from src.banking.services.bank_account_service import BankAccountService

class BankingController:
    """Enterprise-grade controller for banking operations with comprehensive features."""
    
    def __init__(self):
        """Initialize the enhanced banking controller."""
        self.bank_service = BankService()
        self.bank_account_service = BankAccountService()
    
    
    ###############################################################################
    # BANK ENDPOINTS
    ###############################################################################

    ###############################################
    # Get bank
    ###############################################

    def get_banks(self, include_bank_accounts: bool = False) -> ControllerResponseDTO:
        """
        Get all banks.
        
        Returns:
            ControllerResponseDTO: DTO containing banks data and status
        """
        try:
            session = self._get_session()
            try:
                banks = self.bank_service.get_banks(session)
                if banks is None:
                    return ControllerResponseDTO(error="Banks not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                if include_bank_accounts:
                    for bank in banks:
                        bank.accounts = self.bank_account_service.get_bank_accounts(bank.id, session)

                formatted_banks = [format_bank_comprehensive(bank, include_bank_accounts=include_bank_accounts) for bank in banks]
                return ControllerResponseDTO(data=formatted_banks, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting banks: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting banks: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()
        except Exception as e:
            current_app.logger.error(f"Error getting banks: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_bank_by_id(self, bank_id: int, include_bank_accounts: bool = False) -> ControllerResponseDTO:
        """
        Get a bank by ID.
        
        Args:
            bank_id: ID of the bank to retrieve
            include_bank_accounts: Whether to include bank accounts

        Returns:
            ControllerResponseDTO: DTO containing bank data and status
        """
        try:
            session = self._get_session()
            
            try:
                bank = self.bank_service.get_bank_by_id(bank_id, session)
                if not bank:
                    return ControllerResponseDTO(error="Bank not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                if include_bank_accounts:
                    bank.accounts = self.bank_account_service.get_bank_accounts(bank_id, session)

                formatted_bank = format_bank_comprehensive(bank, include_bank_accounts=include_bank_accounts)
                return ControllerResponseDTO(data=formatted_bank, response_code=ApiResponseCode.SUCCESS)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting bank {bank_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting bank {bank_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()   

        except Exception as e:
            current_app.logger.error(f"Error getting bank {bank_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create bank
    ###############################################

    def create_bank(self) -> ControllerResponseDTO:
        """
        Create a new bank with enhanced validation and response.
            
        Returns:
            ControllerResponseDTO: DTO containing bank data and status
        """
        try:
            # Get pre-validated data from middleware
            bank_data = getattr(request, 'validated_data', {})
            if not bank_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)

            session = self._get_session()
            
            try:
                bank = self.bank_service.create_bank(bank_data, session)
                
                session.commit()
                
                formatted_bank = format_bank(bank)
                return ControllerResponseDTO(data=formatted_bank, response_code=ApiResponseCode.CREATED)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating bank: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating bank: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error creating bank: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Delete bank
    ###############################################

    def delete_bank(self, bank_id: int) -> ControllerResponseDTO:
        """
        Delete a bank with enhanced response.
        
        Args:
            bank_id: ID of the bank to delete
            
        Returns:
            ControllerResponseDTO: DTO containing bank data and status
        """
        try:
            session = self._get_session()
        
            try:
                success = self.bank_service.delete_bank(bank_id, session)
                if not success:
                    return ControllerResponseDTO(error="Bank not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting bank {bank_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting bank {bank_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error deleting bank {bank_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################################################
    # BANK ACCOUNT ENDPOINTS
    ###############################################################################

    ###############################################
    # Get bank accounts
    ###############################################

    def get_bank_accounts(self, bank_id: int) -> ControllerResponseDTO:
        """
        Get all bank accounts with enhanced validation and response.

        Args:
            bank_id: ID of the bank to get bank accounts for
            
        Returns:
            ControllerResponseDTO: DTO containing bank accounts data and status
        """
        try:
            session = self._get_session()

            try:
                bank_accounts = self.bank_account_service.get_bank_accounts(session, bank_id)
                if not bank_accounts:
                    return ControllerResponseDTO(error="Bank accounts not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_bank_accounts = [format_bank_account(bank_account) for bank_account in bank_accounts]
                return ControllerResponseDTO(data=formatted_bank_accounts, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting bank accounts {bank_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting bank accounts {bank_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting bank accounts {bank_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_bank_account_by_id(self, bank_account_id: int) -> ControllerResponseDTO:
        """
        Get a bank account by ID with enhanced validation and response.
        
        Args:
            bank_account_id: ID of the bank account to retrieve
            
        Returns:
            ControllerResponseDTO: DTO containing bank account data and status
        """
        try:
            session = self._get_session()

            try:
                bank_account = self.bank_account_service.get_bank_account_by_id(bank_account_id, session)
                if not bank_account:
                    return ControllerResponseDTO(error="Bank account not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_bank_account = format_bank_account(bank_account)
                return ControllerResponseDTO(data=formatted_bank_account, response_code=ApiResponseCode.SUCCESS)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting bank account {bank_account_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting bank account {bank_account_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting bank account {bank_account_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create bank account
    ###############################################

    def create_bank_account(self) -> ControllerResponseDTO:
        """
        Create a new bank account with enhanced validation and response.
        
        Returns:
            ControllerResponseDTO: DTO containing bank account data and status
        """
        try:
            # Get pre-validated data from middleware
            bank_account_data = getattr(request, 'validated_data', {})
            if not bank_account_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)

            session = self._get_session()
        
            try:
                bank_account = self.bank_account_service.create_bank_account(bank_account_data, session)
                
                session.commit()
                
                formatted_bank_account = format_bank_account(bank_account)

                return ControllerResponseDTO(data=formatted_bank_account, response_code=ApiResponseCode.CREATED)
                
            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating bank account: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating bank account: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error creating bank account: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Delete bank account
    ###############################################

    def delete_bank_account(self, bank_account_id: int) -> ControllerResponseDTO:
        """
        Delete a bank account with enhanced response.
        
        Args:
            bank_account_id: ID of the bank account to delete
            
        Returns:
            ControllerResponseDTO: DTO containing bank account data and status
        """
        try:
            session = self._get_session()
            
            try:
                success = self.bank_account_service.delete_bank_account(bank_account_id, session)
                if not success:
                    return ControllerResponseDTO(error="Bank account not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting bank account {bank_account_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting bank account {bank_account_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error deleting bank account {bank_account_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
        

    ###############################################################################
    # SESSION HANDLING
    ###############################################################################

    def _get_session(self) -> Session:
        """
        Get the current database session from middleware.
        
        Returns:
            Database session from Flask's g context
        """
        from src.api.middleware.database_session import get_current_session
        return get_current_session()
