import tempfile
from fastapi import status
from datetime import datetime
from backend.app import app
from fastapi.testclient import TestClient
from database import get_db
from models import Meeting, User
from .conftest import create_user_and_token
from utils.auth import create_access_token

client = TestClient(app)

def create_meeting(db, user):
    meeting = Meeting(
        title="Integration Meeting",
        date=datetime.now().date(),
        start_time=datetime.strptime("10:00:00", "%H:%M:%S").time(),
        end_time=datetime.strptime("11:00:00", "%H:%M:%S").time(),
        duration=3600,
        location="Integration Room",
        is_online=False,
        is_published=False,
        access_level="public",
        created_by_id=user.id,
        status="pending"
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

def test_create_meeting_integration(db_session):
    user, token = create_user_and_token(db_session)
    print(f"[DEBUG] user.id={user.id}, token={token}")
    meeting_data = {
        "title": "Integration Meeting",
        "date": datetime.now().isoformat(),
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "location": "Integration Room",
        "is_online": False,
        "access_level": "public",
        "description": "Test meeting description"
    }
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.post(
        "/api/v1/meetings",
        json=meeting_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_201_CREATED

def test_get_meeting_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        f"/api/v1/meetings/{meeting.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_200_OK

def test_update_meeting_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    update_data = {
        "title": "Updated Integration Meeting",
        "location": "Updated Room"
    }
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.put(
        f"/api/v1/meetings/{meeting.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["location"] == update_data["location"]

def test_delete_meeting_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.delete(
        f"/api/v1/meetings/{meeting.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_upload_audio_integration(db_session):
    # Create an editor user instead of a regular user
    user = User(
        email="editor@example.com",
        password_hash="hashed_password",
        first_name="Editor",
        last_name="User",
        is_active=True,
        role="editor"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(b"dummy audio content")
        f.flush()
        f.seek(0)
        response = client.post(
            f"/api/v1/studio/meetings/{meeting.id}/upload-file",
            files={"file": ("test.wav", open(f.name, "rb"), "audio/wav")},
            headers={"Authorization": f"Bearer {token}"}
        )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
    data = response.json()
    assert "id" in data
    assert "url" in data
    assert data["url"].endswith(".wav")

def test_get_meeting_transcript_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        f"/api/v1/meetings/{meeting.id}/transcript",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_200_OK, 404)

def test_get_meeting_summary_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        f"/api/v1/meetings/{meeting.id}/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_200_OK, 404)

def test_get_meeting_protocol_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        f"/api/v1/meetings/{meeting.id}/protocol",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_200_OK, 404)

def test_chat_answer_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.post(
        f"/api/v1/meetings/{meeting.id}/chat",
        json={"question": "What was discussed?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_200_OK, 404)

def test_meeting_list_pagination_integration(db_session):
    user, token = create_user_and_token(db_session)
    for _ in range(3):
        create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        "/api/v1/meetings/?skip=0&limit=2",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_200_OK, 404)

def test_meeting_search_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        "/api/v1/meetings",
        params={"search": meeting.title},
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_200_OK, 404)

def test_meeting_filters_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        f"/api/v1/meetings/?status={meeting.status}&access_level={meeting.access_level}",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_200_OK, 404)

def test_invalid_meeting_id_integration(db_session):
    user, token = create_user_and_token(db_session)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        "/api/v1/meetings/999999",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_invalid_audio_file_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.post(
        f"/api/v1/meetings/{meeting.id}/audio",
        files={"file": ("test.txt", b"invalid content", "text/plain")},
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_invalid_chat_question_integration(db_session):
    user, token = create_user_and_token(db_session)
    meeting = create_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.post(
        f"/api/v1/meetings/{meeting.id}/chat",
        json={"question": ""},
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_400_BAD_REQUEST 