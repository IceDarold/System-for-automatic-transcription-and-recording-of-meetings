from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

    
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    login = Column(String)
    login = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)
    department_id = Column(Integer, ForeignKey("departments.id"))
    # Связь с департментом
    department = relationship("Department", back_populates="users")
    
class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    # Связь: один департмент → много пользователей
    users = relationship("User", back_populates="department")