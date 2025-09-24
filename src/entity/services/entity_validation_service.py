"""
Entity Validation Service.

This module provides the EntityValidationService class,
which contains the validation logic for the entity system.
"""

from typing import List
from sqlalchemy.orm import Session
import logging

class EntityValidationService:
    """
    Entity Validation Service.

    This class contains the validation logic for the entity system.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
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
        bank_accounts = self.bank_account_repository.get_bank_accounts(session, entity_id=entity_id)
        if bank_accounts:
            errors['bank_accounts'] = ["Cannot delete entity with dependent bank accounts"]
        
        # Cannot delete entity with dependent tax statements
        tax_statements = self.tax_statement_repository.get_tax_statements(session, entity_id=entity_id)
        if tax_statements:
            errors['tax_statements'] = ["Cannot delete entity with dependent tax statements"]
        
        # Cannot delete entity with dependent funds
        funds = self.fund_repository.get_funds(session, entity_id=entity_id)
        if funds:
            errors['funds'] = ["Cannot delete entity with dependent funds"]

        return errors