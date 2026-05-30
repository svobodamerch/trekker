"""Update community_posts for weekly reports

Revision ID: f6h0c4e7i9l2
Revises: f5g9b3d6h8k1
Create Date: 2025-05-30 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'f6h0c4e7i9l2'
down_revision = 'f5g9b3d6h8k1'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if column exists."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = inspector.get_columns(table_name)
    return any(c['name'] == column_name for c in columns)


def upgrade():
    # Add is_weekly_report column to community_posts
    if not column_exists('community_posts', 'is_weekly_report'):
        op.add_column('community_posts', 
            sa.Column('is_weekly_report', sa.Boolean(), nullable=False, server_default='false'))
    
    # Make user_id nullable for system posts
    op.alter_column('community_posts', 'user_id',
        existing_type=sa.Integer(),
        nullable=True)


def downgrade():
    # Revert user_id to non-nullable
    op.alter_column('community_posts', 'user_id',
        existing_type=sa.Integer(),
        nullable=False)
    
    # Drop is_weekly_report column
    if column_exists('community_posts', 'is_weekly_report'):
        op.drop_column('community_posts', 'is_weekly_report')
