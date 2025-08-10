"""merge_heads_before_adding_suspended_status

Revision ID: 25fb36d72ca1
Revises: 3ec332eaed3e, d1ac42f5994a
Create Date: 2025-08-11 02:44:13.183161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25fb36d72ca1'
down_revision: Union[str, Sequence[str], None] = ('3ec332eaed3e', 'd1ac42f5994a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
