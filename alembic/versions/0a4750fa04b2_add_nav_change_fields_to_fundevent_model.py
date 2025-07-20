"""Add NAV change fields to FundEvent model

Revision ID: 0a4750fa04b2
Revises: f223dde71466
Create Date: 2025-07-20 08:58:25.321681

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a4750fa04b2'
down_revision: Union[str, Sequence[str], None] = 'f223dde71466'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add NAV change fields to fund_events table
    op.add_column('fund_events', sa.Column('previous_nav_per_share', sa.Float(), nullable=True))
    op.add_column('fund_events', sa.Column('nav_change_absolute', sa.Float(), nullable=True))
    op.add_column('fund_events', sa.Column('nav_change_percentage', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove NAV change fields from fund_events table
    op.drop_column('fund_events', 'nav_change_percentage')
    op.drop_column('fund_events', 'nav_change_absolute')
    op.drop_column('fund_events', 'previous_nav_per_share')
