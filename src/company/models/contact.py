"""
Contact Model.

This module provides the Contact model class representing contacts at companies.
The model handles only data persistence, with business logic
delegated to services for clean separation of concerns.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from typing import Dict

from src.shared.base import Base

class Contact(Base):
    """
    Model representing a contact person at a company.
    """
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)  # (RELATIONSHIP) foreign key to company
    name = Column(String(255), nullable=False)  # (MANUAL) contact person's name
    title = Column(String(255), nullable=True)  # (MANUAL) contact person's job title
    direct_number = Column(String(50), nullable=True)  # (MANUAL) direct phone number
    direct_email = Column(String(255), nullable=True)  # (MANUAL) direct email address
    notes = Column(Text, nullable=True)  # (MANUAL) additional notes about the contact
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) last update timestamp
    
    # Relationships
    company = relationship("Company", back_populates="contacts")
    
    # Critical indexes for production performance
    __table_args__ = (
        # Foreign key index for JOIN performance
        Index('idx_contacts_company_id', 'company_id'),
        # Composite index for common query patterns
        Index('idx_contacts_company_name', 'company_id', 'name'),
    )
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}', company_id={self.company_id})>"


    def get_field_classification(self) -> Dict[str, str]:
        """
        Field classification for the contact model.
        
        Returns:
            Dict[str, str]: Field classification for the contact model
        """
        return {
            'id': 'SYSTEM',
            'company_id': 'RELATIONSHIP',
            'name': 'MANUAL',
            'title': 'MANUAL',
            'direct_number': 'MANUAL',
            'direct_email': 'MANUAL',
            'notes': 'MANUAL',
            'created_at': 'SYSTEM',
            'updated_at': 'SYSTEM',
        }