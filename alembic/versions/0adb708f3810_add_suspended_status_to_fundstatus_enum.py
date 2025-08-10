"""add_suspended_status_to_fundstatus_enum

Revision ID: 0adb708f3810
Revises: 25fb36d72ca1
Create Date: 2025-08-11 02:44:18.508476

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0adb708f3810'
down_revision: Union[str, Sequence[str], None] = '25fb36d72ca1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add SUSPENDED status to the fundstatus enum
    op.execute("ALTER TYPE fundstatus ADD VALUE 'SUSPENDED'")

def downgrade() -> None:
    """Downgrade schema."""
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type, which is complex
    # For now, we'll leave the SUSPENDED value in place
    pass
