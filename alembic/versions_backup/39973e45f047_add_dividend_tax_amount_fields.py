"""Add dividend tax amount fields

Revision ID: 39973e45f047
Revises: bf379fa293fb
Create Date: 2024-12-19 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39973e45f047'
down_revision = 'bf379fa293fb'
branch_labels = None
depends_on = None


def upgrade():
    # Add dividend tax amount fields
    op.add_column('tax_statements', sa.Column('dividend_franked_tax_amount', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('tax_statements', sa.Column('dividend_unfranked_tax_amount', sa.Float(), nullable=True, server_default='0.0'))


def downgrade():
    # Remove the dividend tax amount columns
    op.drop_column('tax_statements', 'dividend_franked_tax_amount')
    op.drop_column('tax_statements', 'dividend_unfranked_tax_amount')
