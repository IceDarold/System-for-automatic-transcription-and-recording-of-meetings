"""change_action_type

Revision ID: change_action_type
Revises: change_role_type
Create Date: 2024-02-04 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'change_action_type'
down_revision = 'change_role_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Используем временную колонку, затем удалим enum
    op.add_column('audit_logs', sa.Column('action_str', sa.String(), nullable=True))
    
    # Обновляем значения в новой колонке
    op.execute("UPDATE audit_logs SET action_str = action::text")
    
    # Удаляем старую колонку с enum типом
    op.drop_column('audit_logs', 'action')
    
    # Переименовываем временную колонку в action
    op.alter_column('audit_logs', 'action_str', new_column_name='action')
    
    # Устанавливаем not null
    op.alter_column('audit_logs', 'action', nullable=False)
    
    # Создаем ограничение для action
    op.create_check_constraint(
        'action_check', 
        'audit_logs', 
        "action IN ('login', 'logout', 'register', 'token_refresh')"
    )


def downgrade() -> None:
    # Удаляем ограничение
    op.drop_constraint('action_check', 'audit_logs', type_='check')
    
    # Создаем enum тип, если он уже не существует
    op.execute("DO $$ BEGIN CREATE TYPE auditaction AS ENUM ('login', 'logout', 'register', 'token_refresh'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Создаем временную колонку с enum типом
    op.add_column('audit_logs', sa.Column('action_enum', postgresql.ENUM('login', 'logout', 'register', 'token_refresh', name='auditaction'), nullable=True))
    
    # Обновляем значения в новой колонке
    op.execute("UPDATE audit_logs SET action_enum = action::auditaction")
    
    # Удаляем старую текстовую колонку
    op.drop_column('audit_logs', 'action')
    
    # Переименовываем временную колонку в action
    op.alter_column('audit_logs', 'action_enum', new_column_name='action')
    
    # Устанавливаем not null
    op.alter_column('audit_logs', 'action', nullable=False) 