"""update_banking_schema_to_match_models

Revision ID: f1653be3687d
Revises: db450f4a0850
Create Date: 2025-09-26 19:51:05.146550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1653be3687d'
down_revision: Union[str, Sequence[str], None] = 'db450f4a0850'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the new enum types
    bank_type_enum = sa.Enum('COMMERCIAL', 'INVESTMENT', 'CENTRAL', 'COOPERATIVE', 'DIGITAL', name='banktype')
    bank_type_enum.create(op.get_bind())
    
    bank_status_enum = sa.Enum('ACTIVE', 'INACTIVE', 'CLOSED', name='bankstatus')
    bank_status_enum.create(op.get_bind())
    
    bank_account_type_enum = sa.Enum('CHECKING', 'SAVINGS', 'INVESTMENT', 'BUSINESS', 'TRUST', 'JOINT', name='bankaccounttype')
    bank_account_type_enum.create(op.get_bind())
    
    bank_account_status_enum = sa.Enum('ACTIVE', 'INACTIVE', 'CLOSED', 'SUSPENDED', 'OVERDRAFT', name='bankaccountstatus')
    bank_account_status_enum.create(op.get_bind())
    
    # Drop existing tables and recreate with correct schema using raw SQL
    op.execute("DROP TABLE bank_accounts CASCADE")
    op.execute("DROP TABLE banks CASCADE")
    
    # Create the new banks table with correct schema
    op.execute("""
        CREATE TABLE banks (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            country country NOT NULL,
            bank_type banktype,
            swift_bic VARCHAR(11),
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE,
            status bankstatus,
            current_number_of_bank_accounts INTEGER DEFAULT 0,
            current_balance_in_bank_accounts DOUBLE PRECISION DEFAULT 0.0
        )
    """)
    
    # Create the new bank_accounts table with correct schema
    op.execute("""
        CREATE TABLE bank_accounts (
            id SERIAL PRIMARY KEY,
            entity_id INTEGER NOT NULL,
            bank_id INTEGER NOT NULL,
            account_name VARCHAR(255) NOT NULL,
            account_number VARCHAR(64) NOT NULL,
            currency currency NOT NULL,
            account_type bankaccounttype NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE,
            status bankaccountstatus,
            current_balance DOUBLE PRECISION DEFAULT 0.0,
            CONSTRAINT bank_accounts_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES entities(id),
            CONSTRAINT bank_accounts_bank_id_fkey FOREIGN KEY (bank_id) REFERENCES banks(id),
            CONSTRAINT uq_bank_account_unique UNIQUE (entity_id, bank_id, account_number),
            CONSTRAINT uq_bank_account_number_unique UNIQUE (bank_id, account_number)
        )
    """)
    
    # Create indexes
    op.execute("CREATE INDEX ix_bank_accounts_entity_id ON bank_accounts (entity_id)")
    op.execute("CREATE INDEX ix_bank_accounts_bank_id ON bank_accounts (bank_id)")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the new tables
    op.execute("DROP TABLE bank_accounts CASCADE")
    op.execute("DROP TABLE banks CASCADE")
    
    # Recreate the old table structures
    op.create_table('banks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('country', sa.Enum('AU', 'US', 'UK', 'CA', 'NZ', 'SG', 'HK', 'JP', 'DE', 'FR', name='country'), nullable=False),
        sa.Column('swift_bic', sa.String(length=11), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('bank_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('bank_id', sa.Integer(), nullable=False),
        sa.Column('account_name', sa.String(length=255), nullable=False),
        sa.Column('account_number', sa.String(length=64), nullable=False),
        sa.Column('currency', sa.Enum('AUD', 'USD', 'EUR', 'GBP', 'CAD', 'NZD', 'SGD', 'HKD', 'JPY', 'CHF', name='currency'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'SUSPENDED', 'CLOSED', 'PENDING_VERIFICATION', 'RESTRICTED', name='accountstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bank_id'], ['banks.id']),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bank_id', 'account_number', name='uq_bank_account_number_unique'),
        sa.UniqueConstraint('entity_id', 'bank_id', 'account_number', name='uq_bank_account_unique')
    )
    
    # Drop the new enum types
    sa.Enum(name='bankaccountstatus').drop(op.get_bind())
    sa.Enum(name='bankaccounttype').drop(op.get_bind())
    sa.Enum(name='bankstatus').drop(op.get_bind())
    sa.Enum(name='banktype').drop(op.get_bind())
