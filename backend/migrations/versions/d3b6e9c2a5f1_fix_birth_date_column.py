"""Fix birth_date column - add if missing

Revision ID: d3b6e9c2a5f1
Revises: c2a5f8e9b1d2
Create Date: 2025-05-30 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3b6e9c2a5f1'
down_revision = 'c2a5f8e9b1d2'
branch_labels = None
depends_on = None


def upgrade():
    # Add birth_date column if it doesn't exist
    op.add_column('users', sa.Column('birth_date', sa.String(length=10), nullable=True))


def downgrade():
    op.drop_column('users', 'birth_date')
