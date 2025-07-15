"""Remove tax_already_paid field

Revision ID: 27f064a83d4d
Revises: 72b17b2c3309
Create Date: 2025-07-12 16:32:17.389936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27f064a83d4d'
down_revision: Union[str, Sequence[str], None] = '72b17b2c3309'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove tax_already_paid column
    op.drop_column('tax_statements', 'tax_already_paid')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back tax_already_paid column
    op.add_column('tax_statements', sa.Column('tax_already_paid', sa.Float(), nullable=True))
