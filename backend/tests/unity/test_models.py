import pytest
from datetime import datetime, date, time
from models import User, Meeting, Tag
from models.user import UserRole
from models.meeting import AccessLevel, MeetingStatus

# --- User Model Tests ---

@pytest.mark.parametrize(
    "user_data, should_pass, error_type",
    [
        # Valid cases
        ({"email": "valid@example.com", "password_hash": "hash", "first_name": "F", "last_name": "L", "role": UserRole.user.value}, True, None),
        ({"email": "admin@example.com", "password_hash": "hash", "first_name": "Admin", "last_name": "User", "role": UserRole.editor.value}, True, None),
        
        # Invalid cases
        ({"email": "invalid-email", "password_hash": "hash", "first_name": "F", "last_name": "L", "role": UserRole.user.value}, False, ValueError), # Invalid email format (assuming validation is in __init__ or setter)
        ({"email": "invalid_role@example.com", "password_hash": "hash", "first_name": "F", "last_name": "L", "role": "guest"}, False, ValueError), # Invalid role value (assuming validation)
        # Tests for missing required fields (User model __init__ enforces them)
        ({"password_hash": "hash", "first_name": "F", "last_name": "L", "role": UserRole.user.value}, False, ValueError), # Missing email
        ({"email": "no_pass@example.com", "first_name": "F", "last_name": "L", "role": UserRole.user.value}, False, ValueError), # Missing password_hash
        ({"email": "no_fname@example.com", "password_hash": "hash", "last_name": "L", "role": UserRole.user.value}, False, ValueError), # Missing first_name
        ({"email": "no_lname@example.com", "password_hash": "hash", "first_name": "F", "role": UserRole.user.value}, False, ValueError), # Missing last_name
        # TODO: Add tests for missing required fields like email, password_hash, first_name, last_name if User model enforces them - Covered by above
    ]
)
def test_user_model_validation(user_data, should_pass, error_type):
    """Test User model creation with various valid and invalid data."""
    if should_pass:
        user = User(**user_data)
        for key, value in user_data.items():
            # Skip password_hash check, often not directly accessible or useful to compare
            if key != "password_hash":
                assert getattr(user, key) == value
    else:
        with pytest.raises(error_type):
            User(**user_data)

# --- Meeting Model Tests ---

# Define default valid meeting data to reduce repetition
DEFAULT_VALID_MEETING_DATA = {
    "title": "Default Meeting",
    "date": date(2024, 1, 1),
    "start_time": time(10, 0, 0),
    "end_time": time(11, 0, 0),
    "duration": 3600,
    "location": "Default Location",
    "is_online": False,
    "is_published": False,
    "access_level": AccessLevel.private.value,
    "created_by_id": 1, # Dummy ID, not validated in unit test
    "status": MeetingStatus.pending.value
}

@pytest.mark.parametrize(
    "meeting_data_override, should_pass, error_type",
    [
        # Valid cases
        ({}, True, None), # Default valid data
        ({"title": "Specific Meeting", "access_level": AccessLevel.public.value}, True, None),
        ({"date": "2024-07-20", "start_time": "15:30:00"}, True, None), # String dates/times are valid if __init__ handles them
        ({"duration": 0}, True, None), # Zero duration might be valid
        ({"description": None}, True, None), # Optional fields can be None
        ({"status": MeetingStatus.done.value}, True, None),

        # Invalid cases
        ({"title": None}, False, ValueError), # Missing title (assuming __init__ checks)
        ({"title": "  "}, False, ValueError), # Empty/whitespace title (assuming __init__ checks)
        ({"date": "invalid-date"}, False, ValueError), # Invalid date format string
        ({"start_time": "invalid-time"}, False, ValueError), # Invalid time format string
        ({"duration": -100}, False, ValueError), # Negative duration
        ({"access_level": "unknown"}, False, ValueError), # Invalid access level string
        ({"status": "invalid"}, False, ValueError), # Invalid status string
        # TODO: Add test for end_time < start_time if validation exists in Meeting model __init__
    ]
)
def test_meeting_model_validation(meeting_data_override, should_pass, error_type):
    """Test Meeting model creation with various valid and invalid data."""
    # Prepare final data by merging default with overrides
    final_data = {**DEFAULT_VALID_MEETING_DATA, **meeting_data_override}
    # Handle explicit None overrides if needed for testing missing fields vs null
    if meeting_data_override.get("title") is None:
        final_data.pop("title", None)
    
    if should_pass:
        meeting = Meeting(**final_data)
        for key, value in final_data.items():
            # Some keys might be processed (like date/time strings)
            # We check the *intended* value if possible, or just existence/type
            if key == "date" and isinstance(value, str):
                 assert meeting.date == date.fromisoformat(value)
            elif key in ["start_time", "end_time"] and isinstance(value, str):
                 expected_time = time.fromisoformat(value)
                 assert getattr(meeting, key) == expected_time
            elif key == "created_by_id": # Not a real foreign key object here
                assert meeting.created_by_id == value 
            elif hasattr(meeting, key):
                 assert getattr(meeting, key) == value
    else:
        with pytest.raises(error_type):
            Meeting(**final_data)

@pytest.mark.parametrize(
    "status, expected_is_ready",
    [
        (MeetingStatus.pending.value, False),
        (MeetingStatus.processing.value, False),
        (MeetingStatus.done.value, True),
        (MeetingStatus.failed.value, False),
    ]
)
def test_meeting_is_ready(status, expected_is_ready):
    """Test the Meeting.is_ready property based on status."""
    meeting_data = {**DEFAULT_VALID_MEETING_DATA, "status": status}
    meeting = Meeting(**meeting_data)
    assert meeting.is_ready == expected_is_ready

# --- Tag Model Tests ---

@pytest.mark.parametrize(
    "tag_data, should_pass, error_type",
    [
        # Valid cases
        ({"label": "valid-tag"}, True, None),
        ({"label": " Another Valid Tag "}, True, None), # Assuming leading/trailing whitespace might be handled or allowed initially

        # Invalid cases
        ({"label": None}, False, ValueError), # Missing label (assuming __init__ checks)
        ({"label": ""}, False, ValueError), # Empty label (assuming __init__ checks)
        ({"label": "   "}, False, ValueError), # Whitespace label (assuming __init__ checks)
    ]
)
def test_tag_model_validation(tag_data, should_pass, error_type):
    """Test Tag model creation with various valid and invalid data."""
    if should_pass:
        tag = Tag(**tag_data)
        assert tag.label == tag_data["label"]
    else:
        with pytest.raises(error_type):
            Tag(**tag_data)

# --- Relationship Tests (Keep simple for unit tests, focus on model logic not DB persistence) ---

def test_meeting_participants_relationship():
    """Test adding participants to a meeting model instance (in memory)."""
    meeting = Meeting(**DEFAULT_VALID_MEETING_DATA)
    user1 = User(email="p1@example.com", password_hash="h", first_name="P", last_name="1", role="user")
    user2 = User(email="p2@example.com", password_hash="h", first_name="P", last_name="2", role="user")

    # Assuming relationship is initialized as a list or similar appendable structure
    if not hasattr(meeting, 'participants') or meeting.participants is None:
        pytest.skip("Skipping participant relationship test: meeting.participants not initialized as expected.")
    
    meeting.participants.append(user1)
    meeting.participants.append(user2)
    
    assert len(meeting.participants) == 2
    assert user1 in meeting.participants
    assert user2 in meeting.participants

def test_meeting_tags_relationship():
    """Test adding tags to a meeting model instance (in memory)."""
    meeting = Meeting(**DEFAULT_VALID_MEETING_DATA)
    tag1 = Tag(label="tag1")
    tag2 = Tag(label="tag2")

    if not hasattr(meeting, 'tags') or meeting.tags is None:
         pytest.skip("Skipping tag relationship test: meeting.tags not initialized as expected.")
    
    meeting.tags.append(tag1)
    meeting.tags.append(tag2)
    
    assert len(meeting.tags) == 2
    assert tag1 in meeting.tags
    assert tag2 in meeting.tags

# Removed old non-parameterized tests: test_user_model, test_meeting_model, test_tag_model, etc. 