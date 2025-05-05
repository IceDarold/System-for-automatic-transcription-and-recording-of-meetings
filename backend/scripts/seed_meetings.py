from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from typing import List

from database import SessionLocal
from models.meeting import Meeting, Tag
from models.user import User, UserRole

def create_mock_tags(db: Session) -> List[Tag]:
    # Список тегов, которые мы хотим иметь
    tag_labels = ["финансы", "планирование", "разработка", "маркетинг", 
                 "hr", "стратегия", "обучение", "презентация"]
    
    # Получаем уже существующие теги
    existing_tags = db.query(Tag).all()
    existing_labels = [tag.label for tag in existing_tags]
    
    # Создаем только новые теги
    new_tags = []
    for label in tag_labels:
        if label not in existing_labels:
            tag = Tag(label=label)
            db.add(tag)
            new_tags.append(tag)
    
    if new_tags:
        db.commit()
        print(f"Created {len(new_tags)} new tags")
    else:
        print("All tags already exist")
    
    # Возвращаем все теги (и существующие, и новые)
    return db.query(Tag).all()

def create_mock_meetings(db: Session, users: List[User], tags: List[Tag]):
    # Проверяем, есть ли уже встречи в базе
    existing_meetings_count = db.query(Meeting).count()
    if existing_meetings_count > 0:
        print(f"There are already {existing_meetings_count} meetings in the database. Skipping meeting creation.")
        return
    
    # Создаем несколько встреч для каждого пользователя
    created_count = 0
    for user in users:
        for i in range(3):  # 3 встречи на пользователя
            meeting = Meeting(
                title=f"Встреча {i+1} от {user.first_name}",
                date=datetime.now().date() + timedelta(days=random.randint(-30, 30)),
                description=f"Описание встречи {i+1} от {user.first_name}",
                is_online=random.choice([True, False]),
                is_published=random.choice([True, False]),
                created_by_id=user.id,
                status='pending',
                access_level='private'
            )
            
            # Добавляем случайные теги
            meeting.tags = random.sample(tags, k=min(random.randint(1, 3), len(tags)))
            
            db.add(meeting)
            created_count += 1
    
    if created_count > 0:
        db.commit()
        print(f"Created {created_count} mock meetings")
    else:
        print("No new meetings created")

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
        
        # Создаем встречи
        create_mock_meetings(db, users, tags)
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_database() 