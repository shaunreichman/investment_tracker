"""
Entity domain models.

This module contains the core entity models including Entity.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

# Import the Base from shared
from ..shared.base import Base


class EntityType(enum.Enum):
    """Enumeration for entity types."""
    INDIVIDUAL = "individual"
    COMPANY = "company"
    TRUST = "trust"
    PARTNERSHIP = "partnership"


class Entity(Base):
    """Model representing an investing entity (person or company)."""
    __tablename__ = 'entities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    tax_jurisdiction = Column(String(10), default="AU")  # Tax jurisdiction (e.g., 'AU' for Australia, 'US' for United States)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    funds = relationship("Fund", back_populates="entity", cascade="all, delete-orphan")
    tax_statements = relationship("TaxStatement", back_populates="entity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}', jurisdiction='{self.tax_jurisdiction}')>"
    
    def get_financial_year(self, date):
        """Get the financial year for a given date based on the entity's tax jurisdiction."""
        if self.tax_jurisdiction == "AU":
            # Australian financial year: July 1 to June 30
            if date.month >= 7:
                # July to December: current year to next year
                return f"{date.year}-{str(date.year + 1)[-2:]}"
            else:
                # January to June: previous year to current year
                return f"{date.year - 1}-{str(date.year)[-2:]}"
        else:
            # Default to calendar year for other jurisdictions
            return str(date.year) 