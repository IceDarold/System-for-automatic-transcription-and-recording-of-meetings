import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app import app
from models.user import User, UserRole
from models.meeting import Meeting, MeetingStatus, AccessLevel
from core.auth import create_access_token

client = TestClient(app)

@pytest.fixture
def editor_user(db: Session):
    user = User(
        email="editor@test.com",
        first_name="Editor",
        last_name="Test",
        role=UserRole.editor,
        password_hash="hashed_password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def editor_token(editor_user):
    return create_access_token({"sub": editor_user.id, "role": editor_user.role})

@pytest.fixture
def test_meeting(db: Session, editor_user):
    meeting = Meeting(
        title="Test Meeting",
        date=datetime.now(),
        status=MeetingStatus.pending,
        created_by_id=editor_user.id,
        access_level=AccessLevel.private
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

def test_create_meeting_draft(editor_token):
    response = client.post(
        "/api/v1/meetings",
        headers={"Authorization": f"Bearer {editor_token}"},
        data={
            "title": "New Meeting",
            "date": datetime.now().isoformat(),
            "short_description": "Test meeting"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Meeting"
    assert data["status"] == MeetingStatus.pending

def test_upload_meeting_file(editor_token, test_meeting):
    # Create a test audio file
    test_file = ("test.wav", b"test audio content", "audio/wav")
    
    response = client.post(
        f"/api/v1/meetings/{test_meeting.id}/files",
        headers={"Authorization": f"Bearer {editor_token}"},
        files={"file": test_file}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "url" in data

def test_start_meeting_processing(editor_token, test_meeting):
    response = client.post(
        f"/api/v1/meetings/{test_meeting.id}/start",
        headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert response.status_code == 400  # Should fail without audio file
    
    # Add audio file and try again
    test_file = ("test.wav", b"test audio content", "audio/wav")
    client.post(
        f"/api/v1/meetings/{test_meeting.id}/files",
        headers={"Authorization": f"Bearer {editor_token}"},
        files={"file": test_file}
    )
    
    response = client.post(
        f"/api/v1/meetings/{test_meeting.id}/start",
        headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing_started"

def test_get_editor_data(editor_token, test_meeting):
    response = client.get(
        f"/api/v1/meetings/{test_meeting.id}/editor",
        headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_meeting.id
    assert data["title"] == test_meeting.title

def test_update_editor_data(editor_token, test_meeting):
    update_data = {
        "transcript": [
            {
                "speaker": None,
                "start": 0.0,
                "end": 5.0,
                "text": "Test transcript",
                "confidence": 0.95,
                "language": "ru"
            }
        ],
        "summary": "Test summary",
        "protocol": "Test protocol"
    }
    
    response = client.put(
        f"/api/v1/meetings/{test_meeting.id}/editor",
        headers={"Authorization": f"Bearer {editor_token}"},
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "updated"

def test_publish_meeting(editor_token, test_meeting):
    # First add required content
    update_data = {
        "transcript": [
            {
                "speaker": None,
                "start": 0.0,
                "end": 5.0,
                "text": "Test transcript",
                "confidence": 0.95,
                "language": "ru"
            }
        ],
        "summary": "Test summary",
        "protocol": "Test protocol"
    }
    
    client.put(
        f"/api/v1/meetings/{test_meeting.id}/editor",
        headers={"Authorization": f"Bearer {editor_token}"},
        json=update_data
    )
    
    # Try to publish
    response = client.post(
        f"/api/v1/meetings/{test_meeting.id}/publish",
        headers={"Authorization": f"Bearer {editor_token}"},
        data={"access_level": AccessLevel.public}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"

def test_access_control(editor_token, test_meeting):
    # Create regular user
    regular_user = User(
        email="user@test.com",
        first_name="Regular",
        last_name="User",
        role=UserRole.user,
        password_hash="hashed_password"
    )
    db.add(regular_user)
    db.commit()
    regular_token = create_access_token({"sub": regular_user.id, "role": regular_user.role})
    
    # Try to access studio endpoints
    response = client.post(
        "/api/v1/meetings",
        headers={"Authorization": f"Bearer {regular_token}"},
        data={
            "title": "New Meeting",
            "date": datetime.now().isoformat()
        }
    )
    assert response.status_code == 403
    
    response = client.get(
        f"/api/v1/meetings/{test_meeting.id}/editor",
        headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 403 