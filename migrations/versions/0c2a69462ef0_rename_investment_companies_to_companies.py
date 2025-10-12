"""rename_investment_companies_to_companies

Revision ID: 0c2a69462ef0
Revises: fe1b56aa9852
Create Date: 2025-10-09 12:13:18.462714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c2a69462ef0'
down_revision: Union[str, Sequence[str], None] = 'fe1b56aa9852'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Rename investment_companies to companies and update all references."""
    
    # Step 1: Drop foreign key constraints that reference investment_companies
    op.drop_constraint('funds_investment_company_id_fkey', 'funds', type_='foreignkey')
    op.drop_constraint('contacts_investment_company_id_fkey', 'contacts', type_='foreignkey')
    
    # Step 2: Drop indexes on investment_companies table (will be recreated with new names)
    op.drop_index('idx_investment_companies_type_status', table_name='investment_companies')
    op.drop_index('idx_investment_companies_status', table_name='investment_companies')
    op.drop_index('idx_investment_companies_name_status', table_name='investment_companies')
    op.drop_index('idx_investment_companies_company_type', table_name='investment_companies')
    
    # Step 3: Drop indexes on contacts table that reference investment_company_id
    op.drop_index('idx_contacts_company_name', table_name='contacts')
    op.drop_index('idx_contacts_investment_company_id', table_name='contacts')
    
    # Step 4: Drop indexes on funds table that reference investment_company_id
    op.drop_index('idx_funds_investment_company_id', table_name='funds')
    
    # Step 5: Rename the table
    op.rename_table('investment_companies', 'companies')
    
    # Step 6: Rename foreign key columns
    op.alter_column('contacts', 'investment_company_id', new_column_name='company_id')
    op.alter_column('funds', 'investment_company_id', new_column_name='company_id')
    
    # Step 7: Recreate indexes on companies table with new names
    op.create_index('idx_companies_company_type', 'companies', ['company_type'], unique=False)
    op.create_index('idx_companies_status', 'companies', ['status'], unique=False)
    op.create_index('idx_companies_type_status', 'companies', ['company_type', 'status'], unique=False)
    op.create_index('idx_companies_name_status', 'companies', ['name', 'status'], unique=False)
    
    # Step 8: Recreate indexes on contacts table with new column name
    op.create_index('idx_contacts_company_id', 'contacts', ['company_id'], unique=False)
    op.create_index('idx_contacts_company_name', 'contacts', ['company_id', 'name'], unique=False)
    
    # Step 9: Recreate indexes on funds table with new column name
    op.create_index('idx_funds_company_id', 'funds', ['company_id'], unique=False)
    
    # Step 10: Recreate foreign key constraints with new names
    op.create_foreign_key('funds_company_id_fkey', 'funds', 'companies', ['company_id'], ['id'])
    op.create_foreign_key('contacts_company_id_fkey', 'contacts', 'companies', ['company_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema: Revert companies back to investment_companies."""
    
    # Step 1: Drop foreign key constraints
    op.drop_constraint('contacts_company_id_fkey', 'contacts', type_='foreignkey')
    op.drop_constraint('funds_company_id_fkey', 'funds', type_='foreignkey')
    
    # Step 2: Drop indexes on companies table
    op.drop_index('idx_companies_name_status', table_name='companies')
    op.drop_index('idx_companies_type_status', table_name='companies')
    op.drop_index('idx_companies_status', table_name='companies')
    op.drop_index('idx_companies_company_type', table_name='companies')
    
    # Step 3: Drop indexes on contacts table
    op.drop_index('idx_contacts_company_name', table_name='contacts')
    op.drop_index('idx_contacts_company_id', table_name='contacts')
    
    # Step 4: Drop indexes on funds table
    op.drop_index('idx_funds_company_id', table_name='funds')
    
    # Step 5: Rename the table back
    op.rename_table('companies', 'investment_companies')
    
    # Step 6: Rename foreign key columns back
    op.alter_column('contacts', 'company_id', new_column_name='investment_company_id')
    op.alter_column('funds', 'company_id', new_column_name='investment_company_id')
    
    # Step 7: Recreate original indexes on investment_companies table
    op.create_index('idx_investment_companies_company_type', 'investment_companies', ['company_type'], unique=False)
    op.create_index('idx_investment_companies_status', 'investment_companies', ['status'], unique=False)
    op.create_index('idx_investment_companies_type_status', 'investment_companies', ['company_type', 'status'], unique=False)
    op.create_index('idx_investment_companies_name_status', 'investment_companies', ['name', 'status'], unique=False)
    
    # Step 8: Recreate original indexes on contacts table
    op.create_index('idx_contacts_investment_company_id', 'contacts', ['investment_company_id'], unique=False)
    op.create_index('idx_contacts_company_name', 'contacts', ['investment_company_id', 'name'], unique=False)
    
    # Step 9: Recreate original indexes on funds table
    op.create_index('idx_funds_investment_company_id', 'funds', ['investment_company_id'], unique=False)
    
    # Step 10: Recreate original foreign key constraints
    op.create_foreign_key('funds_investment_company_id_fkey', 'funds', 'investment_companies', ['investment_company_id'], ['id'])
    op.create_foreign_key('contacts_investment_company_id_fkey', 'contacts', 'investment_companies', ['investment_company_id'], ['id'])
