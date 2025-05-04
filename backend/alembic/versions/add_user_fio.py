"""add user fio

Revision ID: add_user_fio
Revises: initial_migration
Create Date: 2024-02-04 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_fio'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if users table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'users' not in tables:
        # If table doesn't exist, create it with all columns
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('first_name', sa.String(), nullable=False),
            sa.Column('last_name', sa.String(), nullable=False),
            sa.Column('middle_name', sa.String(), nullable=True),
            sa.Column('password_hash', sa.String(), nullable=False),
            sa.Column('role', postgresql.ENUM('user', 'superadmin', name='userrole'), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    else:
        # If table exists, add new columns
        columns = [c['name'] for c in inspector.get_columns('users')]
        
        if 'first_name' not in columns:
            op.add_column('users', sa.Column('first_name', sa.String(), nullable=True))
        if 'last_name' not in columns:
            op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))
        if 'middle_name' not in columns:
            op.add_column('users', sa.Column('middle_name', sa.String(), nullable=True))
        
        # Make columns non-nullable after adding them
        op.alter_column('users', 'first_name', nullable=False)
        op.alter_column('users', 'last_name', nullable=False)


def downgrade() -> None:
    # Check if users table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'users' in tables:
        # Remove the new columns
        columns = [c['name'] for c in inspector.get_columns('users')]
        
        if 'middle_name' in columns:
            op.drop_column('users', 'middle_name')
        if 'last_name' in columns:
            op.drop_column('users', 'last_name')
        if 'first_name' in columns:
            op.drop_column('users', 'first_name')

    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.execute('DROP TYPE auditaction') 