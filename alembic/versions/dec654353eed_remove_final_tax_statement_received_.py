"""Remove final_tax_statement_received field

Revision ID: dec654353eed
Revises: 1267d9948898
Create Date: 2025-08-03 08:30:10.161678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dec654353eed'
down_revision: Union[str, Sequence[str], None] = '1267d9948898'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('funds', 'final_tax_statement_received')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('funds', sa.Column('final_tax_statement_received', sa.BOOLEAN(), nullable=True))
