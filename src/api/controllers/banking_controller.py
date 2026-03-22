"""
Banking API Controller.
"""

from flask import request, current_app
from sqlalchemy.orm import Session
from src.api.dto.controller_response_dto import ControllerResponseDTO
from src.api.dto.response_codes import ApiResponseCode
from src.api.controllers.formatters.banking_formatter import format_bank, format_bank_account, format_bank_account_balance, format_bank_comprehensive, format_bank_account_comprehensive
from src.shared.exceptions import ValidationException
from src.banking.services.bank_service import BankService
from src.banking.services.bank_account_service import BankAccountService
from src.banking.services.bank_account_balance_service import BankAccountBalanceService


class BankingController:
    """
    Controller for banking operations.

    Attributes:
        bank_service (BankService): Service for bank operations
        bank_account_service (BankAccountService): Service for bank account operations
    """
    
    def __init__(self):
        """Initialize the enhanced banking controller."""
        self.bank_service = BankService()
        self.bank_account_service = BankAccountService()
        self.bank_account_balance_service = BankAccountBalanceService()
    
    
    ###############################################################################
    # BANK ENDPOINTS
    ###############################################################################

    ###############################################
    # Get bank
    ###############################################

    def get_banks(self) -> ControllerResponseDTO:
        """
        Get all banks with optional search filters and bank accounts.
        
        Search parameters (all optional):
            name: Filter by bank name
            names: Filter by bank names
            country: Filter by country code
            countries: Filter by country codes
            bank_type: Filter by bank type
            bank_types: Filter by bank types
            sort_by: Sort by (NAME, COUNTRY, CURRENCY, TYPE, STATUS, CREATED_AT, UPDATED_AT)
            sort_order: Sort order (ASC, DESC)
            include_bank_accounts: Whether to include bank accounts
            include_bank_account_balances: Whether to include bank account balances
                    
        Returns:
            ControllerResponseDTO containing banks data or error
        """
        try:
            # Get search parameters from middleware (all optional)
            search_data = getattr(request, 'validated_data', {})

            # Normalize single values to arrays for service layer
            if 'name' in search_data:
                search_data['names'] = [search_data['name']]
            if 'country' in search_data:
                search_data['countries'] = [search_data['country']]
            if 'bank_type' in search_data:
                search_data['bank_types'] = [search_data['bank_type']]
            
            # Extract search parameters (None if not provided)
            names = search_data.get('names')
            countries = search_data.get('countries')
            bank_types = search_data.get('bank_types')
            sort_by = search_data.get('sort_by')
            sort_order = search_data.get('sort_order')

            include_bank_accounts = search_data.get('include_bank_accounts', False)
            include_bank_account_balances = search_data.get('include_bank_account_balances', False)
            
            session = self._get_session()
            try:
                # Pass search parameters to service (all are optional)
                banks = self.bank_service.get_banks(
                    session=session,
                    names=names, 
                    countries=countries, 
                    bank_types=bank_types,
                    sort_by=sort_by,
                    sort_order=sort_order,
                    include_bank_accounts=include_bank_accounts,
                    include_bank_account_balances=include_bank_account_balances
                )
                
                if banks is None:
                    return ControllerResponseDTO(error="Banks not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_banks = [format_bank_comprehensive(bank, include_bank_accounts, include_bank_account_balances) for bank in banks]
                response_data = {
                    'banks': formatted_banks,
                    'count': len(formatted_banks)
                }
                return ControllerResponseDTO(data=response_data, response_code=ApiResponseCode.SUCCESS)

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

    def get_bank_by_id(self, bank_id: int) -> ControllerResponseDTO:
        """
        Get a bank by ID with optional bank accounts.
        
        Args:
            bank_id: ID of the bank to retrieve

        Search parameters (all optional):
            include_bank_accounts: Whether to include bank accounts
            include_bank_account_balances: Whether to include bank account balances

        Returns:
            ControllerResponseDTO: DTO containing bank data and status
        """
        try:
            search_data = getattr(request, 'validated_data', {})

            include_bank_accounts = search_data.get('include_bank_accounts', False)
            include_bank_account_balances = search_data.get('include_bank_account_balances', False)
            
            session = self._get_session()
            
            try:
                bank = self.bank_service.get_bank_by_id(bank_id, session, include_bank_accounts, include_bank_account_balances)
                if bank is None:
                    return ControllerResponseDTO(error=f"Bank with ID {bank_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_bank = format_bank_comprehensive(bank, include_bank_accounts, include_bank_account_balances)
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
            bank_data = getattr(request, 'validated_data', {})
            if not bank_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)

            session = self._get_session()
            
            try:
                bank = self.bank_service.create_bank(bank_data, session)
                
                session.commit()
                
                formatted_bank = format_bank(bank)
                return ControllerResponseDTO(data=formatted_bank, response_code=ApiResponseCode.CREATED)
                
            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating bank: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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
                    return ControllerResponseDTO(error=f"Bank with ID {bank_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
                
            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting bank {bank_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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

    def get_bank_accounts(self, bank_id: int = None) -> ControllerResponseDTO:
        """
        Get all bank accounts with optional search filters.

        Args:
            bank_id: ID of the bank to get bank accounts for (optional)

        Search parameters (all optional):
            bank_id: Filter by bank ID
            bank_ids: Filter by bank IDs
            entity_id: Filter by entity ID
            entity_ids: Filter by entity IDs
            account_name: Filter by account name
            account_names: Filter by account names
            currency: Filter by currency code
            currencies: Filter by currency codes
            status: Filter by status
            statuses: Filter by statuses
            account_type: Filter by account type
            account_types: Filter by account types
            sort_by: Sort by (NAME, ACCOUNT_NUMBER, CURRENCY, STATUS, CREATED_AT, UPDATED_AT)
            sort_order: Sort order (ASC, DESC)
            include_bank_account_balances: Whether to include bank account balances
                    
        Returns:
            ControllerResponseDTO
        """
        try:
            search_data = getattr(request, 'validated_data', {})

            # Normalize single values to arrays for service layer
            if bank_id:
                search_data['bank_ids'] = [bank_id]
            elif 'bank_id' in search_data:
                search_data['bank_ids'] = [search_data['bank_id']]
            if 'entity_id' in search_data:
                search_data['entity_ids'] = [search_data['entity_id']]
            if 'account_name' in search_data:
                search_data['account_names'] = [search_data['account_name']]
            if 'currency' in search_data:
                search_data['currencies'] = [search_data['currency']]
            if 'status' in search_data:
                search_data['statuses'] = [search_data['status']]
            if 'account_type' in search_data:
                search_data['account_types'] = [search_data['account_type']]

            bank_ids = search_data.get('bank_ids')
            entity_ids = search_data.get('entity_ids')
            account_names = search_data.get('account_names')
            currencies = search_data.get('currencies')
            statuses = search_data.get('statuses')
            account_types = search_data.get('account_types')
            sort_by = search_data.get('sort_by')
            sort_order = search_data.get('sort_order')

            include_bank_account_balances = search_data.get('include_bank_account_balances', False)
            
            session = self._get_session()
            try:
                # Pass search parameters to service (all are optional)
                bank_accounts = self.bank_account_service.get_bank_accounts(
                    session=session,
                    bank_ids=bank_ids, 
                    entity_ids=entity_ids, 
                    account_names=account_names, 
                    currencies=currencies, 
                    statuses=statuses, 
                    account_types=account_types,
                    sort_by=sort_by,
                    sort_order=sort_order,
                    include_bank_account_balances=include_bank_account_balances
                )
                if bank_accounts is None:
                    return ControllerResponseDTO(error="Bank accounts not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_bank_accounts = [format_bank_account_comprehensive(bank_account, include_bank_account_balances) for bank_account in bank_accounts]
                response_data = {
                    'bank_accounts': formatted_bank_accounts,
                    'count': len(formatted_bank_accounts)
                }
                return ControllerResponseDTO(data=response_data, response_code=ApiResponseCode.SUCCESS)

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
            
        Search parameters (all optional):
            include_bank_account_balances: Whether to include bank account balances

        Returns:
            ControllerResponseDTO: DTO containing bank account data and status
        """
        try:
            search_data = getattr(request, 'validated_data', {})

            include_bank_account_balances = search_data.get('include_bank_account_balances', False)

            session = self._get_session()
            try:
                bank_account = self.bank_account_service.get_bank_account_by_id(bank_account_id, session, include_bank_account_balances)
                if bank_account is None:
                    return ControllerResponseDTO(error=f"Bank account with ID {bank_account_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                formatted_bank_account = format_bank_account_comprehensive(bank_account, include_bank_account_balances)
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

    def create_bank_account(self, bank_id: int) -> ControllerResponseDTO:
        """
        Create a new bank account with enhanced validation and response.
        
        Args:
            bank_id: ID of the bank to add bank account to
            
        Returns:
            ControllerResponseDTO: DTO containing bank account data and status
        """
        try:
            bank_account_data = getattr(request, 'validated_data', {})
            if not bank_account_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)

            session = self._get_session()
        
            try:
                bank_account = self.bank_account_service.create_bank_account(bank_id, bank_account_data, session)
                
                session.commit()
                
                formatted_bank_account = format_bank_account(bank_account)

                return ControllerResponseDTO(data=formatted_bank_account, response_code=ApiResponseCode.CREATED)
                
            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating bank account: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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
                    return ControllerResponseDTO(error=f"Bank account with ID {bank_account_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()                
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)

            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting bank account {bank_account_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
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
    # BANK ACCOUNT BALANCE ENDPOINTS
    ###############################################################################

    ###############################################
    # Get bank account balances
    ############################################### 

    def get_bank_account_balances(self, bank_id: int = None, bank_account_id: int = None) -> ControllerResponseDTO:
        """
        Get all bank account balances for a specific bank account.

        Args:
            bank_id: ID of the bank to get balances for
            bank_account_id: ID of the bank account to get balances for

        Search parameters (all optional):
            bank_id: Filter by bank ID
            bank_ids: Filter by bank IDs
            bank_account_id: Filter by bank account ID
            bank_account_ids: Filter by bank account IDs
            currency: Filter by currency code
            currencies: Filter by currency codes
            start_date: Filter by start date
            end_date: Filter by end date
            sort_by: Sort by (DATE, CURRENCY, BALANCE, CREATED_AT, UPDATED_AT)
            sort_order: Sort order (ASC, DESC)

        Returns:
            ControllerResponseDTO containing bank account balances data or error
        """
        try:
            search_data = getattr(request, 'validated_data', {})
            
            # Normalize single values to arrays for service layer
            if bank_id:
                search_data['bank_ids'] = [bank_id]
            elif 'bank_id' in search_data:
                search_data['bank_ids'] = [search_data['bank_id']]
            if bank_account_id:
                search_data['bank_account_ids'] = [bank_account_id]
            elif 'bank_account_id' in search_data:
                search_data['bank_account_ids'] = [search_data['bank_account_id']]
            if 'currency' in search_data:
                search_data['currencies'] = [search_data['currency']]

            bank_ids = search_data.get('bank_ids')
            bank_account_ids = search_data.get('bank_account_ids')
            currencies = search_data.get('currencies')
            start_date = search_data.get('start_date')
            end_date = search_data.get('end_date')
            sort_by = search_data.get('sort_by')
            sort_order = search_data.get('sort_order')

            session = self._get_session()
            try:
                bank_account_balances = self.bank_account_balance_service.get_bank_account_balances(
                    session=session,
                    bank_ids=bank_ids,
                    bank_account_ids=bank_account_ids,
                    currencies=currencies,
                    start_date=start_date,
                    end_date=end_date,
                    sort_by=sort_by,
                    sort_order=sort_order
                )
                if bank_account_balances is None:
                    return ControllerResponseDTO(error="Bank account balances not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_bank_account_balances = [format_bank_account_balance(bank_account_balance) for bank_account_balance in bank_account_balances]
                response_data = {
                    'bank_account_balances': formatted_bank_account_balances,
                    'count': len(formatted_bank_account_balances)
                }
                return ControllerResponseDTO(data=response_data, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting bank account balances {bank_account_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting bank account balances {bank_account_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting bank account balances {bank_account_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)

    def get_bank_account_balance_by_id(self, bank_account_balance_id: int) -> ControllerResponseDTO:
        """
        Get a bank account balance by ID.

        Args:
            bank_account_balance_id: ID of the bank account balance to retrieve

        Returns:
            ControllerResponseDTO
        """
        try:
            session = self._get_session()
            try:
                bank_account_balance = self.bank_account_balance_service.get_bank_account_balance_by_id(bank_account_balance_id, session)
                if bank_account_balance is None:
                    return ControllerResponseDTO(error=f"Bank account balance with ID {bank_account_balance_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)

                formatted_bank_account_balance = format_bank_account_balance(bank_account_balance)
                return ControllerResponseDTO(data=formatted_bank_account_balance, response_code=ApiResponseCode.SUCCESS)

            except ValueError as e:
                current_app.logger.warning(f"Business logic error getting bank account balance {bank_account_balance_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error getting bank account balance {bank_account_balance_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error getting bank account balance {bank_account_balance_id}: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Create bank account balance
    ###############################################
    
    def create_bank_account_balance(self, bank_account_id: int) -> ControllerResponseDTO:
        """
        Create a new bank account balance.

        Args:
            bank_account_id: ID of the bank account to add bank account balance to

        Returns:
            ControllerResponseDTO
        """
        try:
            bank_account_balance_data = getattr(request, 'validated_data', {})
            if not bank_account_balance_data:
                return ControllerResponseDTO(error='No validated data available', response_code=ApiResponseCode.VALIDATION_ERROR)

            session = self._get_session()
            
            try:
                bank_account_balance = self.bank_account_balance_service.create_bank_account_balance(bank_account_id, bank_account_balance_data, session)
                
                session.commit()
                
                formatted_bank_account_balance = format_bank_account_balance(bank_account_balance)

                return ControllerResponseDTO(data=formatted_bank_account_balance, response_code=ApiResponseCode.CREATED)
                
            except ValidationException as e:
                current_app.logger.warning(f"Validation error creating bank account balance: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except ValueError as e:
                current_app.logger.warning(f"Business logic error creating bank account balance: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error creating bank account balance: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error creating bank account balance: {str(e)}")
            return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)


    ###############################################
    # Delete bank account balance
    ###############################################

    def delete_bank_account_balance(self, bank_account_balance_id: int) -> ControllerResponseDTO:
        """
        Delete a bank account balance.

        Args:
            bank_account_balance_id: ID of the bank account balance to delete

        Returns:
            ControllerResponseDTO containing bank account balance data or error
        """
        try:
            session = self._get_session()
            try:
                success = self.bank_account_balance_service.delete_bank_account_balance(bank_account_balance_id, session)
                if not success:
                    return ControllerResponseDTO(error=f"Bank account balance with ID {bank_account_balance_id} not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
                
                session.commit()
                return ControllerResponseDTO(response_code=ApiResponseCode.DELETED)
            
            except ValidationException as e:
                current_app.logger.warning(f"Validation error deleting bank account balance {bank_account_balance_id}: {e.message}")
                session.rollback()
                return ControllerResponseDTO(error=e.message, details=e.details, response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except ValueError as e:
                current_app.logger.warning(f"Business logic error deleting bank account balance {bank_account_balance_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error=str(e), response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR)
            except Exception as e:
                current_app.logger.error(f"Error deleting bank account balance {bank_account_balance_id}: {str(e)}")
                session.rollback()
                return ControllerResponseDTO(error="Internal server error", response_code=ApiResponseCode.INTERNAL_SERVER_ERROR)
            finally:
                session.close()

        except Exception as e:
            current_app.logger.error(f"Error deleting bank account balance {bank_account_balance_id}: {str(e)}")
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
