"""
Contact Model.

This module provides the Contact model class for investment company contacts.
Contact is a pure data container with no business logic.
All business logic has been moved to dedicated services.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from src.shared.base import Base

class Contact(Base):
    """
    Model representing a contact person at an investment company.
    """
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    investment_company_id = Column(Integer, ForeignKey('investment_companies.id'), nullable=False)  # (SYSTEM) foreign key to investment company
    name = Column(String(255), nullable=False)  # (MANUAL) contact person's name
    title = Column(String(255), nullable=True)  # (MANUAL) contact person's job title
    direct_number = Column(String(50), nullable=True)  # (MANUAL) direct phone number
    direct_email = Column(String(255), nullable=True)  # (MANUAL) direct email address
    notes = Column(Text, nullable=True)  # (MANUAL) additional notes about the contact
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) last update timestamp
    
    # Relationships
    investment_company = relationship("InvestmentCompany", back_populates="contacts")
    
    # Critical indexes for production performance
    __table_args__ = (
        # Foreign key index for JOIN performance
        Index('idx_contacts_investment_company_id', 'investment_company_id'),
        # Composite index for common query patterns
        Index('idx_contacts_company_name', 'investment_company_id', 'name'),
    )
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}', company_id={self.investment_company_id})>"
