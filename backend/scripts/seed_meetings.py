from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from typing import List

from database import SessionLocal
from models.meeting import Meeting, Tag, AccessLevel
from models.user import User, UserRole

def create_mock_tags(db: Session) -> List[Tag]:
    tags = [
        Tag(label="финансы"),
        Tag(label="планирование"),
        Tag(label="разработка"),
        Tag(label="маркетинг"),
        Tag(label="hr"),
        Tag(label="стратегия"),
        Tag(label="обучение"),
        Tag(label="презентация")
    ]
    for tag in tags:
        db.add(tag)
    db.commit()
    return tags

def create_mock_meetings(db: Session, users: List[User], tags: List[Tag]):
    # Создаем несколько встреч для каждого пользователя
    for user in users:
        for i in range(3):  # 3 встречи на пользователя
            meeting = Meeting(
                title=f"Встреча {i+1} от {user.first_name}",
                date=datetime.now() + timedelta(days=random.randint(-30, 30)),
                short_description=f"Описание встречи {i+1} от {user.first_name}",
                thumbnail_url=None,
                access_level=random.choice(list(AccessLevel)),
                created_by_id=user.id
            )
            
            # Добавляем случайные теги
            meeting.tags = random.sample(tags, k=random.randint(1, 3))
            
            # Добавляем случайных участников
            other_users = [u for u in users if u.id != user.id]
            meeting.participants = random.sample(other_users, k=random.randint(1, min(3, len(other_users))))
            
            # Для restricted встреч добавляем пользователей с доступом
            if meeting.access_level == AccessLevel.restricted:
                meeting.access_users = random.sample(other_users, k=random.randint(1, min(3, len(other_users))))
            
            db.add(meeting)
    
    db.commit()

def seed_database():
    db = SessionLocal()
    try:
        # Получаем существующих пользователей
        users = db.query(User).all()
        if not users:
            print("No users found in database. Please create users first.")
            return
        
        # Создаем теги
        tags = create_mock_tags(db)
        print(f"Created {len(tags)} tags")
        
        # Создаем встречи
        create_mock_meetings(db, users, tags)
        print("Created mock meetings")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_database() 