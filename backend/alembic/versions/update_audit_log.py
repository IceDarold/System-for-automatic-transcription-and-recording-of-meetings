"""update audit log

Revision ID: update_audit_log
Revises: add_meeting_processing
Create Date: 2024-02-04 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_audit_log'
down_revision = 'add_meeting_processing'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add new columns to audit_logs table
    op.add_column('audit_logs', sa.Column('resource_id', sa.Integer(), nullable=True))
    op.add_column('audit_logs', sa.Column('resource_type', sa.String(), nullable=True))
    op.add_column('audit_logs', sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Update auditaction enum
    op.execute("ALTER TYPE auditaction ADD VALUE IF NOT EXISTS 'view_meeting'")
    op.execute("ALTER TYPE auditaction ADD VALUE IF NOT EXISTS 'create_meeting'")
    op.execute("ALTER TYPE auditaction ADD VALUE IF NOT EXISTS 'update_meeting'")
    op.execute("ALTER TYPE auditaction ADD VALUE IF NOT EXISTS 'delete_meeting'")

def downgrade() -> None:
    # Remove columns from audit_logs table
    op.drop_column('audit_logs', 'metadata')
    op.drop_column('audit_logs', 'resource_type')
    op.drop_column('audit_logs', 'resource_id')

    # Note: We cannot remove enum values in PostgreSQL
    # The enum values will remain in the database 