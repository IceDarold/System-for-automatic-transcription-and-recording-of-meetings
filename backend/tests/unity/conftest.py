import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile
from datetime import datetime

from backend.app import app
from database import Base, get_db
from models import User, Meeting, Tag
from core.security import create_access_token
from core.auth import get_current_user

# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create a fresh database session for each test"""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session, test_user):
    """Create a test client with a test database session and test user auth"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        is_active=True,
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_meeting(db_session, test_user):
    """Create a test meeting"""
    meeting = Meeting(
        title="Test Meeting",
        date=datetime.now().date(),
        start_time=datetime.now().time(),
        end_time=datetime.now().time(),
        duration=3600,
        location="Test Location",
        is_online=False,
        is_published=True,
        access_level="public",
        created_by_id=test_user.id,
        status="done",
        processing_progress=100
    )
    db_session.add(meeting)
    db_session.commit()
    return meeting

@pytest.fixture
def test_participant(db_session, test_meeting, test_user):
    """Add a test participant to the meeting"""
    test_meeting.participants.append(test_user)
    db_session.commit()
    return test_user

@pytest.fixture
def test_tag(db_session, test_meeting):
    """Create a test tag"""
    tag = Tag(
        label="test"
    )
    db_session.add(tag)
    test_meeting.tags.append(tag)
    db_session.commit()
    return tag

@pytest.fixture
def test_audio_file():
    """Create a temporary test audio file"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(b"dummy audio content")
        return f.name

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up any test files after each test"""
    yield
    for file in os.listdir(tempfile.gettempdir()):
        if file.endswith(".wav") or file.endswith(".mp3"):
            try:
                os.remove(os.path.join(tempfile.gettempdir(), file))
            except:
                pass

@pytest.fixture
def user_token(test_user):
    """Create an access token for the test user"""
    return create_access_token({"sub": test_user.email}) 