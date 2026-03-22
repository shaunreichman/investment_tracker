"""add_missing_fund_event_cash_flow_columns

Revision ID: 3b52d887d1a2
Revises: 0c2a69462ef0
Create Date: 2026-01-23 15:19:10.127864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b52d887d1a2'
down_revision: Union[str, Sequence[str], None] = '0c2a69462ef0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add missing columns to fund_event_cash_flows table."""
    
    # Step 1: Add columns as nullable first (so we can populate existing data)
    op.add_column('fund_event_cash_flows', sa.Column('fund_event_date', sa.Date(), nullable=True))
    op.add_column('fund_event_cash_flows', sa.Column('different_month', sa.Boolean(), nullable=True))
    op.add_column('fund_event_cash_flows', sa.Column('adjusted_bank_account_balance_id', sa.Integer(), nullable=True))
    
    # Step 2: Populate fund_event_date from related fund_events
    op.execute("""
        UPDATE fund_event_cash_flows
        SET fund_event_date = fund_events.event_date
        FROM fund_events
        WHERE fund_event_cash_flows.fund_event_id = fund_events.id
    """)
    
    # Step 3: Populate different_month based on transfer_date and fund_event_date
    op.execute("""
        UPDATE fund_event_cash_flows
        SET different_month = (
            EXTRACT(MONTH FROM transfer_date) != EXTRACT(MONTH FROM fund_event_date)
            OR EXTRACT(YEAR FROM transfer_date) != EXTRACT(YEAR FROM fund_event_date)
        )
        WHERE fund_event_date IS NOT NULL
    """)
    
    # Step 4: Set default for different_month where it's still NULL (shouldn't happen, but safety)
    op.execute("""
        UPDATE fund_event_cash_flows
        SET different_month = FALSE
        WHERE different_month IS NULL
    """)
    
    # Step 5: Make fund_event_date NOT NULL (now that all rows are populated)
    op.alter_column('fund_event_cash_flows', 'fund_event_date', nullable=False)
    
    # Step 6: Make different_month NOT NULL with default
    op.alter_column('fund_event_cash_flows', 'different_month', nullable=False, server_default='false')
    
    # Step 7: Create index for adjusted_bank_account_balance_id
    op.create_index(
        'ix_fund_event_cash_flows_adjusted_bank_account_balance_id',
        'fund_event_cash_flows',
        ['adjusted_bank_account_balance_id'],
        unique=False
    )
    
    # Step 8: Create foreign key constraint for adjusted_bank_account_balance_id (only if table exists)
    # Check if bank_account_balances table exists before creating foreign key
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'bank_account_balances'
        )
    """))
    table_exists = result.scalar()
    
    if table_exists:
        op.create_foreign_key(
            'fund_event_cash_flows_adjusted_bank_account_balance_id_fkey',
            'fund_event_cash_flows',
            'bank_account_balances',
            ['adjusted_bank_account_balance_id'],
            ['id']
        )


def downgrade() -> None:
    """Downgrade schema: Remove columns from fund_event_cash_flows table."""
    
    # Step 1: Drop foreign key constraint (if it exists)
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.table_constraints 
            WHERE constraint_schema = 'public' 
            AND constraint_name = 'fund_event_cash_flows_adjusted_bank_account_balance_id_fkey'
        )
    """))
    constraint_exists = result.scalar()
    
    if constraint_exists:
        op.drop_constraint('fund_event_cash_flows_adjusted_bank_account_balance_id_fkey', 'fund_event_cash_flows', type_='foreignkey')
    
    # Step 2: Drop index
    op.drop_index('ix_fund_event_cash_flows_adjusted_bank_account_balance_id', table_name='fund_event_cash_flows')
    
    # Step 3: Drop columns
    op.drop_column('fund_event_cash_flows', 'adjusted_bank_account_balance_id')
    op.drop_column('fund_event_cash_flows', 'different_month')
    op.drop_column('fund_event_cash_flows', 'fund_event_date')
