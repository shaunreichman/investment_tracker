"""add_dividend_fields_to_tax_statement

Revision ID: 23f450329111
Revises: 
Create Date: 2025-07-06 22:53:02.358394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23f450329111'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tax_statements', sa.Column('total_dividends_franked', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('tax_statements', sa.Column('total_dividends_unfranked', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('tax_statements', sa.Column('dividends_franked_taxable_rate', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('tax_statements', sa.Column('dividends_unfranked_taxable_rate', sa.Float(), nullable=True, server_default='0.0'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tax_statements', 'total_dividends_franked')
    op.drop_column('tax_statements', 'total_dividends_unfranked')
    op.drop_column('tax_statements', 'dividends_franked_taxable_rate')
    op.drop_column('tax_statements', 'dividends_unfranked_taxable_rate')
