"""add file meeting id

Revision ID: add_file_meeting_id
Revises: update_audit_log
Create Date: 2024-02-04 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_file_meeting_id'
down_revision = 'update_audit_log'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add meeting_id column to files table
    op.add_column('files', sa.Column('meeting_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_files_meeting_id',
        'files', 'meetings',
        ['meeting_id'], ['id']
    )

def downgrade() -> None:
    # Remove meeting_id column from files table
    op.drop_constraint('fk_files_meeting_id', 'files', type_='foreignkey')
    op.drop_column('files', 'meeting_id') 