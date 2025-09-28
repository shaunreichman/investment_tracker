"""update_entities_schema_to_match_model

Revision ID: db450f4a0850
Revises: 166464c51106
Create Date: 2025-09-26 19:46:47.216738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db450f4a0850'
down_revision: Union[str, Sequence[str], None] = '166464c51106'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the entity_type enum
    entity_type_enum = sa.Enum('PERSON', 'COMPANY', 'TRUST', 'FUND', 'OTHER', name='entitytype')
    entity_type_enum.create(op.get_bind())
    
    # Drop the existing entities table and recreate with correct schema (CASCADE to handle foreign keys)
    op.execute("DROP TABLE entities CASCADE")
    
    # Create the new entities table with correct schema using raw SQL
    op.execute("""
        CREATE TABLE entities (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            entity_type entitytype NOT NULL,
            description TEXT,
            tax_jurisdiction country DEFAULT 'AU' NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the new table
    op.drop_table('entities')
    
    # Recreate the old table structure
    op.create_table('entities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tax_jurisdiction', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Drop the enum type
    sa.Enum(name='entitytype').drop(op.get_bind())
