"""Add daily ten goals table for Brian Tracy technique

Revision ID: e4f8a2c5b7d3
Revises: d3b6e9c2a5f1
Create Date: 2025-05-30 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'e4f8a2c5b7d3'
down_revision = 'd3b6e9c2a5f1'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if table exists."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade():
    # Only create if table doesn't exist
    if not table_exists('daily_ten_goals'):
        op.create_table(
            'daily_ten_goals',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('goal_date', sa.Date(), nullable=False, index=True),
            sa.Column('goals', sa.Text(), nullable=False, default=''),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        )


def downgrade():
    if table_exists('daily_ten_goals'):
        op.drop_table('daily_ten_goals')
