"""
Entity Model.

This module provides the Entity model class, representing investing entities (people or companies) in the system.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from src.shared.enums.shared_enums import Country
from src.entity.enums.entity_enums import EntityType
from src.shared.base import Base
from typing import Dict

class Entity(Base):
    """Model representing an investing entity (person or company)."""
    __tablename__ = 'entities'
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    name = Column(String(255), nullable=False, unique=True)  # (MANUAL) entity name
    entity_type = Column(Enum(EntityType), nullable=False)  # (MANUAL) entity type
    description = Column(Text)  # (MANUAL) entity description
    tax_jurisdiction = Column(Enum(Country), default="AU")  # (MANUAL) tax jurisdiction (e.g., 'AU' for Australia, 'US' for United States)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was last updated
    
    # Relationships
    funds = relationship("Fund", back_populates="entity", cascade="all, delete-orphan")
    bank_accounts = relationship("BankAccount", back_populates="entity", cascade="all, delete-orphan")
    fund_tax_statements = relationship("FundTaxStatement", back_populates="entity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}')>"


    def get_field_classification(self) -> Dict[str, str]:
        """
        Field classification for the entity model.
        
        Returns:
            Dict[str, str]: Field classification for the entity model
        """
        return {
            'id': 'SYSTEM',
            'name': 'MANUAL',
            'entity_type': 'MANUAL',
            'description': 'MANUAL',
            'tax_jurisdiction': 'MANUAL',
            'created_at': 'SYSTEM',
            'updated_at': 'SYSTEM',
        }