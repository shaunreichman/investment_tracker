"""
Bank Service.

This service extracts bank operations and business logic from the Bank model
to provide clean separation of concerns and improved testability.

Extracted functionality:
- Bank creation with validation
- Bank updates with validation
- Bank deletion with validation
- Bank business rule enforcement
"""

from typing import Optional, Dict, Any, List, Union
from sqlalchemy.orm import Session

from src.banking.models import Bank
from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.repositories.bank_repository import BankRepository
from src.banking.enums import Country


class BankService:
    """
    Service for handling bank operations and business logic.
    
    This service provides clean separation of concerns for:
    - Bank creation with comprehensive validation
    - Bank updates with validation and business rules
    - Bank deletion with dependency checking
    - Bank business rule enforcement
    """
    
    def __init__(self, validation_service: Optional[BankingValidationService] = None, bank_repository: Optional[BankRepository] = None):
        """
        Initialize the BankService.
        
        Args:
            validation_service: Validation service to use. If None, creates a new one.
            bank_repository: Bank repository to use. If None, creates a new one.
        """
        self.validation_service = validation_service or BankingValidationService()
        self.bank_repository = bank_repository or BankRepository()
    
    # ============================================================================
    # BANK CREATION
    # ============================================================================
    
    def create_bank(
        self,
        name: str,
        country: Union[str, Country],
        swift_bic: Optional[str] = None,
        session: Optional[Session] = None
    ) -> Bank:
        """
        Create a new bank with comprehensive validation.
        
        This method extracts the business logic from Bank.create() to provide
        clean separation of concerns and improved testability.
        
        Args:
            name: Bank name
            country: Country code (2-letter ISO) or Country enum
            swift_bic: Optional SWIFT/BIC identifier
            session: Database session
            
        Returns:
            Bank: The created bank instance
            
        Raises:
            ValueError: If validation fails
        """
        # Validate all input data
        self.validation_service.validate_bank_name_or_raise(name)
        self.validation_service.validate_country_code_or_raise(country)
        self.validation_service.validate_swift_bic_or_raise(swift_bic)
        
        # Normalize inputs to enums
        normalized_country = self.validation_service.normalize_country(country)
        
        # Validate uniqueness
        self.validation_service.validate_bank_uniqueness_or_raise(name, normalized_country, session)
        
        # Create bank instance
        bank = Bank(
            name=name.strip(),
            country=normalized_country,
            swift_bic=swift_bic
        )
        
        # Use repository to create bank
        return self.bank_repository.create(bank, session)
    
    # ============================================================================
    # BANK UPDATES
    # ============================================================================
    
    def update_bank(
        self,
        bank_id: int,
        data: Dict[str, Any],
        session: Session
    ) -> Bank:
        """
        Update a bank with comprehensive validation.
        
        This method extracts the business logic from the controller to provide
        clean separation of concerns and improved testability.
        
        Args:
            bank_id: ID of the bank to update
            data: Update data dictionary
            session: Database session
            
        Returns:
            Bank: The updated bank instance
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If bank not found
        """
        # Get existing bank
        bank = self.get_bank_by_id(bank_id, session)
        if not bank:
            raise RuntimeError("Bank not found")
        
        # Validate all update data
        self.validation_service.validate_bank_data(data, session, exclude_id=bank_id)
        
        # Update fields
        if 'name' in data:
            bank.name = data['name'].strip()
        
        if 'country' in data:
            bank.country = data['country'].upper()
        
        if 'swift_bic' in data:
            bank.swift_bic = data['swift_bic']
        
        # Commit changes
        session.commit()
        
        return bank
    
    # ============================================================================
    # BANK DELETION
    # ============================================================================
    
    def delete_bank(
        self,
        bank_id: int,
        session: Session
    ) -> bool:
        """
        Delete a bank with dependency checking.
        
        This method extracts the business logic from the controller to provide
        clean separation of concerns and improved testability.
        
        Args:
            bank_id: ID of the bank to delete
            session: Database session
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            RuntimeError: If bank not found or has dependencies
        """
        # Get existing bank
        bank = self.get_bank_by_id(bank_id, session)
        if not bank:
            raise RuntimeError("Bank not found")
        
        # Check for dependent bank accounts
        if self._has_dependent_accounts(bank_id, session):
            raise RuntimeError("Cannot delete bank with dependent accounts")
        
        # Delete bank
        session.delete(bank)
        session.commit()
        
        return True
    
    # ============================================================================
    # BANK QUERIES
    # ============================================================================
    
    def get_bank_by_id(self, bank_id: int, session: Session) -> Optional[Bank]:
        """
        Get a bank by its ID.
        
        Args:
            bank_id: ID of the bank to retrieve
            session: Database session
            
        Returns:
            Bank: Bank instance if found, None otherwise
        """
        return session.query(Bank).filter(Bank.id == bank_id).first()
    
    def get_bank_by_name_and_country(self, name: str, country: str, session: Session) -> Optional[Bank]:
        """
        Get a bank by name and country.
        
        Args:
            name: Bank name
            country: Country code
            session: Database session
            
        Returns:
            Bank: Bank instance if found, None otherwise
        """
        return session.query(Bank).filter(
            Bank.name == name.strip(),
            Bank.country == country.upper()
        ).first()
    
    def get_all_banks(self, session: Session) -> List[Bank]:
        """
        Get all banks.
        
        Args:
            session: Database session
            
        Returns:
            List[Bank]: List of all banks
        """
        return self.bank_repository.get_all(session)
    
    def get_banks_by_country(self, country: str, session: Session) -> List[Bank]:
        """
        Get all banks in a specific country.
        
        Args:
            country: Country code
            session: Database session
            
        Returns:
            List[Bank]: List of banks in the country
        """
        return self.bank_repository.get_by_country(country.upper(), session)
    
    # ============================================================================
    # DEPENDENCY CHECKING
    # ============================================================================
    
    def _has_dependent_accounts(self, bank_id: int, session: Session) -> bool:
        """
        Check if a bank has dependent bank accounts.
        
        Args:
            bank_id: Bank ID to check
            session: Database session
            
        Returns:
            bool: True if bank has dependent accounts
        """
        from src.banking.repositories.bank_account_repository import BankAccountRepository
        
        account_repo = BankAccountRepository()
        count = account_repo.count_by_bank(bank_id, session)
        return count > 0
    
    def get_dependent_accounts_count(self, bank_id: int, session: Session) -> int:
        """
        Get the count of dependent bank accounts for a bank.
        
        Args:
            bank_id: Bank ID to check
            session: Database session
            
        Returns:
            int: Number of dependent accounts
        """
        from src.banking.repositories.bank_account_repository import BankAccountRepository
        
        account_repo = BankAccountRepository()
        return account_repo.count_by_bank(bank_id, session)
    
    # ============================================================================
    # BUSINESS RULE ENFORCEMENT
    # ============================================================================
    
    def can_delete_bank(self, bank_id: int, session: Session) -> tuple[bool, str]:
        """
        Check if a bank can be deleted based on business rules.
        
        Args:
            bank_id: Bank ID to check
            session: Database session
            
        Returns:
            tuple[bool, str]: (can_delete, reason_if_not)
        """
        # Check if bank exists
        bank = self.get_bank_by_id(bank_id, session)
        if not bank:
            return False, "Bank not found"
        
        # Check for dependent accounts
        account_count = self.get_dependent_accounts_count(bank_id, session)
        if account_count > 0:
            return False, f"Bank has {account_count} dependent accounts"
        
        return True, "Bank can be deleted"
    
    def validate_bank_for_update(self, bank_id: int, data: Dict[str, Any], session: Session) -> tuple[bool, str]:
        """
        Validate if a bank can be updated with the given data.
        
        Args:
            bank_id: Bank ID to validate
            data: Update data to validate
            session: Database session
            
        Returns:
            tuple[bool, str]: (can_update, reason_if_not)
        """
        try:
            # Check if bank exists
            bank = self.get_bank_by_id(bank_id, session)
            if not bank:
                return False, "Bank not found"
            
            # Validate update data
            self.validation_service.validate_bank_data(data, session, exclude_id=bank_id)
            
            return True, "Bank can be updated"
            
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"
