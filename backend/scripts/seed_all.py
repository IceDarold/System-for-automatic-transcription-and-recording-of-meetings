import time
import os
from sqlalchemy import text
from seed_users import seed_users
from seed_meetings import seed_database

def wait_for_db():
    """Ждем, пока база данных будет готова"""
    from database import SessionLocal
    max_retries = 10
    retry_interval = 1  # секунды
    
    print("Database connection parameters:")
    print(f"Host: {os.getenv('POSTGRES_SERVER')}")
    print(f"Port: {os.getenv('POSTGRES_PORT', '5432')}")
    print(f"User: {os.getenv('POSTGRES_USER')}")
    print(f"Database: {os.getenv('POSTGRES_DB')}")
    
    for i in range(max_retries):
        try:
            db = SessionLocal()
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

def seed_all():
    if not wait_for_db():
        return
    
    print("Starting database seeding...")
    
    # Сначала создаем пользователей
    print("\nSeeding users...")
    seed_users()
    
    # Затем создаем встречи
    print("\nSeeding meetings...")
    seed_database()
    
    print("\nDatabase seeding completed!")

if __name__ == "__main__":
    seed_all() 