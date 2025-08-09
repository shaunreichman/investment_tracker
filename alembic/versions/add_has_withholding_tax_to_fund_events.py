"""Add has_withholding_tax to fund_events

Revision ID: add_has_withholding_tax
Revises: merge_fcf_heads
Create Date: 2025-08-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_has_withholding_tax'
down_revision: Union[str, Sequence[str], None] = 'merge_fcf_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """SQLite-safe add of has_withholding_tax to fund_events."""
    with op.batch_alter_table('fund_events') as batch_op:
        batch_op.add_column(sa.Column('has_withholding_tax', sa.Boolean(), nullable=False, server_default=sa.text('0')))


def downgrade() -> None:
    with op.batch_alter_table('fund_events') as batch_op:
        batch_op.drop_column('has_withholding_tax')


