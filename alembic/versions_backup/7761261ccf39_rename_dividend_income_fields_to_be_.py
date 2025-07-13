"""Rename dividend income fields to be clearer

Revision ID: 7761261ccf39
Revises: e6b544621144
Create Date: 2024-12-19 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7761261ccf39'
down_revision: Union[str, Sequence[str], None] = 'e6b544621144'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename dividend income fields to be clearer
    op.alter_column('tax_statements', 'total_dividends_franked', new_column_name='dividend_franked_income_amount')
    op.alter_column('tax_statements', 'total_dividends_unfranked', new_column_name='dividend_unfranked_income_amount')
    op.alter_column('tax_statements', 'dividends_franked_taxable_rate', new_column_name='dividend_franked_income_tax_rate')
    op.alter_column('tax_statements', 'dividends_unfranked_taxable_rate', new_column_name='dividend_unfranked_income_tax_rate')


def downgrade() -> None:
    """Downgrade schema."""
    # Revert the column renames
    op.alter_column('tax_statements', 'dividend_franked_income_amount', new_column_name='total_dividends_franked')
    op.alter_column('tax_statements', 'dividend_unfranked_income_amount', new_column_name='total_dividends_unfranked')
    op.alter_column('tax_statements', 'dividend_franked_income_tax_rate', new_column_name='dividends_franked_taxable_rate')
    op.alter_column('tax_statements', 'dividend_unfranked_income_tax_rate', new_column_name='dividends_unfranked_taxable_rate')
