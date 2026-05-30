"""Add user profile fields gender birth_date onboarding

Revision ID: c2a5f8e9b1d2
Revises: b1c5d8e9f2a4
Create Date: 2025-05-30 21:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2a5f8e9b1d2'
down_revision = 'b1c5d8e9f2a4'
branch_labels = None
depends_on = None


def upgrade():
    # Add gender column
    op.add_column('users', sa.Column('gender', sa.String(length=20), nullable=True))
    # Add birth_date column (YYYY-MM-DD format)
    op.add_column('users', sa.Column('birth_date', sa.String(length=10), nullable=True))
    # Add onboarding_completed column
    op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('users', 'onboarding_completed')
    op.drop_column('users', 'birth_date')
    op.drop_column('users', 'gender')
