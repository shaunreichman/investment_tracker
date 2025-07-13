"""Merge heads after dropping cost_of_units column

Revision ID: 1a9fb49d4218
Revises: add_current_equity_balance_to_fundevent, drop_cost_of_units_from_fund_events
Create Date: 2025-07-13 21:00:47.771851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a9fb49d4218'
down_revision: Union[str, Sequence[str], None] = ('add_current_equity_balance_to_fundevent', 'drop_cost_of_units_from_fund_events')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
