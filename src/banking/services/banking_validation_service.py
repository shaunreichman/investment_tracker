"""
Banking Validation Service.

This service extracts business rule validation logic from the banking models
to provide clean separation of concerns and improved testability.

Extracted functionality:
- Country code validation (2-letter ISO)
- Currency code validation (3-letter ISO)
- SWIFT/BIC validation
- Uniqueness constraint validation
- Business rule enforcement
"""

from typing import Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.banking.models import Bank, BankAccount
from src.banking.repositories.bank_repository import BankRepository
from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.banking.enums import Country, Currency, AccountStatus


class BankingValidationService:
    """
    Service for handling banking business rule validation.
    
    This service provides clean separation of concerns for:
    - Country and currency code validation
    - SWIFT/BIC validation
    - Uniqueness constraint validation
    - Business rule enforcement
    """
    
    def __init__(self, bank_repository: Optional[BankRepository] = None, bank_account_repository: Optional[BankAccountRepository] = None):
        """
        Initialize the BankingValidationService.
        
        Args:
            bank_repository: Bank repository to use. If None, creates a new one.
            bank_account_repository: Bank account repository to use. If None, creates a new one.
        """
        self.bank_repository = bank_repository or BankRepository()
        self.bank_account_repository = bank_account_repository or BankAccountRepository()
    
    # ============================================================================
    # COUNTRY CODE VALIDATION
    # ============================================================================
    
    def validate_country_code(self, country: Union[str, Country]) -> bool:
        """
        Validate that a country code is a valid 2-letter ISO code.
        
        Args:
            country: Country code to validate (string or Country enum)
            
        Returns:
            True if valid, False otherwise
        """
        if not country:
            return False
        
        # Handle enum input
        if isinstance(country, Country):
            return True
        
        # Handle string input
        if not isinstance(country, str):
            return False
        
        # Must be exactly 2 letters
        if len(country) != 2:
            return False
        
        # Must be alphabetic
        if not country.isalpha():
            return False
        
        # Check if it's a valid enum value
        try:
            Country(country.upper())
            return True
        except ValueError:
            return False
    
    def validate_country_code_or_raise(self, country: Union[str, Country]) -> None:
        """
        Validate country code and raise ValueError if invalid.
        
        Args:
            country: Country code to validate (string or Country enum)
            
        Raises:
            ValueError: If country code is invalid
        """
        if not self.validate_country_code(country):
            if isinstance(country, str):
                raise ValueError(f"Country must be a valid 2-letter ISO code. Got: {country}")
            else:
                raise ValueError(f"Country must be a valid Country enum or string. Got: {type(country)}")
    
    def normalize_country(self, country: Union[str, Country]) -> Country:
        """
        Normalize country input to Country enum.
        
        Args:
            country: Country code (string or Country enum)
            
        Returns:
            Country: Normalized Country enum
            
        Raises:
            ValueError: If country code is invalid
        """
        if isinstance(country, Country):
            return country
        
        if isinstance(country, str):
            try:
                return Country(country.upper())
            except ValueError:
                raise ValueError(f"Invalid country code: {country}")
        
        raise ValueError(f"Country must be a string or Country enum. Got: {type(country)}")
    
    # ============================================================================
    # CURRENCY CODE VALIDATION
    # ============================================================================
    
    def validate_currency_code(self, currency: Union[str, Currency]) -> bool:
        """
        Validate that a currency code is a valid 3-letter ISO code.
        
        Args:
            currency: Currency code to validate (string or Currency enum)
            
        Returns:
            True if valid, False otherwise
        """
        if not currency:
            return False
        
        # Handle enum input
        if isinstance(currency, Currency):
            return True
        
        # Handle string input
        if not isinstance(currency, str):
            return False
        
        # Must be exactly 3 letters
        if len(currency) != 3:
            return False
        
        # Must be alphabetic
        if not currency.isalpha():
            return False
        
        # Check if it's a valid enum value
        try:
            Currency(currency.upper())
            return True
        except ValueError:
            return False
    
    def validate_currency_code_or_raise(self, currency: Union[str, Currency]) -> None:
        """
        Validate currency code and raise ValueError if invalid.
        
        Args:
            currency: Currency code to validate (string or Currency enum)
            
        Raises:
            ValueError: If currency code is invalid
        """
        if not self.validate_currency_code(currency):
            if isinstance(currency, str):
                raise ValueError(f"Currency must be a valid 3-letter ISO code. Got: {currency}")
            else:
                raise ValueError(f"Currency must be a valid Currency enum or string. Got: {type(currency)}")
    
    def normalize_currency(self, currency: Union[str, Currency]) -> Currency:
        """
        Normalize currency input to Currency enum.
        
        Args:
            currency: Currency code (string or Currency enum)
            
        Returns:
            Currency: Normalized Currency enum
            
        Raises:
            ValueError: If currency code is invalid
        """
        if isinstance(currency, Currency):
            return currency
        
        if isinstance(currency, str):
            try:
                return Currency(currency.upper())
            except ValueError:
                raise ValueError(f"Invalid currency code: {currency}")
        
        raise ValueError(f"Currency must be a string or Currency enum. Got: {type(currency)}")
    
    # ============================================================================
    # ACCOUNT STATUS VALIDATION
    # ============================================================================
    
    def validate_account_status(self, status: Union[bool, AccountStatus]) -> bool:
        """
        Validate account status.
        
        Args:
            status: Account status to validate (boolean or AccountStatus enum)
            
        Returns:
            True if valid, False otherwise
        """
        if status is None:
            return False
        
        # Handle enum input
        if isinstance(status, AccountStatus):
            return True
        
        # Handle boolean input (for backward compatibility)
        if isinstance(status, bool):
            return True
        
        return False
    
    def validate_account_status_or_raise(self, status: Union[bool, AccountStatus]) -> None:
        """
        Validate account status and raise ValueError if invalid.
        
        Args:
            status: Account status to validate (boolean or AccountStatus enum)
            
        Raises:
            ValueError: If account status is invalid
        """
        if not self.validate_account_status(status):
            raise ValueError(f"Account status must be a valid AccountStatus enum or boolean. Got: {type(status)}")
    
    def normalize_account_status(self, status: Union[bool, AccountStatus]) -> AccountStatus:
        """
        Normalize account status input to AccountStatus enum.
        
        Args:
            status: Account status (boolean or AccountStatus enum)
            
        Returns:
            AccountStatus: Normalized AccountStatus enum
            
        Raises:
            ValueError: If account status is invalid
        """
        if isinstance(status, AccountStatus):
            return status
        
        if isinstance(status, bool):
            return AccountStatus.ACTIVE if status else AccountStatus.SUSPENDED
        
        raise ValueError(f"Account status must be a boolean or AccountStatus enum. Got: {type(status)}")
    
    # ============================================================================
    # SWIFT/BIC VALIDATION
    # ============================================================================
    
    def validate_swift_bic(self, swift_bic: Optional[str]) -> bool:
        """
        Validate SWIFT/BIC code format.
        
        Args:
            swift_bic: SWIFT/BIC code to validate (can be None)
            
        Returns:
            True if valid or None, False otherwise
        """
        if swift_bic is None:
            return True  # SWIFT/BIC is optional
        
        if not isinstance(swift_bic, str):
            return False
        
        # SWIFT/BIC should be 8 or 11 characters
        if len(swift_bic) not in [8, 11]:
            return False
        
        # Should be alphanumeric
        if not swift_bic.isalnum():
            return False
        
        return True
    
    def validate_swift_bic_or_raise(self, swift_bic: Optional[str]) -> None:
        """
        Validate SWIFT/BIC code and raise ValueError if invalid.
        
        Args:
            swift_bic: SWIFT/BIC code to validate
            
        Raises:
            ValueError: If SWIFT/BIC code is invalid
        """
        if not self.validate_swift_bic(swift_bic):
            raise ValueError("SWIFT/BIC must be 8 or 11 alphanumeric characters")
    
    # ============================================================================
    # BANK NAME VALIDATION
    # ============================================================================
    
    def validate_bank_name(self, name: str) -> bool:
        """
        Validate bank name.
        
        Args:
            name: Bank name to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not name:
            return False
        
        if not isinstance(name, str):
            return False
        
        # Name must not be empty after trimming
        if not name.strip():
            return False
        
        return True
    
    def validate_bank_name_or_raise(self, name: str) -> None:
        """
        Validate bank name and raise ValueError if invalid.
        
        Args:
            name: Bank name to validate
            
        Raises:
            ValueError: If bank name is invalid
        """
        if not self.validate_bank_name(name):
            raise ValueError("Bank name is required and cannot be empty")
    
    # ============================================================================
    # ACCOUNT NAME VALIDATION
    # ============================================================================
    
    def validate_account_name(self, account_name: str) -> bool:
        """
        Validate bank account name.
        
        Args:
            account_name: Account name to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not account_name:
            return False
        
        if not isinstance(account_name, str):
            return False
        
        # Name must not be empty after trimming
        if not account_name.strip():
            return False
        
        return True
    
    def validate_account_name_or_raise(self, account_name: str) -> None:
        """
        Validate account name and raise ValueError if invalid.
        
        Args:
            account_name: Account name to validate
            
        Raises:
            ValueError: If account name is invalid
        """
        if not self.validate_account_name(account_name):
            raise ValueError("Account name is required and cannot be empty")
    
    # ============================================================================
    # ACCOUNT NUMBER VALIDATION
    # ============================================================================
    
    def validate_account_number(self, account_number: str) -> bool:
        """
        Validate bank account number.
        
        Args:
            account_number: Account number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not account_number:
            return False
        
        if not isinstance(account_number, str):
            return False
        
        # Account number must not be empty after trimming
        if not account_number.strip():
            return False
        
        return True
    
    def validate_account_number_or_raise(self, account_number: str) -> None:
        """
        Validate account number and raise ValueError if invalid.
        
        Args:
            account_number: Account number to validate
            
        Raises:
            ValueError: If account number is invalid
        """
        if not self.validate_account_number(account_number):
            raise ValueError("Account number is required and cannot be empty")
    
    # ============================================================================
    # UNIQUENESS CONSTRAINT VALIDATION
    # ============================================================================
    
    def validate_bank_uniqueness(self, name: str, country: str, session: Session, exclude_id: Optional[int] = None) -> bool:
        """
        Validate that a bank with the same name doesn't exist in the same country.
        
        Args:
            name: Bank name to check
            country: Country code to check
            session: Database session
            exclude_id: Bank ID to exclude from check (for updates)
            
        Returns:
            True if unique, False if duplicate exists
        """
        existing_bank = self.bank_repository.get_by_name_and_country(name.strip(), country.upper(), session)
        
        if existing_bank is None:
            return True
        
        if exclude_id is not None and existing_bank.id == exclude_id:
            return True
        
        return False
    
    def validate_bank_uniqueness_or_raise(self, name: str, country: str, session: Session, exclude_id: Optional[int] = None) -> None:
        """
        Validate bank uniqueness and raise ValueError if duplicate exists.
        
        Args:
            name: Bank name to check
            country: Country code to check
            session: Database session
            exclude_id: Bank ID to exclude from check (for updates)
            
        Raises:
            ValueError: If bank with same name exists in same country
        """
        if not self.validate_bank_uniqueness(name, country, session, exclude_id):
            raise ValueError("Bank with this name already exists in this country")
    
    def validate_bank_account_uniqueness(self, entity_id: int, bank_id: int, account_number: str, session: Session, exclude_id: Optional[int] = None) -> bool:
        """
        Validate that a bank account with the same entity/bank/number doesn't exist.
        
        Args:
            entity_id: Entity ID to check
            bank_id: Bank ID to check
            account_number: Account number to check
            session: Database session
            exclude_id: Account ID to exclude from check (for updates)
            
        Returns:
            True if unique, False if duplicate exists
        """
        existing_account = self.bank_account_repository.get_by_unique(entity_id, bank_id, account_number.strip(), session)
        
        if existing_account is None:
            return True
        
        if exclude_id is not None and existing_account.id == exclude_id:
            return True
        
        return False
    
    def validate_bank_account_uniqueness_or_raise(self, entity_id: int, bank_id: int, account_number: str, session: Session, exclude_id: Optional[int] = None) -> None:
        """
        Validate bank account uniqueness and raise ValueError if duplicate exists.
        
        Args:
            entity_id: Entity ID to check
            bank_id: Bank ID to check
            account_number: Account number to check
            session: Database session
            exclude_id: Account ID to exclude from check (for updates)
            
        Raises:
            ValueError: If bank account already exists for this entity/bank/account_number
        """
        if not self.validate_bank_account_uniqueness(entity_id, bank_id, account_number, session, exclude_id):
            raise ValueError("Bank account already exists for this entity/bank/account_number")
    
    # ============================================================================
    # ENTITY AND BANK EXISTENCE VALIDATION
    # ============================================================================
    
    def validate_entity_exists(self, entity_id: int, session: Session) -> bool:
        """
        Validate that an entity exists.
        
        Args:
            entity_id: Entity ID to validate
            session: Database session
            
        Returns:
            True if entity exists, False otherwise
        """
        if not entity_id:
            return False
        
        # Import here to avoid circular imports
        from src.entity.models import Entity
        entity = session.query(Entity).filter(Entity.id == entity_id).first()
        return entity is not None
    
    def validate_entity_exists_or_raise(self, entity_id: int, session: Session) -> None:
        """
        Validate entity existence and raise ValueError if not found.
        
        Args:
            entity_id: Entity ID to validate
            session: Database session
            
        Raises:
            ValueError: If entity does not exist
        """
        if not self.validate_entity_exists(entity_id, session):
            raise ValueError("Entity not found")
    
    def validate_bank_exists(self, bank_id: int, session: Session) -> bool:
        """
        Validate that a bank exists.
        
        Args:
            bank_id: Bank ID to validate
            session: Database session
            
        Returns:
            True if bank exists, False otherwise
        """
        if not bank_id:
            return False
        
        return self.bank_repository.exists(bank_id, session)
    
    def validate_bank_exists_or_raise(self, bank_id: int, session: Session) -> None:
        """
        Validate bank existence and raise ValueError if not found.
        
        Args:
            bank_id: Bank ID to validate
            session: Database session
            
        Raises:
            ValueError: If bank does not exist
        """
        if not self.validate_bank_exists(bank_id, session):
            raise ValueError("Bank not found")
    
    # ============================================================================
    # COMPREHENSIVE VALIDATION METHODS
    # ============================================================================
    
    def validate_bank_data(self, data: Dict[str, Any], session: Session, exclude_id: Optional[int] = None) -> None:
        """
        Validate all bank data comprehensively.
        
        Args:
            data: Bank data dictionary
            session: Database session
            exclude_id: Bank ID to exclude from uniqueness check (for updates)
            
        Raises:
            ValueError: If any validation fails
        """
        # Validate required fields
        if 'name' in data:
            self.validate_bank_name_or_raise(data['name'])
        
        if 'country' in data:
            self.validate_country_code_or_raise(data['country'])
        
        if 'swift_bic' in data:
            self.validate_swift_bic_or_raise(data.get('swift_bic'))
        
        # Validate uniqueness if name and country are provided
        if 'name' in data and 'country' in data:
            self.validate_bank_uniqueness_or_raise(data['name'], data['country'], session, exclude_id)
    
    def validate_bank_account_data(self, data: Dict[str, Any], session: Session, exclude_id: Optional[int] = None) -> None:
        """
        Validate all bank account data comprehensively.
        
        Args:
            data: Bank account data dictionary
            session: Database session
            exclude_id: Account ID to exclude from uniqueness check (for updates)
            
        Raises:
            ValueError: If any validation fails
        """
        # Validate required fields
        if 'entity_id' in data:
            self.validate_entity_exists_or_raise(data['entity_id'], session)
        
        if 'bank_id' in data:
            self.validate_bank_exists_or_raise(data['bank_id'], session)
        
        if 'account_name' in data:
            self.validate_account_name_or_raise(data['account_name'])
        
        if 'account_number' in data:
            self.validate_account_number_or_raise(data['account_number'])
        
        if 'currency' in data:
            self.validate_currency_code_or_raise(data['currency'])
        
        # Validate uniqueness if all required fields are provided
        if all(key in data for key in ['entity_id', 'bank_id', 'account_number']):
            self.validate_bank_account_uniqueness_or_raise(
                data['entity_id'], 
                data['bank_id'], 
                data['account_number'], 
                session, 
                exclude_id
            )
