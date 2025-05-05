"""rename transcript metadata

Revision ID: rename_transcript_metadata
Revises: add_meeting_search_indexes
Create Date: 2024-02-05 10:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'rename_transcript_metadata'
down_revision = 'add_meeting_search_indexes'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Check if the column exists before trying to rename it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('transcript_blocks')]
    
    if 'metadata' in columns and 'transcript_metadata' not in columns:
        # Rename column from metadata to transcript_metadata
        op.alter_column('transcript_blocks', 'metadata', 
                        new_column_name='transcript_metadata', 
                        existing_type=postgresql.JSON(astext_type=sa.Text()), 
                        existing_nullable=True)

def downgrade() -> None:
    # Rename column back from transcript_metadata to metadata
    op.alter_column('transcript_blocks', 'transcript_metadata', 
                    new_column_name='metadata', 
                    existing_type=postgresql.JSON(astext_type=sa.Text()), 
                    existing_nullable=True) 