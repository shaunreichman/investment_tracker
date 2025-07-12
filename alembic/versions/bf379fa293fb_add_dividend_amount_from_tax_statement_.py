"""Add dividend amount from tax statement flags

Revision ID: bf379fa293fb
Revises: 7761261ccf39
Create Date: 2024-12-19 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf379fa293fb'
down_revision = '7761261ccf39'
branch_labels = None
depends_on = None


def upgrade():
    # Add dividend amount from tax statement flags
    op.add_column('tax_statements', sa.Column('dividend_franked_income_amount_from_tax_statement_flag', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('tax_statements', sa.Column('dividend_unfranked_income_amount_from_tax_statement_flag', sa.Boolean(), nullable=True, server_default='false'))


def downgrade():
    # Remove the dividend flag columns
    op.drop_column('tax_statements', 'dividend_franked_income_amount_from_tax_statement_flag')
    op.drop_column('tax_statements', 'dividend_unfranked_income_amount_from_tax_statement_flag')
