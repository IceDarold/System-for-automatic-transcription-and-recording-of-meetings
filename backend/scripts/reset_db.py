# reset_db.py

import os
import sys
import importlib
import argparse
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine.url import make_url
import logging

# Ensure the project root (backend directory) is in sys.path
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from core.config import settings
from database import Base, init_db

def import_all_models():
    models_path = Path(__file__).resolve().parent / "models"

    for file in os.listdir(models_path):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            importlib.import_module(f"models.{module_name}")
            print(f"Imported model: models.{module_name}")

def reset_database(with_test_data=False, force=False):
    # 🔐 Защита от запуска в проде
    if settings.APP_ENV == "production" and not force:
        print("🚫 Refusing to run in production without --force")
        sys.exit(1)

    print(f"🔄 Resetting PostgreSQL database (env: {settings.APP_ENV})...")

    db_name = settings.POSTGRES_DB
    target_url = settings.DATABASE_URL
    print(f"Target database: '{db_name}'")
    print(f"Target URL: {target_url}")

    # Создаем URL для подключения к стандартной БД (например, 'postgres') для выполнения DROP/CREATE
    try:
        target_db_uri = make_url(target_url)
        admin_db_uri = target_db_uri._replace(database="postgres") # Или template1, если 'postgres' недоступна
        admin_url = admin_db_uri.render_as_string(hide_password=False)
        print(f"Admin URL for DROP/CREATE: {admin_db_uri.render_as_string(hide_password=True)}")
    except Exception as e:
        logging.error(f"❌ Could not create admin database URL from target URL '{target_url}': {e}")
        sys.exit(1)

    # Используем AUTOCOMMIT для операций DROP/CREATE DATABASE
    # Подключаемся к стандартной БД ('postgres') для выполнения DROP/CREATE
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", client_encoding='utf8')
    
    # Шаг 1: Завершение соединений (в отдельном блоке with, подключаемся к целевой БД)
    # Подключение к целевой БД для завершения сессий *в ней*
    terminate_engine = create_engine(target_url, isolation_level="AUTOCOMMIT", client_encoding='utf8')
    try:
        with terminate_engine.connect() as conn:
            print(f"🔌 Terminating existing connections to '{db_name}'...")
            # Завершаем только сессии к целевой БД
            conn.execute(text(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}' AND pid <> pg_backend_pid()"))
            print(f"🔌 Connections to '{db_name}' terminated (or none existed).")
    except Exception as e:
        # Логгируем предупреждение, но продолжаем
        logging.warning(f"Could not terminate connections to '{db_name}' (might be okay if no connections existed or DB doesn't exist yet): {e}")
    finally:
        terminate_engine.dispose() # Закрываем этот engine

    # Шаг 2: Удаление базы данных (подключаемся к 'postgres' БД)
    try:
        with admin_engine.connect() as conn:
            print(f"💣 Dropping database '{db_name}'...")
            conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
            print(f"💣 Database '{db_name}' dropped (or did not exist).")
    except Exception as e:
        logging.error(f"❌ Failed to drop database '{db_name}': {e}")
        admin_engine.dispose()
        sys.exit(1)

    # Шаг 3: Создание базы данных (подключаемся к 'postgres' БД)
    try:
        with admin_engine.connect() as conn:
            print(f"🧱 Creating database '{db_name}'...")
            conn.execute(text(f"CREATE DATABASE {db_name} ENCODING 'utf8'"))
            print(f"🧱 Database '{db_name}' created.")
    except Exception as e:
        logging.error(f"❌ Failed to create database '{db_name}': {e}")
        admin_engine.dispose()
        sys.exit(1)
    finally:
        admin_engine.dispose() # Закрываем admin engine

    # Шаг 4: Создание таблиц с помощью SQLAlchemy
    print(f"📦 Creating tables in '{db_name}' based on models...")
    try:
        # Подключаемся к ТОЛЬКО ЧТО СОЗДАННОЙ базе данных
        target_engine = create_engine(target_url) 
        # Убеждаемся, что все модели загружены, чтобы Base.metadata был полным
        import_all_models() 
        Base.metadata.create_all(bind=target_engine)
        print("📦 Tables created successfully.")
    except Exception as e:
        logging.error(f"❌ Failed to create tables: {e}")
        if target_engine:
             target_engine.dispose()
        sys.exit(1)
    finally:
        # Закрываем engine, использованный для create_all
        if target_engine:
             target_engine.dispose()

    # Шаг 5: Инициализация engine и SessionLocal для приложения/сидинга
    print("🚀 Initializing engine and SessionLocal for the application...")
    initialized_engine = None
    initialized_session_factory = None
    try:
        initialized_engine, initialized_session_factory = init_db()
        if initialized_engine is None or initialized_session_factory is None:
             raise RuntimeError("init_db did not return a valid engine and session factory.")
        print("🚀 Engine and SessionLocal initialized successfully.")
    except Exception as e:
        logging.error(f"❌ Failed to initialize engine/SessionLocal: {e}")
        if initialized_engine:
            initialized_engine.dispose()
        sys.exit(1)

    if with_test_data:
        print("🌱 Seeding test data...")
        try:
            from seed_all import seed_all # Импортируем функцию
            # Передаем фабрику сессий, полученную из init_db
            seed_all(initialized_session_factory) 
        except ImportError:
             logging.error("❌ Could not import seed_all. Make sure seed_all.py exists in scripts folder.")
        except Exception as e:
             logging.error(f"❌ Failed during data seeding: {e}")
             # sys.exit(1) # Оставляем опциональным

    print("✅ Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset the PostgreSQL database")
    parser.add_argument("--with-test-data", action="store_true", help="Seed database with test data after reset")
    parser.add_argument("--force", action="store_true", help="Force execution even in production environment")

    args = parser.parse_args()
    reset_database(with_test_data=args.with_test_data, force=args.force)
