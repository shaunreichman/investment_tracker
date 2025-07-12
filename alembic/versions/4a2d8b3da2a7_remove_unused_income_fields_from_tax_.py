"""Remove unused income fields from tax statements

Revision ID: 4a2d8b3da2a7
Revises: 27f064a83d4d
Create Date: 2025-07-12 16:44:55.554625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a2d8b3da2a7'
down_revision: Union[str, Sequence[str], None] = '27f064a83d4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop unused income fields from tax_statements table
    op.drop_column('tax_statements', 'foreign_income')
    op.drop_column('tax_statements', 'capital_gains')
    op.drop_column('tax_statements', 'other_income')
    op.drop_column('tax_statements', 'total_income')
    op.drop_column('tax_statements', 'foreign_tax_credits')


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add the dropped columns
    op.add_column('tax_statements', sa.Column('foreign_income', sa.Float(), nullable=True))
    op.add_column('tax_statements', sa.Column('capital_gains', sa.Float(), nullable=True))
    op.add_column('tax_statements', sa.Column('other_income', sa.Float(), nullable=True))
    op.add_column('tax_statements', sa.Column('total_income', sa.Float(), nullable=True))
    op.add_column('tax_statements', sa.Column('foreign_tax_credits', sa.Float(), nullable=True))
