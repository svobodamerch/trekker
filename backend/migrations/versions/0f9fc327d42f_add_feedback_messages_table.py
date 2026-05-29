"""add feedback_messages table

Revision ID: 0f9fc327d42f
Revises: dfc8706f3333
Create Date: 2026-05-29 20:18:37.113091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '0f9fc327d42f'
down_revision: Union[str, Sequence[str], None] = 'dfc8706f3333'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('feedback_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('telegram_user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('source', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reminder_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('reminder_date', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('sent_at', sa.DateTime(), nullable=False),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reminder_logs_reminder_date'), 'reminder_logs', ['reminder_date'], unique=False)
    op.create_index(op.f('ix_reminder_logs_user_id'), 'reminder_logs', ['user_id'], unique=False)
    op.add_column('ai_analyses', sa.Column('period_start', sa.DateTime(), nullable=True))
    op.add_column('ai_analyses', sa.Column('period_end', sa.DateTime(), nullable=True))
    op.add_column('ai_analyses', sa.Column('entry_count', sa.Integer(), nullable=True))
    op.add_column('ai_analyses', sa.Column('raw_output', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('ai_analyses', 'raw_output')
    op.drop_column('ai_analyses', 'entry_count')
    op.drop_column('ai_analyses', 'period_end')
    op.drop_column('ai_analyses', 'period_start')
    op.drop_index(op.f('ix_reminder_logs_user_id'), table_name='reminder_logs')
    op.drop_index(op.f('ix_reminder_logs_reminder_date'), table_name='reminder_logs')
    op.drop_table('reminder_logs')
    op.drop_table('feedback_messages')
