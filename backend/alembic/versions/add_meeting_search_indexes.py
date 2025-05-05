"""add meeting search indexes

Revision ID: add_meeting_search_indexes
Revises: add_file_meeting_id
Create Date: 2024-02-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_meeting_search_indexes'
down_revision = 'add_file_meeting_id'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add indexes for search optimization
    op.create_index('ix_meetings_title', 'meetings', ['title'])
    op.create_index('ix_meetings_date', 'meetings', ['date'])
    op.create_index('ix_meetings_created_at', 'meetings', ['created_at'])
    op.create_index('ix_meetings_status', 'meetings', ['status'])
    op.create_index('ix_meetings_created_by', 'meetings', ['created_by'])

    # Add GIN index for full-text search on title and description
    op.execute('CREATE INDEX ix_meetings_search ON meetings USING gin (to_tsvector(\'russian\', title || \' \' || COALESCE(description, \'\')))')

    # Add indexes only for meeting_tags as the other tables don't exist yet
    op.create_index('ix_meeting_tags_tag_id', 'meeting_tags', ['tag_id'])
    op.create_index('ix_meeting_tags_meeting_id', 'meeting_tags', ['meeting_id'])

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_meetings_title')
    op.drop_index('ix_meetings_date')
    op.drop_index('ix_meetings_created_at')
    op.drop_index('ix_meetings_status')
    op.drop_index('ix_meetings_created_by')
    op.drop_index('ix_meetings_search')
    
    # Drop only meeting_tags indexes
    op.drop_index('ix_meeting_tags_tag_id')
    op.drop_index('ix_meeting_tags_meeting_id') 