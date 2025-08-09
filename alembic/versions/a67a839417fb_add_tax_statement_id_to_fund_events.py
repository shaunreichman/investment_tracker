"""add_tax_statement_id_to_fund_events

Revision ID: a67a839417fb
Revises: 0a4750fa04b2
Create Date: 2025-07-20 14:21:48.165175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a67a839417fb'
down_revision: Union[str, Sequence[str], None] = '0a4750fa04b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with SQLite-safe batch ops."""
    with op.batch_alter_table('fund_events') as batch_op:
        batch_op.add_column(sa.Column('tax_statement_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_fund_events_tax_statement_id'), ['tax_statement_id'], unique=False)
        # SQLite: skip explicit FK creation to avoid ALTER constraint limitations


def downgrade() -> None:
    """Downgrade schema with SQLite-safe batch ops."""
    with op.batch_alter_table('fund_events') as batch_op:
        batch_op.drop_index(batch_op.f('ix_fund_events_tax_statement_id'))
        batch_op.drop_column('tax_statement_id')
