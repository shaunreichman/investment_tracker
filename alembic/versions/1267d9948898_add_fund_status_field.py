"""Add fund status field

Revision ID: 1267d9948898
Revises: abb88ad11ad3
Create Date: 2025-08-03 08:21:16.499297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1267d9948898'
down_revision: Union[str, Sequence[str], None] = 'abb88ad11ad3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('funds', sa.Column('status', sa.Enum('ACTIVE', 'REALIZED', 'COMPLETED', name='fundstatus'), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('funds', 'status')
