from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime
from typing import List
import hashlib

from models.user import User, UserRole

def create_mock_users(db: Session) -> List[User]:
    # Создаем тестовых пользователей
    users = [
        User(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password_hash=hashlib.sha256("admin123".encode()).hexdigest(),
            role=UserRole.superadmin
        ),
        User(
            email="ivan@example.com",
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            password_hash=hashlib.sha256("user123".encode()).hexdigest(),
            role=UserRole.user
        ),
        User(
            email="maria@example.com",
            first_name="Мария",
            last_name="Петрова",
            password_hash=hashlib.sha256("user123".encode()).hexdigest(),
            role=UserRole.user
        ),
        User(
            email="alex@example.com",
            first_name="Алексей",
            last_name="Сидоров",
            password_hash=hashlib.sha256("user123".encode()).hexdigest(),
            role=UserRole.user
        ),
        User(
            email="anna@example.com",
            first_name="Анна",
            last_name="Козлова",
            password_hash=hashlib.sha256("user123".encode()).hexdigest(),
            role=UserRole.user
        )
    ]
    
    for user in users:
        db.add(user)
    db.commit()
    return users

def seed_users(session_factory: sessionmaker):
    db: Session = session_factory()
    try:
        # Проверяем, есть ли уже пользователи
        existing_users = db.query(User).first()
        if existing_users:
            print("Users already exist in database. Skipping user creation.")
            return
        
        users = create_mock_users(db)
        print(f"Created {len(users)} users")
        
    finally:
        db.close()

if __name__ == "__main__":
    # При прямом запуске нужна инициализация БД и фабрика
    try:
        from database import SessionLocal, init_db
        print("Initializing DB for direct user seeding...")
        init_db()
        print("Seeding users directly...")
        seed_users(SessionLocal)
    except ImportError:
        print("Could not import DB components. Run via reset_db.py or seed_all.py.")
    except Exception as e:
        print(f"Error during direct user seeding: {e}") 