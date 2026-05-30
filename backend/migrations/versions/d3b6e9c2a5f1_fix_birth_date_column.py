"""Fix birth_date column - add if missing

Revision ID: d3b6e9c2a5f1
Revises: c2a5f8e9b1d2
Create Date: 2025-05-30 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'd3b6e9c2a5f1'
down_revision = 'c2a5f8e9b1d2'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if column exists in table."""
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)


def upgrade():
    # Add birth_date column only if it doesn't exist
    if not column_exists('users', 'birth_date'):
        op.add_column('users', sa.Column('birth_date', sa.String(length=10), nullable=True))


def downgrade():
    # Only drop if exists
    if column_exists('users', 'birth_date'):
        op.drop_column('users', 'birth_date')
