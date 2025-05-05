"""create missing tables

Revision ID: create_missing_tables
Revises: add_user_fio
Create Date: 2025-05-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_missing_tables'
down_revision = 'add_user_fio'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем enum для статуса встречи
    op.execute("DO $$ BEGIN CREATE TYPE meetingstatus AS ENUM ('pending', 'processing', 'done', 'failed'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE accesslevel AS ENUM ('public', 'restricted', 'private'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Создаем таблицу meetings
    op.create_table(
        'meetings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),  # в секундах
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('access_level', postgresql.ENUM('public', 'restricted', 'private', name='accesslevel', create_type=False), nullable=False, server_default='private'),
        sa.Column('status', postgresql.ENUM('pending', 'processing', 'done', 'failed', name='meetingstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('processing_progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meetings_id'), 'meetings', ['id'], unique=False)
    
    # Создаем таблицу tags
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('label')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    
    # Создаем таблицу связей meeting_tags
    op.create_table(
        'meeting_tags',
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('meeting_id', 'tag_id')
    )
    
    # Создаем таблицы для связей многие-ко-многим
    op.create_table(
        'meeting_participants',
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('meeting_id', 'user_id')
    )
    
    op.create_table(
        'meeting_access',
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('meeting_id', 'user_id')
    )

def downgrade() -> None:
    # Удаляем таблицы в обратном порядке
    op.drop_table('meeting_access')
    op.drop_table('meeting_participants')
    op.drop_table('meeting_tags')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')
    op.drop_index(op.f('ix_meetings_id'), table_name='meetings')
    op.drop_table('meetings')
    
    # Удаляем enum
    op.execute('DROP TYPE IF EXISTS meetingstatus')
    op.execute('DROP TYPE IF EXISTS accesslevel') 