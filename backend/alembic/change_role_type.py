"""change role type to string

Revision ID: change_role_type
Revises: change_action_type
Create Date: 2025-05-05 04:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'change_role_type'
down_revision = 'change_action_type'
branch_labels = None
depends_on = None

def upgrade():
    # Change the role column type from enum to string
    op.execute('ALTER TABLE users ALTER COLUMN role TYPE VARCHAR USING role::VARCHAR')
    
    # Drop the role enum type if it exists
    op.execute("DROP TYPE IF EXISTS role")


def downgrade():
    # Create the enum type
    op.execute("CREATE TYPE role AS ENUM ('admin', 'user', 'guest')")
    
    # Convert the string column back to enum
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE role USING role::role") 