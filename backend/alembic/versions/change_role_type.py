"""change_role_type

Revision ID: change_role_type
Revises: add_user_fio
Create Date: 2024-02-04 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'change_role_type'
down_revision = 'add_user_fio'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Используем временную колонку, затем удалим enum
    op.add_column('users', sa.Column('role_str', sa.String(), nullable=True))
    
    # Обновляем значения в новой колонке
    op.execute("UPDATE users SET role_str = role::text")
    
    # Удаляем старую колонку с enum типом
    op.drop_column('users', 'role')
    
    # Переименовываем временную колонку в role
    op.alter_column('users', 'role_str', new_column_name='role')
    
    # Устанавливаем not null и default
    op.alter_column('users', 'role', nullable=False, server_default='user')
    
    # Создаем ограничение для роли
    op.create_check_constraint(
        'role_check', 
        'users', 
        "role IN ('user', 'superadmin')"
    )


def downgrade() -> None:
    # Удаляем ограничение
    op.drop_constraint('role_check', 'users', type_='check')
    
    # Создаем enum тип, если он уже не существует
    op.execute("DO $$ BEGIN CREATE TYPE userrole AS ENUM ('user', 'superadmin'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Создаем временную колонку с enum типом
    op.add_column('users', sa.Column('role_enum', postgresql.ENUM('user', 'superadmin', name='userrole'), nullable=True))
    
    # Обновляем значения в новой колонке
    op.execute("UPDATE users SET role_enum = role::userrole")
    
    # Удаляем старую текстовую колонку
    op.drop_column('users', 'role')
    
    # Переименовываем временную колонку в role
    op.alter_column('users', 'role_enum', new_column_name='role')
    
    # Устанавливаем not null и default
    op.alter_column('users', 'role', nullable=False, server_default='user') 