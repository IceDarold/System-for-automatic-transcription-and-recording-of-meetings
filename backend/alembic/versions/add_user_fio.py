"""add user fio

Revision ID: add_user_fio
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_fio'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем новые колонки
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=False))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=False))
    op.add_column('users', sa.Column('middle_name', sa.String(), nullable=True))
    
    # Удаляем старую колонку username
    op.drop_column('users', 'username')


def downgrade() -> None:
    # Возвращаем старую колонку
    op.add_column('users', sa.Column('username', sa.String(), nullable=False))
    
    # Удаляем новые колонки
    op.drop_column('users', 'middle_name')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name') 