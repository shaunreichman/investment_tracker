"""add_current_nav_total_to_fund

Revision ID: 932568d88bfa
Revises: 762e1a853f03
Create Date: 2025-07-15 09:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '932568d88bfa'
down_revision: Union[str, Sequence[str], None] = '762e1a853f03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


