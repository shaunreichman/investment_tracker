"""add_capital_gain_discount_applicable_flag_and_remove_non_resident_from_fund_tax_statement

Revision ID: d93de0407550
Revises: 361c8101e3d9
Create Date: 2025-10-04 13:39:38.334047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd93de0407550'
down_revision: Union[str, Sequence[str], None] = '361c8101e3d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add capital_gain_discount_applicable_flag column to fund_tax_statements table
    op.add_column('fund_tax_statements', sa.Column('capital_gain_discount_applicable_flag', sa.Boolean(), nullable=True, server_default='true'))
    
    # Remove the old non_resident column from fund_tax_statements table
    op.drop_column('fund_tax_statements', 'non_resident')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the non_resident column
    op.add_column('fund_tax_statements', sa.Column('non_resident', sa.Boolean(), nullable=True))
    
    # Remove capital_gain_discount_applicable_flag column from fund_tax_statements table
    op.drop_column('fund_tax_statements', 'capital_gain_discount_applicable_flag')
