"""Rename debt cost tracking fields to be clearer

Revision ID: e6b544621144
Revises: 23f450329111
Create Date: 2024-12-19 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6b544621144'
down_revision = '23f450329111'
branch_labels = None
depends_on = None


def upgrade():
    # Rename debt cost tracking fields to be clearer
    op.alter_column('tax_statements', 'total_interest_expense', new_column_name='fy_debt_interest_deduction_sum_of_daily_interest')
    op.alter_column('tax_statements', 'interest_deduction_rate', new_column_name='fy_debt_interest_deduction_rate')
    op.alter_column('tax_statements', 'interest_tax_benefit', new_column_name='fy_debt_interest_deduction_total_deduction')


def downgrade():
    # Revert the column renames
    op.alter_column('tax_statements', 'fy_debt_interest_deduction_sum_of_daily_interest', new_column_name='total_interest_expense')
    op.alter_column('tax_statements', 'fy_debt_interest_deduction_rate', new_column_name='interest_deduction_rate')
    op.alter_column('tax_statements', 'fy_debt_interest_deduction_total_deduction', new_column_name='interest_tax_benefit')
