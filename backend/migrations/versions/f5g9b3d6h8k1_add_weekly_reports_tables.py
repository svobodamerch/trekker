"""Add weekly reports tables

Revision ID: f5g9b3d6h8k1
Revises: e4f8a2c5b7d3
Create Date: 2025-05-30 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'f5g9b3d6h8k1'
down_revision = 'e4f8a2c5b7d3'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if table exists."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade():
    # Create weekly_reports table
    if not table_exists('weekly_reports'):
        op.create_table(
            'weekly_reports',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('week_start', sa.Date(), nullable=False, index=True),
            sa.Column('week_end', sa.Date(), nullable=False),
            sa.Column('entries_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('days_with_entries', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('days_missed', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('streak_at_week_end', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('avg_mood', sa.Float(), nullable=True),
            sa.Column('avg_anxiety', sa.Float(), nullable=True),
            sa.Column('avg_energy', sa.Float(), nullable=True),
            sa.Column('summary', sa.Text(), nullable=False, server_default=''),
            sa.Column('highlights', sa.Text(), nullable=False, server_default=''),
            sa.Column('patterns', sa.Text(), nullable=False, server_default=''),
            sa.Column('encouragement', sa.Text(), nullable=False, server_default=''),
            sa.Column('suggestions', sa.Text(), nullable=False, server_default=''),
            sa.Column('raw_ai_output', sa.Text(), nullable=True),
            sa.Column('sent_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    
    # Create community_weekly_reports table
    if not table_exists('community_weekly_reports'):
        op.create_table(
            'community_weekly_reports',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
            sa.Column('week_start', sa.Date(), nullable=False, index=True, unique=True),
            sa.Column('week_end', sa.Date(), nullable=False),
            sa.Column('total_users', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('active_users', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('total_entries', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('total_pulse_entries', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('total_diary_entries', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('community_avg_mood', sa.Float(), nullable=True),
            sa.Column('community_avg_anxiety', sa.Float(), nullable=True),
            sa.Column('community_avg_energy', sa.Float(), nullable=True),
            sa.Column('community_summary', sa.Text(), nullable=False, server_default=''),
            sa.Column('trends', sa.Text(), nullable=False, server_default=''),
            sa.Column('encouragement', sa.Text(), nullable=False, server_default=''),
            sa.Column('collective_challenge', sa.Text(), nullable=False, server_default=''),
            sa.Column('community_post_id', sa.Integer(), sa.ForeignKey('community_posts.id'), nullable=True),
            sa.Column('raw_ai_output', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )


def downgrade():
    if table_exists('community_weekly_reports'):
        op.drop_table('community_weekly_reports')
    if table_exists('weekly_reports'):
        op.drop_table('weekly_reports')
