"""add_companies_ui_phase1_fields

Revision ID: 3ec332eaed3e
Revises: add_has_withholding_tax
Create Date: 2025-08-10 19:54:42.282639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ec332eaed3e'
down_revision: Union[str, Sequence[str], None] = 'add_has_withholding_tax'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new fields to investment_companies table
    op.add_column('investment_companies', sa.Column('company_type', sa.String(100), nullable=True))
    op.add_column('investment_companies', sa.Column('business_address', sa.Text(), nullable=True))
    
    # Create contacts table
    op.create_table('contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('investment_company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('direct_number', sa.String(50), nullable=True),
        sa.Column('direct_email', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['investment_company_id'], ['investment_companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop contacts table
    op.drop_table('contacts')
    
    # Remove columns from investment_companies table
    op.drop_column('investment_companies', 'business_address')
    op.drop_column('investment_companies', 'company_type')
