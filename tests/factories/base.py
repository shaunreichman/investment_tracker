"""
Base Factory Classes.

This module provides the foundational factory classes and utilities
for creating test data that mirrors the backend model structure.
"""

import factory
from faker import Faker
from typing import Optional, Type, Dict, Set
from sqlalchemy.orm import Session


fake = Faker()

# Global session for factories
_current_session: Optional[Session] = None


def set_session(session: Session) -> None:
    """
    Set the database session for all factories dynamically.
    
    This function automatically discovers all SessionedFactory subclasses
    and sets their session, eliminating the need for manual registration.
    
    Args:
        session: The SQLAlchemy session to use for all factories
    """
    global _current_session
    _current_session = session
    
    # Dynamically find all SessionedFactory subclasses
    for factory_class in SessionedFactory.__subclasses__():
        factory_class._meta.sqlalchemy_session = session


def get_session() -> Optional[Session]:
    """Get the current database session."""
    return _current_session


class SessionedFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Base factory that uses the current session.
    
    This factory automatically handles session management and provides
    consistent behavior across all domain factories.
    """
    
    class Meta:
        sqlalchemy_session = None  # Will be set dynamically
    
    @classmethod
    def create(cls, **kwargs):
        """
        Override create to ensure session is set before creating.
        
        This method ensures that the factory has a valid session before
        attempting to create objects, and handles the session management
        automatically.
        """
        if cls._meta.sqlalchemy_session is None:
            # Try to get session from current app context
            try:
                from flask import current_app
                if current_app.config.get('TEST_DB_SESSION'):
                    cls._meta.sqlalchemy_session = current_app.config['TEST_DB_SESSION']
            except:
                pass
        
        # Create the object
        obj = cls.build(**kwargs)
        
        # Add to session but don't commit - let the test session handle it
        if cls._meta.sqlalchemy_session:
            cls._meta.sqlalchemy_session.add(obj)
            cls._meta.sqlalchemy_session.flush()  # Flush to get ID but don't commit
            cls._meta.sqlalchemy_session.refresh(obj)
        
        return obj


def is_system_field(column_name: str, model_class: Type) -> bool:
    """Check if a column is a system field using model field classification."""
    classification = model_class().get_field_classification()
    field_type = classification.get(column_name, 'UNKNOWN')
    return field_type == 'SYSTEM'


def is_foreign_key_field(column_name: str, model_class: Type) -> bool:
    """Check if a column is a foreign key field using model field classification."""
    classification = model_class().get_field_classification()
    field_type = classification.get(column_name, 'UNKNOWN')
    return field_type == 'RELATIONSHIP'


def is_calculated_field(column_name: str, model_class: Type) -> bool:
    """Check if a column is a calculated field using model field classification."""
    classification = model_class().get_field_classification()
    field_type = classification.get(column_name, 'UNKNOWN')
    return field_type in ['CALCULATED', 'SYSTEM']


def get_manual_fields_from_model(model_class: Type) -> Set[str]:
    """Get manual fields from a model using its field classification."""
    classification = model_class().get_field_classification()
    manual_fields = set()
    
    for field_name, field_type in classification.items():
        # Include manual fields, but exclude foreign key fields (handled by relationships)
        if field_type == 'MANUAL' and not is_foreign_key_field(field_name, model_class):
            manual_fields.add(field_name)
    
    return manual_fields


def validate_factory_model_consistency(factory_class: Type[SessionedFactory], model_class: Type) -> Dict[str, Set[str]]:
    """
    Validate that factory fields match model fields using the model's field classification.
    
    This function uses the model's get_field_classification() method to determine
    which fields should be in factories, providing a clean and maintainable approach.
    
    Args:
        factory_class: The factory class to validate
        model_class: The corresponding model class
        
    Returns:
        Dictionary with 'missing_in_factory' and 'extra_in_factory' keys
    """
    # Get manual fields from model using field classification
    model_fields = get_manual_fields_from_model(model_class)
    
    # Get factory fields (excluding Meta and special attributes)
    factory_fields = set()
    for attr_name in dir(factory_class):
        if not attr_name.startswith('_') and not attr_name == 'Meta':
            attr = getattr(factory_class, attr_name)
            # Check if it's a factory-boy declaration
            if hasattr(attr, '__class__') and 'factory.declarations' in str(attr.__class__):
                # Skip relationship fields (SubFactory declarations)
                if 'SubFactory' not in str(attr.__class__):
                    factory_fields.add(attr_name)
    
    # Check for mismatches
    missing_in_factory = model_fields - factory_fields
    extra_in_factory = factory_fields - model_fields
    
    return {
        'missing_in_factory': missing_in_factory,
        'extra_in_factory': extra_in_factory
    }


def validate_all_factories() -> Dict[str, Dict[str, Set[str]]]:
    """
    Validate all factories against their corresponding models.
    
    Returns:
        Dictionary mapping factory names to their validation results
    """
    results = {}
    
    # Import all factories and their models
    from .fund_factories import (
        FundFactory, FundEventFactory, FundEventCashFlowFactory, FundTaxStatementFactory
    )
    from .entity_factories import EntityFactory
    from .banking_factories import BankFactory, BankAccountFactory
    from .company_factories import CompanyFactory, ContactFactory
    from .rates_factories import RiskFreeRateFactory
    
    from src.fund.models import Fund, FundEvent, FundEventCashFlow, FundTaxStatement
    from src.entity.models import Entity
    from src.banking.models import Bank, BankAccount
    from src.company.models import Company, Contact
    from src.rates.models import RiskFreeRate
    
    # Factory to model mapping
    factory_model_pairs = [
        (FundFactory, Fund),
        (FundEventFactory, FundEvent),
        (FundEventCashFlowFactory, FundEventCashFlow),
        (FundTaxStatementFactory, FundTaxStatement),
        (EntityFactory, Entity),
        (BankFactory, Bank),
        (BankAccountFactory, BankAccount),
        (CompanyFactory, Company),
        (ContactFactory, Contact),
        (RiskFreeRateFactory, RiskFreeRate),
    ]
    
    for factory_class, model_class in factory_model_pairs:
        factory_name = factory_class.__name__
        results[factory_name] = validate_factory_model_consistency(factory_class, model_class)
    
    return results
