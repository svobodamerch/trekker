"""Add user profile fields gender birth_date onboarding

Revision ID: c2a5f8e9b1d2
Revises: b1c5d8e9f2a4
Create Date: 2025-05-30 21:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'c2a5f8e9b1d2'
down_revision = 'b1c5d8e9f2a4'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if column exists in table."""
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)


def upgrade():
    # Add gender column if not exists
    if not column_exists('users', 'gender'):
        op.add_column('users', sa.Column('gender', sa.String(length=20), nullable=True))
    # Add birth_date column if not exists
    if not column_exists('users', 'birth_date'):
        op.add_column('users', sa.Column('birth_date', sa.String(length=10), nullable=True))
    # Add onboarding_completed column if not exists
    if not column_exists('users', 'onboarding_completed'):
        op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    if column_exists('users', 'onboarding_completed'):
        op.drop_column('users', 'onboarding_completed')
    if column_exists('users', 'birth_date'):
        op.drop_column('users', 'birth_date')
    if column_exists('users', 'gender'):
        op.drop_column('users', 'gender')
