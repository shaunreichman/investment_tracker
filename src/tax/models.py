"""
Tax domain models.

This module contains the core tax models including TaxStatement.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

# Import the Base from shared
from ..shared.base import Base


class TaxStatement(Base):
    """Model representing a tax statement for a fund/entity/financial year.
    
    Relationships:
    - fund: The fund this tax statement relates to.
    - entity: The entity this tax statement relates to.
    
    Business rules:
    - Each fund/entity/financial year combination can have one tax statement.
    - Tax statements are used for reconciliation with fund distributions.
    - Manual fields are entered from tax documents, calculated fields are computed.
    """
    __tablename__ = 'tax_statements'
    
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False, index=True)
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False, index=True)
    financial_year = Column(String(10), nullable=False, index=True)  # e.g., '2022-23'
    
    # Manual fields (from tax statement)
    manual_gross_interest = Column(Float, default=0.0)  # Gross interest from tax statement
    manual_net_interest = Column(Float, default=0.0)    # Net interest from tax statement
    manual_tax_withheld = Column(Float, default=0.0)    # Tax withheld from tax statement
    
    # Calculated fields (from fund events)
    calculated_gross_interest = Column(Float, default=0.0)  # Calculated from fund distributions
    calculated_net_interest = Column(Float, default=0.0)    # Calculated from fund distributions
    calculated_tax_withheld = Column(Float, default=0.0)    # Calculated from fund tax payments
    
    # Reconciliation fields
    gross_difference = Column(Float, default=0.0)  # manual_gross - calculated_gross
    net_difference = Column(Float, default=0.0)    # manual_net - calculated_net
    tax_difference = Column(Float, default=0.0)    # manual_tax - calculated_tax
    
    # Metadata
    statement_received_date = Column(Date)  # When the tax statement was received
    notes = Column(Text)  # Additional notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fund = relationship("Fund", back_populates="tax_statements", lazy='selectin')
    entity = relationship("Entity", lazy='selectin')
    
    def __repr__(self):
        """Return a string representation of the TaxStatement instance for debugging/logging."""
        return f"<TaxStatement(id={self.id}, fund_id={self.fund_id}, entity_id={self.entity_id}, fy='{self.financial_year}')>"
    
    @property
    def is_reconciled(self):
        """Check if the tax statement is reconciled (differences are small)."""
        return (abs(self.gross_difference) < 0.01 and 
                abs(self.net_difference) < 0.01 and 
                abs(self.tax_difference) < 0.01)
    
    def calculate_reconciliation_differences(self):
        """Calculate the differences between manual and calculated fields."""
        self.gross_difference = self.manual_gross_interest - self.calculated_gross_interest
        self.net_difference = self.manual_net_interest - self.calculated_net_interest
        self.tax_difference = self.manual_tax_withheld - self.calculated_tax_withheld
    
    def get_reconciliation_summary(self):
        """Get a summary of the reconciliation status."""
        from ..shared.calculations import get_reconciliation_explanation
        
        return {
            'is_reconciled': self.is_reconciled,
            'gross_difference': self.gross_difference,
            'net_difference': self.net_difference,
            'tax_difference': self.tax_difference,
            'explanation': get_reconciliation_explanation(
                self.gross_difference, 
                self.tax_difference, 
                self.net_difference
            )
        } 