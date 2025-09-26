"""
Bank Service.

This service extracts bank operations and business logic from the Bank model
to provide clean separation of concerns and improved testability.

Extracted functionality:
- Bank creation with validation
- Bank deletion with validation
- Bank business rule enforcement
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
    
    This service provides clean separation of concerns for:
    - Bank creation with comprehensive validation
    - Bank updates with validation and business rules
    - Bank deletion with dependency checking
    - Bank business rule enforcement
    """
    
    def __init__(self, banking_validation_service: Optional[BankingValidationService] = None, bank_repository: Optional[BankRepository] = None):
        """
        Initialize the BankService.
        
        Args:
            banking_validation_service: Validation service to use. If None, creates a new one.
            bank_repository: Bank repository to use. If None, creates a new one.
        """
        self.banking_validation_service = banking_validation_service or BankingValidationService()
        self.bank_repository = bank_repository or BankRepository()


    ################################################################################
    # Get Bank
    ################################################################################

    def get_banks(self, session: Session,
                    name: Optional[str] = None,
                    country: Optional[Country] = None,
                    bank_type: Optional[BankType] = None,
                    sort_by: SortFieldBank = SortFieldBank.NAME,
                    sort_order: SortOrder = SortOrder.ASC
    ) -> List[Bank]:
        """
        Get all banks.
        
        Args:
            session: Database session
            name: Bank name
            country: Country code
            bank_type: Bank type
            sort_by: Sort field
            sort_order: Sort order
        """
        return self.bank_repository.get_banks(session, name, country, bank_type, sort_by, sort_order)

    def get_bank_by_id(self, bank_id: int, session: Session) -> Optional[Bank]:
        """
        Get a bank by its ID.
        
        Args:
            bank_id: ID of the bank to retrieve
            session: Database session
            
        Returns:
            Bank: Bank instance if found, None otherwise
        """
        return self.bank_repository.get_bank_by_id(bank_id, session)


    ################################################################################
    # Create Bank
    ################################################################################
    
    def create_bank(self, bank_data: Dict[str, Any], session: Session) -> Bank:
        """
        Create a new bank with comprehensive validation.
        
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
            raise ValueError(f"Failed to create bank")

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
            raise ValueError(f"Bank not found")
        
        # Check for dependent bank accounts
        validation_errors = self.banking_validation_service.validate_bank_deletion(bank_id, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")
        
        # Delete bank through repository
        success = self.bank_repository.delete_bank(bank_id, session)
        if not success:
            raise ValueError(f"Failed to delete bank")
        
        return success