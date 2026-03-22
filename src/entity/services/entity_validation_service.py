"""
Entity Validation Service.
"""

from typing import Dict, Any
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
    
    def validate_entity_deletion(self, entity_id: int, session: Session) -> Dict[str, Dict[str, Any]]:
        """
        Validate the deletion of an entity.

        Args:
            entity_id: ID of the entity to delete
            session: Database session
            
        Returns:
            Dictionary with structured validation errors (empty if valid)
            Format: {
                "bank_accounts_dependency": {"count": 3, "message": "..."},
                "tax_statements_dependency": {"count": 1, "message": "..."},
                "funds_dependency": {"count": 2, "message": "..."}
            }
        """
        dependencies = {}
        
        # Cannot delete entity with dependent bank accounts
        bank_accounts = self.bank_account_repository.get_bank_accounts(session, entity_ids=[entity_id])
        if bank_accounts:
            dependencies['bank_accounts_dependency'] = {
                'message': f"Cannot delete entity with bank accounts (we have {len(bank_accounts)} dependent bank accounts)"
            }
        
        # Cannot delete entity with dependent tax statements
        tax_statements = self.fund_tax_statement_repository.get_fund_tax_statements(session, entity_ids=[entity_id])
        if tax_statements:
            dependencies['tax_statements_dependency'] = {
                'message': f"Cannot delete entity with tax statements (we have {len(tax_statements)} dependent tax statements)"
            }
        
        # Cannot delete entity with dependent funds
        funds = self.fund_repository.get_funds(session, entity_ids=[entity_id])
        if funds:
            dependencies['funds_dependency'] = {
                'message': f"Cannot delete entity with funds (we have {len(funds)} dependent funds)"
            }

        return dependencies
        