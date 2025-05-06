import pytest
from datetime import datetime, date, time
from models import User, Meeting, Tag
from models.user import UserRole
from models.meeting import AccessLevel, MeetingStatus

def test_user_model():
    """Test User model validation"""
    # Test valid user
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        is_active=True,
        role="user"
    )
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.is_active == True
    assert user.role == "user"

    # Test invalid email
    with pytest.raises(ValueError):
        User(
            email="invalid-email",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            is_active=True,
            role="user"
        )

def test_meeting_model():
    """Test Meeting model validation"""
    # Test valid meeting
    meeting = Meeting(
        title="Test Meeting",
        date=datetime.now().date(),
        start_time=datetime.now().time(),
        end_time=datetime.now().time(),
        duration=3600,
        location="Test Location",
        is_online=False,
        is_published=False,
        access_level="private",
        created_by_id=1,
        status="pending"
    )
    assert meeting.title == "Test Meeting"
    assert meeting.is_online == False
    assert meeting.is_published == False
    assert meeting.access_level == "private"
    assert meeting.status == "pending"

    # Test invalid date
    with pytest.raises(ValueError):
        Meeting(
            title="Test Meeting",
            date="invalid-date",
            start_time=datetime.now().time(),
            end_time=datetime.now().time(),
            duration=3600,
            location="Test Location",
            is_online=False,
            is_published=False,
            access_level="private",
            created_by_id=1,
            status="pending"
        )

def test_meeting_participants():
    """Test meeting participants relationship"""
    meeting = Meeting(
        title="Test Meeting",
        date=datetime.now().date(),
        start_time=datetime.now().time(),
        end_time=datetime.now().time(),
        duration=3600,
        location="Test Location",
        is_online=False,
        is_published=False,
        access_level="private",
        created_by_id=1,
        status="pending"
    )
    
    user1 = User(
        email="user1@example.com",
        password_hash="hashed_password",
        first_name="User",
        last_name="One",
        is_active=True,
        role="user"
    )
    
    user2 = User(
        email="user2@example.com",
        password_hash="hashed_password",
        first_name="User",
        last_name="Two",
        is_active=True,
        role="user"
    )
    
    meeting.participants.append(user1)
    meeting.participants.append(user2)
    
    assert len(meeting.participants) == 2
    assert user1 in meeting.participants
    assert user2 in meeting.participants

def test_tag_model():
    """Test Tag model validation"""
    # Test valid tag
    tag = Tag(label="test")
    assert tag.label == "test"

    # Test invalid label
    with pytest.raises(ValueError):
        Tag(label="")

def test_meeting_relationships():
    """Test meeting relationships"""
    meeting = Meeting(
        title="Test Meeting",
        date=datetime.now().date(),
        start_time=datetime.now().time(),
        end_time=datetime.now().time(),
        duration=3600,
        location="Test Location",
        is_online=False,
        is_published=False,
        access_level="private",
        created_by_id=1,
        status="pending"
    )
    
    tag1 = Tag(label="tag1")
    tag2 = Tag(label="tag2")
    
    meeting.tags.append(tag1)
    meeting.tags.append(tag2)
    
    assert len(meeting.tags) == 2
    assert tag1 in meeting.tags
    assert tag2 in meeting.tags

def test_meeting_status_transitions():
    """Test meeting status transitions"""
    meeting = Meeting(
        title="Test Meeting",
        date=datetime.now().date(),
        start_time=datetime.now().time(),
        end_time=datetime.now().time(),
        duration=3600,
        location="Test Location",
        is_online=False,
        is_published=False,
        access_level="private",
        created_by_id=1,
        status="pending"
    )
    
    assert meeting.status == "pending"
    meeting.status = "processing"
    assert meeting.status == "processing"
    meeting.status = "done"
    assert meeting.status == "done"

def test_meeting_access_levels():
    """Test meeting access levels"""
    meeting = Meeting(
        title="Test Meeting",
        date=datetime.now().date(),
        start_time=datetime.now().time(),
        end_time=datetime.now().time(),
        duration=3600,
        location="Test Location",
        is_online=False,
        is_published=False,
        access_level="private",
        created_by_id=1,
        status="pending"
    )
    
    assert meeting.access_level == "private"
    meeting.access_level = "restricted"
    assert meeting.access_level == "restricted"
    meeting.access_level = "public"
    assert meeting.access_level == "public" 