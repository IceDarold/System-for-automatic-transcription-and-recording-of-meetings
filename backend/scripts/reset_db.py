import os
import subprocess
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
import importlib
import sys

def reset_database():
    """
    Полностью сбрасывает и пересоздает базу данных
    """
    print("Resetting database...")
    
    # Получаем параметры подключения из переменных окружения
    db_host = os.environ.get("POSTGRES_SERVER", "db")
    db_port = os.environ.get("POSTGRES_PORT", "5432")
    db_user = os.environ.get("POSTGRES_USER", "postgres")
    db_pass = os.environ.get("POSTGRES_PASSWORD", "postgres")
    db_name = os.environ.get("POSTGRES_DB", "meeting_system")
    
    # Подключаемся к базе postgres для управления базами данных
    admin_engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/postgres")
    
    # Отключаем активные подключения и удаляем базу данных
    with admin_engine.connect() as conn:
        conn.execute("COMMIT")
        conn.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}'")
        conn.execute("COMMIT")
        
        # Удаляем базу данных (если существует)
        conn.execute("COMMIT")
        conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
        
        # Создаем базу данных заново
        conn.execute("COMMIT")
        conn.execute(f"CREATE DATABASE {db_name}")
    
    # Создаем движок для новой базы данных
    engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
    
    # Импортируем все модели, чтобы они были зарегистрированы в Base.metadata
    import_all_models()
    
    # Создаем все таблицы
    print("Creating tables...")
    Base.metadata.create_all(engine)
    
    print("Database reset successfully!")
    return True

def import_all_models():
    """
    Импортирует все модели, чтобы они были зарегистрированы в Base.metadata
    """
    models_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    
    # Добавляем директорию верхнего уровня в sys.path
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Импортируем все .py файлы из директории models
    for file in os.listdir(models_path):
        if file.endswith(".py") and file != "__init__.py":
            module_name = file[:-3]  # Убираем расширение .py
            try:
                importlib.import_module(f"models.{module_name}")
                print(f"Imported model: {module_name}")
            except ImportError as e:
                print(f"Failed to import model {module_name}: {e}")

if __name__ == "__main__":
    reset_database() 