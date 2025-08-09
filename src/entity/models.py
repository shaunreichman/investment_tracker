"""
Entity domain models.

This module contains the core entity models including Entity.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# Import the Base from shared
from ..shared.base import Base
from ..shared.utils import with_session, with_class_session

class Entity(Base):
    """Model representing an investing entity (person or company)."""
    __tablename__ = 'entities'
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    name = Column(String(255), nullable=False, unique=True)  # (MANUAL) entity name
    description = Column(Text)  # (MANUAL) entity description
    tax_jurisdiction = Column(String(10), default="AU")  # (MANUAL) tax jurisdiction (e.g., 'AU' for Australia, 'US' for United States)
    created_at = Column(DateTime, default=datetime.utcnow)  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # (SYSTEM) timestamp when record was last updated
    
    # Relationships
    funds = relationship("Fund", back_populates="entity", cascade="all, delete-orphan")
    bank_accounts = relationship("BankAccount", back_populates="entity", cascade="all, delete-orphan")
    tax_statements = relationship("TaxStatement", back_populates="entity", cascade="all, delete-orphan")
    
    @classmethod
    def create(cls, name, description=None, tax_jurisdiction="AU", session=None):
        """
        Create a new entity with validation and business logic.
        
        Args:
            name (str): Entity name (must be unique)
            description (str, optional): Entity description
            tax_jurisdiction (str): Tax jurisdiction code (default: "AU")
            session (Session): Database session (required - managed by outermost backend layer)
        
        Returns:
            Entity: The created entity
            
        Raises:
            ValueError: If name is empty or entity already exists
        """
        # Validation
        if not name or not name.strip():
            raise ValueError("Entity name is required and cannot be empty")
        
        name = name.strip()
        
        # Validate tax jurisdiction
        if tax_jurisdiction not in ["AU", "US", "UK", "CA"]:  # Add more as needed
            raise ValueError(f"Unsupported tax jurisdiction: {tax_jurisdiction}")
        
        # Check for existing entity with same name
        existing = session.query(cls).filter(cls.name == name).first()
        if existing:
            raise ValueError(f"Entity with name '{name}' already exists")
        
        # Create the entity
        entity = cls(
            name=name,
            description=description,
            tax_jurisdiction=tax_jurisdiction
        )
        
        session.add(entity)
        session.flush()  # Get the ID without committing
        
        return entity
    
    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}')>"
    
    @classmethod
    def get_by_name(cls, name, session=None):
        """
        Get an entity by name.
        
        Args:
            name (str): Entity name
            session (Session): Database session
        
        Returns:
            Entity or None: The entity if found, None otherwise
        """
        return session.query(cls).filter(cls.name == name).first()
    
    @classmethod
    def get_all(cls, session=None):
        """
        Get all entities.
        
        Args:
            session (Session): Database session
        
        Returns:
            list: List of all entities
        """
        return session.query(cls).all()
    
    @classmethod
    def get_by_id(cls, entity_id, session=None):
        """
        Get an entity by ID.
        
        Args:
            entity_id (int): Entity ID
            session (Session): Database session
        
        Returns:
            Entity or None: The entity if found, None otherwise
        """
        return session.query(cls).filter(cls.id == entity_id).first()
    
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
    
    def get_financial_years_for_period(self, start_date, end_date):
        """Get all financial years between start and end dates for this entity.
        
        Args:
            start_date (date): Start date for the period
            end_date (date): End date for the period
        
        Returns:
            set: Set of financial year strings
        """
        from .calculations import get_financial_years_for_fund_period
        return get_financial_years_for_fund_period(start_date, end_date, self) 