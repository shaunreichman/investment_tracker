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
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
