"""add_cash_flow_balance_amount_to_fund_events

Revision ID: 361c8101e3d9
Revises: 767f21b3f548
Create Date: 2025-09-28 13:23:36.030532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '361c8101e3d9'
down_revision: Union[str, Sequence[str], None] = '767f21b3f548'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add cash_flow_balance_amount column to fund_events table
    op.add_column('fund_events', sa.Column('cash_flow_balance_amount', sa.Float(), nullable=False, server_default='0.0'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove cash_flow_balance_amount column from fund_events table
    op.drop_column('fund_events', 'cash_flow_balance_amount')
