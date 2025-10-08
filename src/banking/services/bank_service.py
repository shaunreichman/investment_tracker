"""
Bank Service.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from src.banking.models import Bank
from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.repositories.bank_repository import BankRepository
from src.banking.enums.bank_enums import BankType, SortFieldBank, BankStatus
from src.shared.enums.shared_enums import Country, SortOrder


class BankService:
    """
    Service for handling bank operations and business logic.
    This module provides the BankService class, which handles bank operations and business logic.
    The service provides clean separation of concerns for:
    - Bank retrieval
    - Bank creation
    - Bank deletion with dependency checking

    The service uses the BankingValidationService to validate banks and the BankRepository to perform CRUD operations.
    The service is used by the BankingController to handle bank operations.
    """
    
    def __init__(self):
        """
        Initialize the BankService.
        
        Args:
            None
        """
        self.banking_validation_service = BankingValidationService()
        self.bank_repository = BankRepository()


    ################################################################################
    # Get Bank
    ################################################################################

    def get_banks(self, session: Session,
                    names: Optional[List[str]] = None,
                    countries: Optional[List[Country]] = None,
                    bank_types: Optional[List[BankType]] = None,
                    sort_by: SortFieldBank = SortFieldBank.NAME,
                    sort_order: SortOrder = SortOrder.ASC,
                    include_bank_accounts: Optional[bool] = False,
                    include_bank_account_balances: Optional[bool] = False
    ) -> List[Bank]:
        """
        Get all banks.
        
        Args:
            session: Database session
            names: Bank names
            countries: Country codes
            bank_types: Bank types
            sort_by: Sort field
            sort_order: Sort order
            include_bank_accounts: Whether to include bank accounts
            include_bank_account_balances: Whether to include bank account balances
        
        Returns:
            List of banks
        """
        return self.bank_repository.get_banks(session, names, countries, bank_types, sort_by, sort_order, include_bank_accounts, include_bank_account_balances)

    def get_bank_by_id(self, bank_id: int, session: Session, include_bank_accounts: Optional[bool] = False, include_bank_account_balances: Optional[bool] = False) -> Optional[Bank]:
        """
        Get a bank by its ID.
        
        Args:
            bank_id: ID of the bank to retrieve
            session: Database session
            include_bank_accounts: Whether to include bank accounts
            include_bank_account_balances: Whether to include bank account balances
            
        Returns:
            Bank: Bank instance if found, None otherwise
        """
        return self.bank_repository.get_bank_by_id(bank_id, session, include_bank_accounts, include_bank_account_balances)


    ################################################################################
    # Create Bank
    ################################################################################
    
    def create_bank(self, bank_data: Dict[str, Any], session: Session) -> Bank:
        """
        Create a new bank.
        
        Args:
            bank_data: Dictionary containing bank data
            session: Database session
            
        Returns:
            Bank: The created bank instance
            
        Raises:
            ValueError: If validation fails
        """
        processed_data = bank_data.copy()

        # Set the bank status to INACTIVE on creation
        processed_data['status'] = BankStatus.INACTIVE

        bank = self.bank_repository.create_bank(processed_data, session)
        if not bank:
            raise ValueError(f"Failed to create bank with name '{processed_data.get('name', 'unknown')}'")

        return bank

    
    ################################################################################
    # Delete Bank
    ################################################################################
    
    def delete_bank(self, bank_id: int, session: Session) -> bool:
        """
        Delete a bank with dependency checking.
        
        Args:
            bank_id: ID of the bank to delete
            session: Database session
            
        Returns:
            bool: True if bank was deleted, False otherwise
            
        Raises:
            ValueError: If bank not found or has dependencies
        """
        # Get existing bank
        bank = self.get_bank_by_id(bank_id, session)
        if not bank:
            raise ValueError(f"Bank with ID {bank_id} not found")
        
        # Check for dependent bank accounts
        validation_errors = self.banking_validation_service.validate_bank_deletion(bank_id, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed for bank with ID {bank_id}: {validation_errors}")
        
        # Delete bank through repository
        success = self.bank_repository.delete_bank(bank_id, session)
        if not success:
            raise ValueError(f"Failed to delete bank with ID {bank_id}")
        
        return success