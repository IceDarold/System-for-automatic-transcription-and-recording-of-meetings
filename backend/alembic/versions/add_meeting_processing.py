"""add meeting processing

Revision ID: add_meeting_processing
Revises: create_missing_tables
Create Date: 2024-02-04 20:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_meeting_processing'
down_revision = 'create_missing_tables'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create enum types
    op.execute("DO $$ BEGIN CREATE TYPE meetingstatus AS ENUM ('pending', 'processing', 'done', 'failed'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE filetype AS ENUM ('audio', 'transcript', 'summary', 'protocol', 'thumbnail'); EXCEPTION WHEN duplicate_object THEN null; END $$;")

    # Create files table
    op.create_table(
        'files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_type', postgresql.ENUM('audio', 'transcript', 'summary', 'protocol', 'thumbnail', name='filetype', create_type=False), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_files_id'), 'files', ['id'], unique=False)

    # Create transcript_blocks table
    op.create_table(
        'transcript_blocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('speaker_id', sa.Integer(), nullable=True),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('language', sa.String(2), nullable=False, server_default='ru'),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ),
        sa.ForeignKeyConstraint(['speaker_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcript_blocks_id'), 'transcript_blocks', ['id'], unique=False)

    # Add new columns to meetings table
    op.add_column('meetings', sa.Column('status', postgresql.ENUM('pending', 'processing', 'done', 'failed', name='meetingstatus', create_type=False), nullable=False, server_default='pending'))
    op.add_column('meetings', sa.Column('processing_progress', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('meetings', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('meetings', sa.Column('audio_file_id', sa.Integer(), nullable=True))
    op.add_column('meetings', sa.Column('transcript_file_id', sa.Integer(), nullable=True))
    op.add_column('meetings', sa.Column('summary_file_id', sa.Integer(), nullable=True))
    op.add_column('meetings', sa.Column('protocol_file_id', sa.Integer(), nullable=True))

    # Add foreign key constraints
    op.create_foreign_key(None, 'meetings', 'files', ['audio_file_id'], ['id'])
    op.create_foreign_key(None, 'meetings', 'files', ['transcript_file_id'], ['id'])
    op.create_foreign_key(None, 'meetings', 'files', ['summary_file_id'], ['id'])
    op.create_foreign_key(None, 'meetings', 'files', ['protocol_file_id'], ['id'])

def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint(None, 'meetings', type_='foreignkey')
    op.drop_constraint(None, 'meetings', type_='foreignkey')
    op.drop_constraint(None, 'meetings', type_='foreignkey')
    op.drop_constraint(None, 'meetings', type_='foreignkey')

    # Drop columns from meetings table
    op.drop_column('meetings', 'protocol_file_id')
    op.drop_column('meetings', 'summary_file_id')
    op.drop_column('meetings', 'transcript_file_id')
    op.drop_column('meetings', 'audio_file_id')
    op.drop_column('meetings', 'error_message')
    op.drop_column('meetings', 'processing_progress')
    op.drop_column('meetings', 'status')

    # Drop transcript_blocks table
    op.drop_index(op.f('ix_transcript_blocks_id'), table_name='transcript_blocks')
    op.drop_table('transcript_blocks')

    # Drop files table
    op.drop_index(op.f('ix_files_id'), table_name='files')
    op.drop_table('files')

    # Drop enum types
    op.execute('DROP TYPE filetype')
    op.execute('DROP TYPE meetingstatus') 