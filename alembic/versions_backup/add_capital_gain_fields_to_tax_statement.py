"""Add capital gain fields to tax statement

Revision ID: add_capital_gain_fields_to_tax_statement
Revises: e6b544621144
Create Date: 2025-01-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_capital_gain_fields_to_tax_statement'
down_revision = 'aa30bbb41a7e'
branch_labels = None
depends_on = None


def upgrade():
    # Add capital gain fields to tax_statements table
    op.add_column('tax_statements', sa.Column('capital_gain_income_amount', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('tax_statements', sa.Column('capital_gain_income_tax_rate', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('tax_statements', sa.Column('capital_gain_tax_amount', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('tax_statements', sa.Column('capital_gain_discount_amount', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('tax_statements', sa.Column('capital_gain_income_amount_from_tax_statement_flag', sa.Boolean(), nullable=True, server_default='false'))


def downgrade():
    # Remove capital gain fields from tax_statements table
    op.drop_column('tax_statements', 'capital_gain_income_amount_from_tax_statement_flag')
    op.drop_column('tax_statements', 'capital_gain_discount_amount')
    op.drop_column('tax_statements', 'capital_gain_tax_amount')
    op.drop_column('tax_statements', 'capital_gain_income_tax_rate')
    op.drop_column('tax_statements', 'capital_gain_income_amount') 