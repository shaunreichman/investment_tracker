"""Add group_id_seq sequence for event grouping

Revision ID: 6fafcf6542e3
Revises: 7a4b390f8d20
Create Date: 2025-09-06 18:09:18.836089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fafcf6542e3'
down_revision: Union[str, Sequence[str], None] = '7a4b390f8d20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create sequence for group IDs
    op.execute("CREATE SEQUENCE IF NOT EXISTS group_id_seq START WITH 1 INCREMENT BY 1")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the sequence
    op.execute("DROP SEQUENCE IF EXISTS group_id_seq")
