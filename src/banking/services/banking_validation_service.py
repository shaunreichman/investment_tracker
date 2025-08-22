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

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.banking.models import Bank, BankAccount


class BankingValidationService:
    """
    Service for handling banking business rule validation.
    
    This service provides clean separation of concerns for:
    - Country and currency code validation
    - SWIFT/BIC validation
    - Uniqueness constraint validation
    - Business rule enforcement
    """
    
    def __init__(self):
        """Initialize the BankingValidationService."""
        pass
    
    # ============================================================================
    # COUNTRY CODE VALIDATION
    # ============================================================================
    
    def validate_country_code(self, country: str) -> bool:
        """
        Validate that a country code is a valid 2-letter ISO code.
        
        Args:
            country: Country code to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not country:
            return False
        
        # Must be exactly 2 letters
        if not isinstance(country, str) or len(country) != 2:
            return False
        
        # Must be alphabetic
        if not country.isalpha():
            return False
        
        return True
    
    def validate_country_code_or_raise(self, country: str) -> None:
        """
        Validate country code and raise ValueError if invalid.
        
        Args:
            country: Country code to validate
            
        Raises:
            ValueError: If country code is invalid
        """
        if not self.validate_country_code(country):
            raise ValueError("Country must be a 2-letter ISO code")
    
    # ============================================================================
    # CURRENCY CODE VALIDATION
    # ============================================================================
    
    def validate_currency_code(self, currency: str) -> bool:
        """
        Validate that a currency code is a valid 3-letter ISO code.
        
        Args:
            currency: Currency code to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not currency:
            return False
        
        # Must be exactly 3 letters
        if not isinstance(currency, str) or len(currency) != 3:
            return False
        
        # Must be alphabetic
        if not currency.isalpha():
            return False
        
        return True
    
    def validate_currency_code_or_raise(self, currency: str) -> None:
        """
        Validate currency code and raise ValueError if invalid.
        
        Args:
            currency: Currency code to validate
            
        Raises:
            ValueError: If currency code is invalid
        """
        if not self.validate_currency_code(currency):
            raise ValueError("Currency must be a 3-letter ISO code")
    
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
        query = session.query(Bank).filter(
            Bank.name == name.strip(),
            Bank.country == country.upper()
        )
        
        if exclude_id is not None:
            query = query.filter(Bank.id != exclude_id)
        
        existing_bank = query.first()
        return existing_bank is None
    
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
        query = session.query(BankAccount).filter(
            BankAccount.entity_id == entity_id,
            BankAccount.bank_id == bank_id,
            BankAccount.account_number == account_number.strip()
        )
        
        if exclude_id is not None:
            query = query.filter(BankAccount.id != exclude_id)
        
        existing_account = query.first()
        return existing_account is None
    
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
        
        bank = session.query(Bank).filter(Bank.id == bank_id).first()
        return bank is not None
    
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
