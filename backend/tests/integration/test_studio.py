import pytest
from fastapi import status
from backend.app import app
from fastapi.testclient import TestClient
from database import get_db
from models import User, Meeting
from .conftest import create_user_and_token, create_access_token
from datetime import datetime
import tempfile

client = TestClient(app)

def create_editor_user_and_token(db):
    user = User(
        email="editor@example.com",
        password_hash="hashed_password",
        first_name="Editor",
        last_name="User",
        is_active=True,
        role="editor"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return user, token

def create_studio_meeting(db, user):
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
        created_by_id=user.id,
        status="pending"
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

def test_create_meeting_draft(db_session):
    user, token = create_editor_user_and_token(db_session)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.post(
        "/api/v1/studio/meetings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "New Meeting",
            "date": "2024-03-20",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "location": "Conference Room"
        }
    )
    app.dependency_overrides = {}
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Meeting"
    assert data["status"] == "draft"

def test_upload_meeting_file(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(b"dummy audio content")
        f.flush()
        f.seek(0)
        response = client.post(
            f"/api/v1/studio/meetings/{meeting.id}/files",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.wav", open(f.name, "rb"), "audio/wav")}
        )
    app.dependency_overrides = {}
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.wav"
    assert data["file_type"] == "audio"

def test_start_meeting_processing(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.post(
        f"/api/v1/studio/meetings/{meeting.id}/process",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "processing"

def test_get_editor_data(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        f"/api/v1/studio/meetings/{meeting.id}/editor",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == 200
    data = response.json()
    assert "transcript" in data
    assert "summary" in data
    assert "protocol" in data

def test_update_editor_data(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.put(
        f"/api/v1/studio/meetings/{meeting.id}/editor",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "transcript": "Updated transcript",
            "summary": "Updated summary",
            "protocol": "Updated protocol"
        }
    )
    app.dependency_overrides = {}
    assert response.status_code == 200
    data = response.json()
    assert data["transcript"] == "Updated transcript"
    assert data["summary"] == "Updated summary"
    assert data["protocol"] == "Updated protocol"

def test_publish_meeting(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.post(
        f"/api/v1/studio/meetings/{meeting.id}/publish",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == 200
    data = response.json()
    assert data["is_published"] == True
    assert data["status"] == "done"

def test_access_control(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    # Test unauthorized access
    response = client.get(
        f"/api/v1/studio/meetings/{meeting.id}/editor",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    # Test access to non-existent meeting
    response = client.get(
        "/api/v1/studio/meetings/999/editor",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404 