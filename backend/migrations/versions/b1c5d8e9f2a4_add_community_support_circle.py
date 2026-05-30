"""Add community support circle tables

Revision ID: b1c5d8e9f2a4
Revises: a318bc88c71c
Create Date: 2026-05-30 20:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b1c5d8e9f2a4'
down_revision: Union[str, None] = 'a318bc88c71c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create community_posts table
    op.create_table(
        'community_posts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('source_type', sa.String(length=50), nullable=False, default='custom'),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('discussion_prompt', sa.Text(), nullable=True),
        sa.Column('visibility', sa.String(length=20), nullable=False, default='anonymous'),
        sa.Column('status', sa.String(length=20), nullable=False, default='published'),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create community_comments table
    op.create_table(
        'community_comments',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('post_id', sa.Integer(), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('comment_type', sa.String(length=30), nullable=False, default='support'),
        sa.Column('status', sa.String(length=20), nullable=False, default='published'),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['post_id'], ['community_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create community_reactions table
    op.create_table(
        'community_reactions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('post_id', sa.Integer(), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('reaction_type', sa.String(length=20), nullable=False, default='support'),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['post_id'], ['community_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create unique constraint for reactions (one per user per post)
    op.create_unique_constraint(
        'uq_user_post_reaction', 
        'community_reactions', 
        ['post_id', 'user_id', 'reaction_type']
    )
    
    # Create community_reports table
    op.create_table(
        'community_reports',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('reporter_user_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('comment_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(length=100), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='new'),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['reporter_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['post_id'], ['community_posts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['comment_id'], ['community_comments.id'], ondelete='SET NULL'),
    )


def downgrade() -> None:
    op.drop_table('community_reports')
    op.drop_table('community_reactions')
    op.drop_table('community_comments')
    op.drop_table('community_posts')
