"""add current_equity_balance to FundEvent

Revision ID: add_current_equity_balance_to_fundevent
Revises: add_capital_gain_fields_to_tax_statement
Create Date: 2024-05-10

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_current_equity_balance_to_fundevent'
down_revision = 'add_capital_gain_fields_to_tax_statement'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('fund_events', sa.Column('current_equity_balance', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('fund_events', 'current_equity_balance') 