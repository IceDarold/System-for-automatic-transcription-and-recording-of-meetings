import time
import os
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker # Import sessionmaker for type hinting

# Предполагаем, что эти функции тоже принимают session_factory или используют его глобально
from seed_users import seed_users
from seed_meetings import seed_database

def wait_for_db(session_factory: sessionmaker):
    """Ждем, пока база данных будет готова, используя переданную фабрику сессий."""
    # from database import SessionLocal # Больше не импортируем здесь
    max_retries = 10
    retry_interval = 1  # секунды
    
    print("Database connection parameters:")
    print(f"Host: {os.getenv('POSTGRES_SERVER')}")
    print(f"Port: {os.getenv('POSTGRES_PORT', '5432')}")
    print(f"User: {os.getenv('POSTGRES_USER')}")
    print(f"Database: {os.getenv('POSTGRES_DB')}")
    
    for i in range(max_retries):
        if not session_factory:
             print("Error: Session factory not provided to wait_for_db")
             return False
        try:
            db = session_factory() # Используем переданную фабрику
            # Проверяем подключение простым запросом
            db.execute(text("SELECT 1"))
            db.close()
            print("Database is ready!")
            return True
        except Exception as e:
            print(f"Waiting for database... ({i+1}/{max_retries})")
            print(f"Error: {str(e)}")
            time.sleep(retry_interval)
    
    print("Could not connect to database after maximum retries")
    return False

def seed_all(session_factory: sessionmaker):
    """Заполняет базу данных, используя переданную фабрику сессий."""
    if not wait_for_db(session_factory):
        return
    
    print("Starting database seeding...")
    
    # Передаем session_factory в дочерние функции сидинга
    print("\nSeeding users...")
    seed_users(session_factory)
    
    print("\nSeeding meetings...")
    seed_database(session_factory)
    
    print("\nDatabase seeding completed!")

if __name__ == "__main__":
    # Для прямого запуска скрипта нужно получить SessionLocal
    # Это может быть неидеально, лучше запускать через reset_db
    print("(Running seed_all.py directly)")
    try:
        # Импортируем init_db из database
        from database import init_db 
        print("Initializing DB for direct script run...")
        # Вызываем init_db и получаем engine и session_factory
        _, session_factory_for_direct_run = init_db()
        if session_factory_for_direct_run is None:
            raise RuntimeError("init_db() failed to provide a session factory during direct run.")
        print("Seeding with session factory obtained from init_db...")
        # Передаем полученную фабрику в seed_all
        seed_all(session_factory_for_direct_run)
    except ImportError as e:
        print(f"Could not import dependencies ({e}). Run this script via reset_db.py or ensure DB is initialized and PYTHONPATH is correct.")
    except Exception as e:
        print(f"An error occurred during direct seeding: {e}") 