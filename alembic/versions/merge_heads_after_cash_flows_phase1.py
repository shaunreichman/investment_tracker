"""Merge heads after cash flows phase 1

Revision ID: merge_fcf_heads
Revises: 0e0cbd0e843f, 932568d88bfa, fcf_phase1
Create Date: 2025-08-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'merge_fcf_heads'
down_revision: Union[str, Sequence[str], None] = ('0e0cbd0e843f', '932568d88bfa', 'fcf_phase1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


