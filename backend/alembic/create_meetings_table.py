"""create meetings table

Revision ID: create_meetings_table
Revises: add_user_fio
Create Date: 2025-05-05 04:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_meetings_table'
down_revision = 'add_user_fio'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create enum type for access level
    op.execute("DO $$ BEGIN CREATE TYPE accesslevel AS ENUM ('private', 'team', 'public'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Create meetings table
    op.create_table(
        'meetings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('access_level', postgresql.ENUM('private', 'team', 'public', name='accesslevel', create_type=False), nullable=False, server_default='private'),
        sa.Column('is_ready', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meetings_id'), 'meetings', ['id'], unique=False)
    
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('label')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    
    # Create meeting_tags association table
    op.create_table(
        'meeting_tags',
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('meeting_id', 'tag_id')
    )
    
    # Create meeting_participants association table
    op.create_table(
        'meeting_participants',
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('meeting_id', 'user_id')
    )

def downgrade() -> None:
    # Drop tables
    op.drop_table('meeting_participants')
    op.drop_table('meeting_tags')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')
    op.drop_index(op.f('ix_meetings_id'), table_name='meetings')
    op.drop_table('meetings')
    
    # Drop enum
    op.execute('DROP TYPE accesslevel') 