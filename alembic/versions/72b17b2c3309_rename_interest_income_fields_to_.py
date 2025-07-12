"""Rename interest income fields to consistent naming pattern

Revision ID: 72b17b2c3309
Revises: 39973e45f047
Create Date: 2025-07-12 16:14:11.565164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72b17b2c3309'
down_revision: Union[str, Sequence[str], None] = '39973e45f047'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename interest income fields to consistent naming pattern
    op.alter_column('tax_statements', 'distribution_receivable_this_fy', new_column_name='interest_receivable_this_fy')
    op.alter_column('tax_statements', 'distribution_received_prev_fy', new_column_name='interest_receivable_prev_fy')
    op.alter_column('tax_statements', 'non_resident_withholding_tax_from_statement', new_column_name='interest_non_resident_withholding_tax_from_statement')
    op.alter_column('tax_statements', 'interest_taxable_rate', new_column_name='interest_income_tax_rate')
    op.alter_column('tax_statements', 'total_interest_income', new_column_name='interest_income_amount')
    op.alter_column('tax_statements', 'non_resident_withholding_tax_already_withheld', new_column_name='interest_non_resident_withholding_tax_already_withheld')
    op.alter_column('tax_statements', 'tax_payable', new_column_name='interest_income_tax_amount')


def downgrade() -> None:
    """Downgrade schema."""
    # Revert interest income field renames
    op.alter_column('tax_statements', 'interest_receivable_this_fy', new_column_name='distribution_receivable_this_fy')
    op.alter_column('tax_statements', 'interest_receivable_prev_fy', new_column_name='distribution_received_prev_fy')
    op.alter_column('tax_statements', 'interest_non_resident_withholding_tax_from_statement', new_column_name='non_resident_withholding_tax_from_statement')
    op.alter_column('tax_statements', 'interest_income_tax_rate', new_column_name='interest_taxable_rate')
    op.alter_column('tax_statements', 'interest_income_amount', new_column_name='total_interest_income')
    op.alter_column('tax_statements', 'interest_non_resident_withholding_tax_already_withheld', new_column_name='non_resident_withholding_tax_already_withheld')
    op.alter_column('tax_statements', 'interest_income_tax_amount', new_column_name='tax_payable')
