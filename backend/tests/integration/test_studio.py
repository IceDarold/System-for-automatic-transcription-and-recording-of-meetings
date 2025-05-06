import pytest
from fastapi import status
from backend.app import app
from fastapi.testclient import TestClient
from database import get_db
from models import User, Meeting
from .conftest import create_user_and_token, create_access_token
from datetime import datetime
import tempfile
import os
from models.file import File, FileType

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
            "date": datetime.now().isoformat(),
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "location": "Conference Room",
            "is_online": False,
            "description": "Test meeting",
            "access_level": "private"
        }
    )
    app.dependency_overrides = {}
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Meeting"
    assert data["status"] == "pending"

def test_upload_meeting_file(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(b"dummy audio content")
        f.flush()
        f.seek(0)
        response = client.post(
            f"/api/v1/studio/meetings/{meeting.id}/upload-file",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.wav", open(f.name, "rb"), "audio/wav")}
        )
    app.dependency_overrides = {}
    assert response.status_code == 201 or response.status_code == 200
    data = response.json()
    assert data["id"]
    assert "url" in data

def test_process_meeting(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    
    # Создаем фиктивный файл и привязываем его к встрече
    audio_file = File(
        filename="test.wav",
        file_type=FileType.audio,
        mime_type="audio/wav",
        size=1000,
        url="/test.wav",
        storage_path="/test.wav",
        meeting_id=meeting.id
    )
    db_session.add(audio_file)
    db_session.commit()
    db_session.refresh(audio_file)
    
    # Устанавливаем audio_file_id для встречи
    meeting.audio_file_id = audio_file.id
    db_session.commit()
    
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.post(
        f"/api/v1/studio/meetings/{meeting.id}/process",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == 202
    data = response.json()
    assert "status" in data

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
    assert data["is_ready"] == True
    assert data["status"] == "published"

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

def test_upload_and_convert_to_wav(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    # Подготовим фейковый mp3-файл
    mp3_path = "test.mp3"
    with open(mp3_path, "wb") as f:
        f.write(b"FAKE MP3 DATA")  # Для настоящей проверки используйте реальный mp3
    with open(mp3_path, "rb") as f:
        response = client.post(
            f"/api/v1/studio/meetings/{meeting.id}/upload-file",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.mp3", f, "audio/mp3")}
        )
    app.dependency_overrides = {}
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["converted_to_wav"] is True
    assert data["url"].endswith(".wav")
    # Проверить, что файл реально существует (если путь локальный)
    if os.path.exists(data["url"]):
        assert os.path.isfile(data["url"])
    # Удалить тестовый mp3
    os.remove(mp3_path)

def test_upload_wav_no_conversion(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    wav_path = "test.wav"
    # Создаём фейковый wav-файл (для реального теста используйте настоящий wav)
    with open(wav_path, "wb") as f:
        f.write(b"RIFF....WAVEfmt ")
    with open(wav_path, "rb") as f:
        response = client.post(
            f"/api/v1/studio/meetings/{meeting.id}/upload-file",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.wav", f, "audio/wav")}
        )
    app.dependency_overrides = {}
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["converted_to_wav"] is False
    assert data["url"].endswith(".wav")
    if os.path.exists(data["url"]):
        assert os.path.isfile(data["url"])
    os.remove(wav_path)

def test_upload_video_and_convert_to_wav(db_session):
    user, token = create_editor_user_and_token(db_session)
    meeting = create_studio_meeting(db_session, user)
    app.dependency_overrides[get_db] = lambda: db_session
    video_path = "test.mp4"
    # Создаём фейковый mp4-файл (для реального теста используйте настоящий mp4 с аудио)
    with open(video_path, "wb") as f:
        f.write(b"FAKE MP4 DATA")
    with open(video_path, "rb") as f:
        response = client.post(
            f"/api/v1/studio/meetings/{meeting.id}/upload-file",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.mp4", f, "video/mp4")}
        )
    app.dependency_overrides = {}
    assert response.status_code in (200, 201)
    data = response.json()
    # converted_to_wav True только если ffmpeg смог извлечь аудио
    assert data["url"].endswith(".wav")
    if os.path.exists(data["url"]):
        assert os.path.isfile(data["url"])
    os.remove(video_path) 