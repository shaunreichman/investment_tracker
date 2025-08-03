"""add_end_date_to_funds

Revision ID: 762e1a853f03
Revises: dec654353eed
Create Date: 2025-08-03 11:38:33.536152

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '762e1a853f03'
down_revision: Union[str, Sequence[str], None] = 'dec654353eed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add end_date column to funds table
    op.add_column('funds', sa.Column('end_date', sa.Date(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove end_date column from funds table
    op.drop_column('funds', 'end_date')
