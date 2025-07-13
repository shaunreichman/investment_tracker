"""
Drop cost_of_units from fund_events (unified with current_equity_balance)
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'drop_cost_of_units_from_fund_events'
down_revision = None  # Set this to the latest revision in your migrations
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('fund_events', 'cost_of_units')

def downgrade():
    op.add_column('fund_events', sa.Column('cost_of_units', sa.Float(), nullable=True)) 