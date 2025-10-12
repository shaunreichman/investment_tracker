"""
Entity Validation Service.
"""

from typing import List
from sqlalchemy.orm import Session
import logging
from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.fund.repositories.fund_repository import FundRepository
from src.fund.repositories.fund_tax_statement_repository import FundTaxStatementRepository

class EntityValidationService:
    """
    Entity Validation Service.

    This module provides the EntityValidationService class, which handles entity business rule validation.
    The service provides clean separation of concerns for:
    - Entity deletion with dependency checking

    The service uses the BankAccountRepository, FundTaxStatementRepository, and FundRepository to perform CRUD operations.
    """

    def __init__(self):
        """
        Initialize the EntityValidationService.

        Args:
            bank_account_repository: Bank account repository to use. If None, creates a new one.
            fund_tax_statement_repository: Fund tax statement repository to use. If None, creates a new one.
            fund_repository: Fund repository to use. If None, creates a new one.
        """
        self.bank_account_repository = BankAccountRepository()
        self.fund_tax_statement_repository = FundTaxStatementRepository()
        self.fund_repository = FundRepository()
        
    ################################################################################
    # Validate Entity
    ################################################################################
    
    def validate_entity_deletion(self, entity_id: int, session: Session) -> List[str]:
        """
        Validate the deletion of an entity.

        Args:
            entity_id: ID of the entity to delete
            session: Database session
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = {}
        
        # Cannot delete entity with dependent bank accounts
        bank_accounts = self.bank_account_repository.get_bank_accounts(session, entity_ids=[entity_id])
        if bank_accounts:
            errors['bank_accounts'] = [f"Cannot delete entity with dependent bank accounts. We have {len(bank_accounts)} bank accounts associated with this entity."]
        
        # Cannot delete entity with dependent tax statements
        tax_statements = self.fund_tax_statement_repository.get_fund_tax_statements(session, entity_ids=[entity_id])
        if tax_statements:
            errors['tax_statements'] = [f"Cannot delete entity with dependent tax statements. We have {len(tax_statements)} tax statements associated with this entity."]
        
        # Cannot delete entity with dependent funds
        funds = self.fund_repository.get_funds(session, entity_ids=[entity_id])
        if funds:
            errors['funds'] = [f"Cannot delete entity with dependent funds. We have {len(funds)} funds associated with this entity."]

        return errors