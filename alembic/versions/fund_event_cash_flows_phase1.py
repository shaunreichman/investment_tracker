"""Phase 1: banking models, cash flow model, event enum trims, completion flag

Revision ID: fcf_phase1
Revises: dec654353eed
Create Date: 2025-08-09
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fcf_phase1'
down_revision = 'dec654353eed'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create banks
    op.create_table(
        'banks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('country', sa.String(length=2), nullable=False),
        sa.Column('swift_bic', sa.String(length=11), nullable=True),
    )

    # Create bank_accounts with uniqueness
    op.create_table(
        'bank_accounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('entity_id', sa.Integer(), sa.ForeignKey('entities.id'), nullable=False),
        sa.Column('bank_id', sa.Integer(), sa.ForeignKey('banks.id'), nullable=False),
        sa.Column('account_name', sa.String(length=255), nullable=False),
        sa.Column('account_number', sa.String(length=64), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.UniqueConstraint('entity_id', 'bank_id', 'account_number', name='uq_bank_account_unique'),
    )
    op.create_index(op.f('ix_bank_accounts_entity_id'), 'bank_accounts', ['entity_id'], unique=False)
    op.create_index(op.f('ix_bank_accounts_bank_id'), 'bank_accounts', ['bank_id'], unique=False)

    # Add is_cash_flow_complete to fund_events
    op.add_column('fund_events', sa.Column('is_cash_flow_complete', sa.Boolean(), nullable=False, server_default=sa.text('0')))

    # Create fund_event_cash_flows
    op.create_table(
        'fund_event_cash_flows',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('fund_event_id', sa.Integer(), sa.ForeignKey('fund_events.id'), nullable=False),
        sa.Column('bank_account_id', sa.Integer(), sa.ForeignKey('bank_accounts.id'), nullable=False),
        sa.Column('direction', sa.String(length=16), nullable=False),  # store enum as string
        sa.Column('transfer_date', sa.Date(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('reference', sa.String(length=255)),
        sa.Column('notes', sa.Text()),
    )
    op.create_index(op.f('ix_fecf_fund_event_id'), 'fund_event_cash_flows', ['fund_event_id'], unique=False)
    op.create_index(op.f('ix_fecf_bank_account_id'), 'fund_event_cash_flows', ['bank_account_id'], unique=False)
    op.create_index(op.f('ix_fecf_transfer_date'), 'fund_event_cash_flows', ['transfer_date'], unique=False)

    # NOTE: Trimming EventType enum (MANAGEMENT_FEE, CARRIED_INTEREST, OTHER) requires care per dialect.
    # For SQLite tests we rely on code-level enum change; for production enums (e.g., Postgres), add explicit ALTER TYPE here.


def downgrade() -> None:
    op.drop_index(op.f('ix_fecf_transfer_date'), table_name='fund_event_cash_flows')
    op.drop_index(op.f('ix_fecf_bank_account_id'), table_name='fund_event_cash_flows')
    op.drop_index(op.f('ix_fecf_fund_event_id'), table_name='fund_event_cash_flows')
    op.drop_table('fund_event_cash_flows')

    op.drop_column('fund_events', 'is_cash_flow_complete')

    op.drop_index(op.f('ix_bank_accounts_bank_id'), table_name='bank_accounts')
    op.drop_index(op.f('ix_bank_accounts_entity_id'), table_name='bank_accounts')
    op.drop_table('bank_accounts')

    op.drop_table('banks')



