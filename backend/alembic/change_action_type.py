"""change action type to string

Revision ID: change_action_type
Revises: initial_migration
Create Date: 2025-05-05 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'change_action_type'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Change the action column type from enum to string
    op.execute('ALTER TABLE audit_logs ALTER COLUMN action TYPE VARCHAR USING action::VARCHAR')
    
    # Drop the audit_action enum type if it exists
    op.execute("DROP TYPE IF EXISTS audit_action")


def downgrade():
    # Create the enum type
    op.execute("CREATE TYPE audit_action AS ENUM ('login', 'logout', 'register', 'token_refresh', 'view_meeting', 'create_meeting', 'update_meeting', 'delete_meeting')")
    
    # Convert the string column back to enum
    op.execute("ALTER TABLE audit_logs ALTER COLUMN action TYPE audit_action USING action::audit_action") 