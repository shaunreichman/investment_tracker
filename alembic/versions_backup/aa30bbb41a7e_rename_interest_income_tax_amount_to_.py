"""Rename interest_income_tax_amount to interest_tax_amount

Revision ID: aa30bbb41a7e
Revises: 4a2d8b3da2a7
Create Date: 2025-07-12 10:46:12.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'aa30bbb41a7e'
down_revision: Union[str, Sequence[str], None] = '4a2d8b3da2a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column('tax_statements', 'interest_income_tax_amount', new_column_name='interest_tax_amount')

def downgrade() -> None:
    op.alter_column('tax_statements', 'interest_tax_amount', new_column_name='interest_income_tax_amount')
