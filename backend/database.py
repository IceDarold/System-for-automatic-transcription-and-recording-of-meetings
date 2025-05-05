from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Use DATABASE_URL if available, otherwise use SQLALCHEMY_DATABASE_URI
db_url = settings.DATABASE_URL or settings.SQLALCHEMY_DATABASE_URI
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 