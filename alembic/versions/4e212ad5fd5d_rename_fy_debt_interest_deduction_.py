"""rename_fy_debt_interest_deduction_fields_to_eofy

Revision ID: 4e212ad5fd5d
Revises: a67a839417fb
Create Date: 2025-07-20 15:44:09.690724

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e212ad5fd5d'
down_revision: Union[str, Sequence[str], None] = 'a67a839417fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename fy_debt_interest_deduction fields to eofy_debt_interest_deduction
    op.alter_column('tax_statements', 'fy_debt_interest_deduction_sum_of_daily_interest', new_column_name='eofy_debt_interest_deduction_sum_of_daily_interest')
    op.alter_column('tax_statements', 'fy_debt_interest_deduction_rate', new_column_name='eofy_debt_interest_deduction_rate')
    op.alter_column('tax_statements', 'fy_debt_interest_deduction_total_deduction', new_column_name='eofy_debt_interest_deduction_total_deduction')


def downgrade() -> None:
    """Downgrade schema."""
    # Rename eofy_debt_interest_deduction fields back to fy_debt_interest_deduction
    op.alter_column('tax_statements', 'eofy_debt_interest_deduction_sum_of_daily_interest', new_column_name='fy_debt_interest_deduction_sum_of_daily_interest')
    op.alter_column('tax_statements', 'eofy_debt_interest_deduction_rate', new_column_name='fy_debt_interest_deduction_rate')
    op.alter_column('tax_statements', 'eofy_debt_interest_deduction_total_deduction', new_column_name='fy_debt_interest_deduction_total_deduction')
