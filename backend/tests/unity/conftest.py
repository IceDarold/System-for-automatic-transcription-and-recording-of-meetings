import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from datetime import datetime

from database import Base, get_db
from models import User, Meeting, Tag

# Test database URL (SQLite in-memory for unit tests)
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine (SQLite in-memory)."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}, # Necessary for SQLite
        poolclass=StaticPool, # Good for in-memory DB
    )
    Base.metadata.create_all(bind=engine)
    yield engine # Yield engine for potential session-scoped setup
    # No need to drop tables usually for :memory:

@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create a fresh SQLite database session for each unit test."""
    connection = test_db_engine.connect()
    # Begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    # Rollback the transaction to revert any changes made during the test
    transaction.rollback()
    # Return the connection to the pool
    connection.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user instance in the unit test DB session."""
    # Note: Consider if unit tests should mock the DB instead.
    # Using a real (in-memory) DB blurs the line with integration tests.
    user = User(
        email="unit_test@example.com", # Different email for clarity
        password_hash="hashed_password", # Unit tests might not need real hashing
        first_name="Unit",
        last_name="Tester",
        is_active=True,
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_meeting(db_session, test_user):
    """Create a test meeting instance in the unit test DB session."""
    meeting = Meeting(
        title="Unit Test Meeting",
        date=datetime.now().date(),
        start_time=datetime.now().time(),
        end_time=datetime.now().time(),
        duration=3600,
        location="Unit Test Location",
        is_online=False,
        is_published=True,
        access_level="public",
        created_by_id=test_user.id,
        status="done",
        processing_progress=100
    )
    db_session.add(meeting)
    db_session.commit()
    db_session.refresh(meeting)
    return meeting

@pytest.fixture
def test_participant(db_session, test_meeting, test_user):
    """Add a test participant to the meeting in the unit test DB session."""
    # This modifies the meeting object potentially, ensure test isolation
    if test_user not in test_meeting.participants:
         test_meeting.participants.append(test_user)
         db_session.commit()
    return test_user

@pytest.fixture
def test_tag(db_session, test_meeting):
    """Create a test tag and associate it with the meeting in the unit test DB session."""
    tag = Tag(
        label="unit_test_tag"
    )
    db_session.add(tag)
    # Ensure association is handled correctly if needed for the test
    if tag not in test_meeting.tags:
        test_meeting.tags.append(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag 