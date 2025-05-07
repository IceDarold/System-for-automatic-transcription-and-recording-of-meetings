import pytest
from fastapi import status
from datetime import datetime, date, time
from pathlib import Path
from models.user import UserRole # For role checking
from models.meeting import AccessLevel, MeetingStatus # For payloads and assertions
from models.file import File as DBFileModel, FileType as DBFileType

# Assume client, user_factory, auth_headers_factory, meeting_factory, db_session, tmp_file_factory are available from conftest

# --- Helper for creating users with specific roles ---
def create_studio_user(user_factory, role: UserRole, email_suffix: str):
    return user_factory(email=f"studio_{role.value}_{email_suffix}@example.com", role=role.value)

# --- Tests for POST /api/v1/studio/meetings (create_meeting_draft) ---
@pytest.mark.parametrize(
    "actor_role, expected_status",
    [
        (UserRole.editor, status.HTTP_201_CREATED),
        (UserRole.superadmin, status.HTTP_201_CREATED),
        (UserRole.user, status.HTTP_403_FORBIDDEN), # Regular user cannot create studio drafts
    ]
)
def test_create_meeting_draft_access_control(client, user_factory, auth_headers_factory, actor_role, expected_status):
    actor = create_studio_user(user_factory, actor_role, "createdraft")
    headers = auth_headers_factory(actor)
    
    payload = {
        "title": f"Studio Draft by {actor_role.value}",
        "date": date(2024, 8, 1).isoformat(),
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "access_level": AccessLevel.private.value
    }
    response = client.post("/api/v1/studio/meetings", json=payload, headers=headers)
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["status"] == MeetingStatus.pending.value # Should be draft/pending
        assert data["created_by_id"] == actor.id

def test_create_meeting_draft_unauthenticated(client):
    payload = {"title": "Unauth Draft", "date": date(2024, 8, 1).isoformat()}
    response = client.post("/api/v1/studio/meetings", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# --- Tests for POST /api/v1/studio/meetings/{meeting_id}/upload-file ---
@pytest.mark.parametrize(
    "creator_role, uploader_role, is_owner, expected_status",
    [
        (UserRole.editor, UserRole.editor, True, status.HTTP_201_CREATED),      # Editor uploads to own meeting
        (UserRole.editor, UserRole.superadmin, False, status.HTTP_201_CREATED), # Superadmin uploads to editor's meeting
        (UserRole.editor, UserRole.editor, False, status.HTTP_403_FORBIDDEN),   # Editor uploads to another editor's meeting (if not allowed by check_meeting_owner)
        (UserRole.editor, UserRole.user, True, status.HTTP_403_FORBIDDEN),       # User (non-editor) tries to upload
    ]
)
def test_studio_upload_file_access_control(client, user_factory, auth_headers_factory, meeting_factory, tmp_file_factory, creator_role, uploader_role, is_owner, expected_status):
    creator = create_studio_user(user_factory, creator_role, "uploadcreator")
    
    if is_owner:
        uploader = creator
    else:
        uploader = create_studio_user(user_factory, uploader_role, "uploader")
        
    headers = auth_headers_factory(uploader)
    studio_meeting = meeting_factory(created_by_user=creator, title="Studio Upload Target", status=MeetingStatus.pending)
    
    tmp_file_path = tmp_file_factory(filename="studio_audio.mp3", content=b"dummy studio audio")

    with open(tmp_file_path, "rb") as f:
        response = client.post(
            f"/api/v1/studio/meetings/{studio_meeting.id}/upload-file", 
            files={"file": (Path(tmp_file_path).name, f, "audio/mpeg")},
            headers=headers
        )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        data = response.json()
        assert "id" in data # file ID from DBFile
        assert "url" in data

def test_studio_upload_file_unauthenticated(client, tmp_file_factory):
    tmp_file_path = tmp_file_factory(filename="unauth_audio.mp3", content=b"dummy")
    with open(tmp_file_path, "rb") as f:
        response = client.post("/api/v1/studio/meetings/1/upload-file", files={"file": (Path(tmp_file_path).name, f, "audio/mpeg")})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# --- Tests for POST /api/v1/studio/meetings/{meeting_id}/process ---
@pytest.mark.parametrize(
    "creator_role, processor_role, is_owner, initial_meeting_status, has_audio_file, expected_status",
    [
        (UserRole.editor, UserRole.editor, True, MeetingStatus.pending, True, status.HTTP_202_ACCEPTED),      # Editor processes own pending meeting with audio
        (UserRole.editor, UserRole.superadmin, False, MeetingStatus.pending, True, status.HTTP_202_ACCEPTED), # Superadmin processes editor's meeting
        (UserRole.editor, UserRole.editor, False, MeetingStatus.pending, True, status.HTTP_403_FORBIDDEN),  # Editor processes another editor's meeting
        (UserRole.editor, UserRole.user, True, MeetingStatus.pending, True, status.HTTP_403_FORBIDDEN),      # User (non-editor) tries to process
        (UserRole.editor, UserRole.editor, True, MeetingStatus.processing, True, status.HTTP_400_BAD_REQUEST),# Already processing
        (UserRole.editor, UserRole.editor, True, MeetingStatus.pending, False, status.HTTP_400_BAD_REQUEST), # No audio file
    ]
)
def test_studio_process_meeting_access_and_validation(
    client, user_factory, auth_headers_factory, meeting_factory, db_session, # Add db_session if meeting_factory doesn't set audio_file_id
    creator_role, processor_role, is_owner, initial_meeting_status, has_audio_file, expected_status
):
    creator = create_studio_user(user_factory, creator_role, "processcreator")
    processor = creator if is_owner else create_studio_user(user_factory, processor_role, "processor")
    headers = auth_headers_factory(processor)
    
    studio_meeting = meeting_factory(created_by_user=creator, title="Studio Process Target", status=initial_meeting_status)
    if has_audio_file:
        # This assumes meeting_factory can link/create a dummy audio file ID or we do it manually
        # For simplicity, let's assume it does for now, or this needs adjustment.
        # If you have a FileModel and can create one:
        # dummy_file = FileModel(filename="dummy.wav", mime_type="audio/wav", size=123, url="/files/dummy.wav", storage_path="dummy.wav", meeting_id=studio_meeting.id)
        # db_session.add(dummy_file)
        # db_session.flush()
        # studio_meeting.audio_file_id = dummy_file.id
        # db_session.commit()
        pass # Placeholder: Ensure meeting has an audio_file_id if has_audio_file is True
        if not studio_meeting.audio_file_id: # If meeting_factory doesn't set it
             # Create a dummy FileModel record and link it
             dummy_audio = DBFileModel(filename="test.wav", file_type=DBFileType.audio, mime_type="audio/wav", size=100, url="/files/test.wav", storage_path="dummy/test.wav", meeting_id=studio_meeting.id)
             db_session.add(dummy_audio)
             db_session.commit() # Commit to get ID
             studio_meeting.audio_file_id = dummy_audio.id
             db_session.commit()
             db_session.refresh(studio_meeting)

    response = client.post(f"/api/v1/studio/meetings/{studio_meeting.id}/process", headers=headers)
    assert response.status_code == expected_status
    if expected_status == status.HTTP_202_ACCEPTED:
        data = response.json()
        assert data["status"] == "processing_started"
        db_session.refresh(studio_meeting)
        assert studio_meeting.status == MeetingStatus.processing

def test_studio_process_meeting_unauthenticated(client):
    response = client.post("/api/v1/studio/meetings/1/process")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# --- Placeholder for GET /editor, PUT /editor, POST /publish --- 
# These will follow a similar pattern: access control, unauthenticated, valid/invalid data for PUT

@pytest.mark.skip(reason="GET /editor tests not yet implemented")
def test_studio_get_editor_data_access_control(): pass

@pytest.mark.skip(reason="PUT /editor tests not yet implemented")
def test_studio_update_editor_data_access_control(): pass

@pytest.mark.skip(reason="PUT /editor data validation tests not yet implemented")
def test_studio_update_editor_data_validation(): pass

@pytest.mark.skip(reason="POST /publish tests not yet implemented")
def test_studio_publish_meeting_access_control(): pass

# Add unauthenticated tests for GET /editor, PUT /editor, POST /publish as well
@pytest.mark.skip(reason="Unauthenticated GET /editor test not yet implemented")
def test_studio_get_editor_data_unauthenticated(): pass

@pytest.mark.skip(reason="Unauthenticated PUT /editor test not yet implemented")
def test_studio_update_editor_data_unauthenticated(): pass

@pytest.mark.skip(reason="Unauthenticated POST /publish test not yet implemented")
def test_studio_publish_meeting_unauthenticated(): pass

# Need to ensure Path is imported if used: from pathlib import Path 