import os
import shutil
from sqlalchemy import create_engine, text
from database import get_db, Base, engine

def reset_migrations():
    """
    Сброс миграций Alembic и пересоздание с нуля
    """
    print("Resetting migrations...")
    
    # Удаляем существующие миграции, кроме env.py и шаблона
    versions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic", "versions")
    if os.path.exists(versions_dir):
        for file in os.listdir(versions_dir):
            if file.endswith(".py") and file != "__init__.py":
                os.remove(os.path.join(versions_dir, file))
                print(f"Removed migration file: {file}")
    
    # Создаем новую миграцию, которая соответствует текущим моделям
    os.system("alembic revision --autogenerate -m 'initial_migration'")
    
    print("Migration files reset successfully.")

if __name__ == "__main__":
    reset_migrations() 