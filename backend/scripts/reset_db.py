# reset_db.py

import os
import sys
import importlib
import argparse
from pathlib import Path

# Ensure the project root (backend directory) is in sys.path
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from sqlalchemy import create_engine
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
    print(f"🔄 Resetting PostgreSQL URL: {target_url}...")

    admin_engine = create_engine(target_url, isolation_level="AUTOCOMMIT", client_encoding='utf8')
    with admin_engine.connect() as conn:
        print("🔌 Terminating existing connections...")
        conn.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}'")
        print("💣 Dropping database...")
        conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
        print("🧱 Creating database...")
        conn.execute(f"CREATE DATABASE {db_name} ENCODING 'utf8'")

    target_engine = create_engine(target_url)
    import_all_models()
    print("📦 Creating tables...")
    Base.metadata.create_all(bind=target_engine)

    init_db()

    if with_test_data:
        print("🌱 Seeding test data...")
        from seed_all import seed_all
        seed_all()

    print("✅ Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset the PostgreSQL database")
    parser.add_argument("--with-test-data", action="store_true", help="Seed database with test data after reset")
    parser.add_argument("--force", action="store_true", help="Force execution even in production environment")

    args = parser.parse_args()
    reset_database(with_test_data=args.with_test_data, force=args.force)
