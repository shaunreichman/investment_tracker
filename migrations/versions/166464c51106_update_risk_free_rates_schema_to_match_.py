"""update_risk_free_rates_schema_to_match_model

Revision ID: 166464c51106
Revises: 6fafcf6542e3
Create Date: 2025-09-26 19:38:12.006482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '166464c51106'
down_revision: Union[str, Sequence[str], None] = '6fafcf6542e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing values to existing currency enum
    op.execute("ALTER TYPE currency ADD VALUE 'CNY'")
    op.execute("ALTER TYPE currency ADD VALUE 'KRW'")
    
    # Create the risk_free_rate_type enum
    risk_free_rate_type_enum = sa.Enum('GOVERNMENT_BOND', 'LIBOR', 'SOFR', name='riskfreeratetype')
    risk_free_rate_type_enum.create(op.get_bind())
    
    # Drop the existing table and recreate with correct schema using raw SQL
    op.drop_table('risk_free_rates')
    
    # Create the new table with correct schema using raw SQL
    op.execute("""
        CREATE TABLE risk_free_rates (
            id SERIAL PRIMARY KEY,
            currency currency NOT NULL,
            date DATE NOT NULL,
            rate DOUBLE PRECISION NOT NULL,
            rate_type riskfreeratetype DEFAULT 'GOVERNMENT_BOND',
            source VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE,
            CONSTRAINT uq_risk_free_rate UNIQUE (currency, date, rate_type)
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the new table
    op.drop_table('risk_free_rates')
    
    # Recreate the old table structure
    op.create_table('risk_free_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('rate_date', sa.Date(), nullable=False),
        sa.Column('rate', sa.Float(), nullable=False),
        sa.Column('rate_type', sa.String(length=50), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('currency', 'rate_date', 'rate_type', name='uq_risk_free_rate')
    )
    
    # Drop the enum types
    sa.Enum(name='riskfreeratetype').drop(op.get_bind())
    sa.Enum(name='currency').drop(op.get_bind())
