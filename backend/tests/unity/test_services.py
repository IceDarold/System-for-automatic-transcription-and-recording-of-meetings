import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import os
from pathlib import Path
from fastapi import UploadFile
from io import BytesIO
import shutil
import httpx # Added for httpx specific exceptions
import json # Added for json.JSONDecodeError
from typing import Optional

from models import User, Meeting, File
from models.user import UserRole
from models.meeting import AccessLevel, MeetingStatus
from core.storage import save_file
from core.model_api import ModelAPIClient, model_api, ModelAPIError
from core.config import settings
from models.file import FileType
from sqlalchemy.orm import Session

@pytest.fixture
def mock_audio_file_path(tmp_path: Path) -> str:
    """Create a temporary dummy audio file using tmp_path and return its path string."""
    audio_file = tmp_path / "test_audio_fixture.wav"
    audio_file.write_bytes(b"dummy audio content for model_api tests")
    return str(audio_file)

@pytest.mark.asyncio
async def test_transcribe_audio_success(mock_audio_file_path):
    """Test transcription service success and call arguments."""
    expected_response_data = [{"text": "Test transcript", "start": 0, "end": 1}]
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.return_value = expected_response_data
        
        result = await model_api.transcribe_audio(mock_audio_file_path)
        
        assert result == expected_response_data
        mock_make_request.assert_called_once() 
        
        args, kwargs = mock_make_request.call_args
        assert kwargs.get("method") == "POST"
        assert kwargs.get("endpoint") == "/transcribe"
        assert "files" in kwargs
        assert kwargs.get("timeout") == settings.MODEL_API_TIMEOUT

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_transcript, mock_api_response, expected_service_result",
    [
        # Basic case
        ([{"text": "This is a short transcript.", "start": 0, "end": 1}], 
         {"summary": "Short transcript summary."}, 
         "Short transcript summary."),
        # Longer transcript
        ([{"text": "First part.", "start": 0, "end": 1}, {"text": "Second part.", "start": 1, "end": 2}], 
         {"summary": "Summary of two parts."}, 
         "Summary of two parts."),
        # Transcript with no text (edge case, depends on how API handles it)
        ([{"text": "", "start": 0, "end": 1}], 
         {"summary": "Summary of empty text."}, 
         "Summary of empty text."),
        # API returns slightly different structure but service extracts correctly
        ([{"text": "Data for summary."}], # Missing start/end, if service handles it
         {"summary": "Summary from data.", "keywords": ["data", "summary"]}, 
         "Summary from data."),
    ]
)
async def test_generate_summary_success_parametrized(test_transcript, mock_api_response, expected_service_result):
    """Test summarization service with various transcripts and responses."""
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.return_value = mock_api_response
        
        result = await model_api.generate_summary(test_transcript)
        
        assert result == expected_service_result
        mock_make_request.assert_called_once_with(
            method="POST", 
            endpoint="/summarize", 
            json_data={"transcript": test_transcript},
            timeout=settings.MODEL_API_TIMEOUT
        )

@pytest.mark.asyncio
async def test_detect_speakers_success(mock_audio_file_path):
    """Test speaker diarization service success and call arguments."""
    test_transcript = [{"text": "Hello world from a speaker.", "start": 0, "end": 1}]
    expected_response_data = [{"speaker": "Speaker 1", "text": "Hello world from a speaker."}]
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.return_value = expected_response_data
        
        result = await model_api.detect_speakers(test_transcript, mock_audio_file_path)
        
        assert result == expected_response_data
        mock_make_request.assert_called_once() 
        
        args, kwargs = mock_make_request.call_args
        assert kwargs.get("method") == "POST"
        assert kwargs.get("endpoint") == "/diarize" # TODO: Verify model-api endpoint for diarization
        assert kwargs.get("json_data") == {"transcript": test_transcript}
        assert "files" in kwargs # Check that files argument was passed (for audio)
        # Example of a more specific check on the file part if the key is known, e.g., 'audio_file':
        # files_dict = kwargs["files"]
        # assert "audio_file" in files_dict 
        # uploaded_file_tuple = files_dict["audio_file"] # (filename, file_obj, content_type)
        # assert Path(mock_audio_file_path).name in uploaded_file_tuple[0]
        assert kwargs.get("timeout") == settings.MODEL_API_TIMEOUT

@pytest.mark.asyncio
async def test_protocol_generator_service_success(): # Renamed for clarity
    """Test protocol generation service success and call arguments."""
    test_transcript = [{"text": "Action item: do this. Decision: go there.", "start": 0, "end": 1}]
    test_summary = "Meeting summary about actions and decisions."
    expected_response_data = {"protocol": "Generated test protocol content."}
    # Assuming the method extracts the protocol string directly
    expected_service_result = "Generated test protocol content."
    
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.return_value = expected_response_data
        
        result = await model_api.generate_protocol(test_transcript, test_summary)
        
        assert result == expected_service_result
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="/generate_protocol", # TODO: Verify model-api endpoint for protocol generation
            json_data={"transcript": test_transcript, "summary": test_summary},
            timeout=settings.MODEL_API_TIMEOUT
        )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_question, mock_api_response, expected_service_result",
    [
        ("What was decision A?", {"answer": "Decision A was made.", "confidence": 0.95}, "Decision A was made."),
        ("Any risks identified?", {"answer": "Risk X and Y.", "source_segments": [1, 2]}, "Risk X and Y."),
        ("Elaborate on topic Z.", {"answer": "Topic Z is complex..."}, "Topic Z is complex..."),
        # Case: API returns a slightly different answer structure but service adapts
        ("Who is responsible for task Q?", {"answer_text": "User B.", "certainty": "high"}, "User B."),
    ]
)
async def test_meeting_chatbot_service_success_parametrized(test_meeting, test_question, mock_api_response, expected_service_result):
    """Test meeting chatbot service with various questions and responses."""
    # TODO: Ensure ModelAPIClient.get_meeting_answer handles varied API response structures (e.g., 'answer' vs 'answer_text')
    # Ensure your model_api.get_meeting_answer is robust enough if mock_api_response structure varies
    # For the last case, it assumes get_meeting_answer tries to find "answer" or "answer_text"
    if "answer_text" in mock_api_response and "answer" not in mock_api_response:
        # This simulates a scenario where your service might need to adapt to different key names
        # For the purpose of this test, we assume the service logic handles this adaptation.
        # If it doesn't, this specific parameterized case might fail or require service modification.
        pass # The service is expected to handle this specific mock_api_response structure

    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.return_value = mock_api_response
        
        result = await model_api.get_meeting_answer(test_meeting.id, test_question)
        
        assert result == expected_service_result
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint=f"/chat/{test_meeting.id}", # TODO: Verify model-api endpoint for chat
            json_data={"question": test_question},
            timeout=settings.MODEL_API_TIMEOUT
        )

@pytest.fixture
def mock_upload_file() -> Mock:
    """Creates a mock UploadFile object."""
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = "test_audio.mp3"
    # Simulate a file-like object for .file attribute
    mock_file.file = BytesIO(b"dummy audio content for save_file test")
    # Make .read() an AsyncMock
    mock_file.read = AsyncMock(return_value=b"dummy audio content for save_file test")
    mock_file.content_type = "audio/mpeg"
    # Reset seek to the beginning of the stream for reading - not strictly needed if .read() is mocked but good practice
    # mock_file.file.seek(0) # Not needed as file.read() is mocked directly
    return mock_file

@pytest.fixture
def mock_db_session() -> Mock:
    """Creates a mock SQLAlchemy Session."""
    session = Mock(spec=Session)
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    return session

@pytest.mark.asyncio
async def test_save_file_success(mocker, mock_upload_file: UploadFile, mock_db_session: Session):
    """Test successful file saving, path generation, content writing, and DB record creation."""
    meeting_id = 123
    # user_id is not a param of the new save_file function provided by user
    file_type_enum_mock = mocker.Mock(spec=FileType) # Assuming FileType is an enum

    mock_storage_dir = "test_storage"
    # This dict structure is assumed based on `save_file`s usage of `ALLOWED_MIME_TYPES.keys()` and `startswith()`
    mock_allowed_mime_types_dict = {"audio/": ".ext", "audio/mpeg": ".mp3"} 
    fixed_uuid_value = "fixed-uuid-123"
    expected_content = b"dummy audio content for save_file test"
    
    mock_upload_file.read = AsyncMock(return_value=expected_content)
    mock_upload_file.content_type = "audio/mpeg" # Ensure it matches a key or prefix
    # Extract extension from original filename for expected unique filename
    original_filename, original_ext = os.path.splitext(mock_upload_file.filename)

    # Mock dependencies in core.storage
    mocker.patch("core.storage.settings.STORAGE_DIR", mock_storage_dir)
    mocker.patch("core.storage.settings.ALLOWED_UPLOAD_PREFIXES", ["audio/"]) # Mock for ALLOWED_UPLOAD_PREFIXES
    # Mock uuid.uuid4() to return an object that can be str() and has .hex if used (save_file uses str() directly)
    mock_uuid_obj = Mock()
    mock_uuid_obj.__str__ = lambda: fixed_uuid_value
    # save_file uses f"{uuid.uuid4()}{ext}", so it calls str() on the uuid object.
    mock_uuid_call = mocker.patch("core.storage.uuid.uuid4", return_value=mock_uuid_obj)
    mock_os_makedirs = mocker.patch("core.storage.os.makedirs")
    
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    
    MockFileModelClass = mocker.patch("core.storage.FileModel")
    mock_file_instance = Mock(spec=File) 
    MockFileModelClass.return_value = mock_file_instance

    saved_file_model = await save_file(
        db=mock_db_session, 
        file=mock_upload_file, 
        meeting_id=meeting_id, 
        file_type=file_type_enum_mock
    )

    mock_uuid_call.assert_called_once()
    expected_unique_filename = f"{fixed_uuid_value}{original_ext}" 
    
    mock_os_makedirs.assert_called_once_with(mock_storage_dir, exist_ok=True)
    
    expected_file_path = os.path.join(mock_storage_dir, expected_unique_filename)
    mock_open.assert_called_once_with(expected_file_path, "wb")
    # Assert that the AsyncMock mock_upload_file.read was awaited
    assert mock_upload_file.read.called 
    mock_open().write.assert_called_once_with(expected_content)

    MockFileModelClass.assert_called_once_with(
        filename=mock_upload_file.filename, 
        file_type=file_type_enum_mock,
        mime_type=mock_upload_file.content_type,
        size=len(expected_content),
        url=f"/files/{expected_unique_filename}",
        storage_path=expected_file_path,
        meeting_id=meeting_id
    )
    
    mock_db_session.add.assert_called_once_with(mock_file_instance)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_file_instance)
    
    assert saved_file_model == mock_file_instance

@pytest.mark.asyncio
async def test_save_file_unsupported_mime_type(mocker, mock_upload_file: UploadFile, mock_db_session: Session):
    """Test save_file raises ValueError for unsupported MIME type."""
    meeting_id = 123
    file_type_enum_mock = mocker.Mock(spec=FileType)
    
    mock_storage_dir = "test_storage"
    mock_allowed_mime_types_dict = {"image/png": ".png"} 
    mock_upload_file.content_type = "application/octet-stream" # This is not in the allowed list

    mocker.patch("core.storage.settings.STORAGE_DIR", mock_storage_dir)
    mocker.patch("core.storage.settings.ALLOWED_UPLOAD_PREFIXES", ["audio/"]) # Correct mock for the test
    mock_os_makedirs = mocker.patch("core.storage.os.makedirs")
    mock_open_func = mocker.patch("builtins.open")

    with pytest.raises(ValueError, match=f"Unsupported file type: {mock_upload_file.content_type}"):
        await save_file(
            db=mock_db_session, 
            file=mock_upload_file, 
            meeting_id=meeting_id, 
            file_type=file_type_enum_mock
        )
    
    mock_os_makedirs.assert_not_called()
    mock_open_func.assert_not_called()
    mock_db_session.add.assert_not_called()

@pytest.mark.asyncio
async def test_save_file_directory_creation_os_error(mocker, mock_upload_file: UploadFile, mock_db_session: Session):
    """Test error handling when os.makedirs fails."""
    meeting_id = 123
    file_type_enum_mock = mocker.Mock(spec=FileType)

    mock_storage_dir = "test_storage_mkdir_fail"
    mock_allowed_mime_types_dict = {"audio/mpeg": ".mp3"} 
    mock_upload_file.content_type = "audio/mpeg"
    original_filename, original_ext = os.path.splitext(mock_upload_file.filename)

    mocker.patch("core.storage.settings.STORAGE_DIR", mock_storage_dir)
    mocker.patch("core.storage.settings.ALLOWED_UPLOAD_PREFIXES", ["audio/"]) # Correct mock for the test
    mock_uuid_obj = Mock()
    mock_uuid_obj.__str__ = lambda: "fixed-uuid"
    mocker.patch("core.storage.uuid.uuid4", return_value=mock_uuid_obj)
    mock_os_makedirs = mocker.patch("core.storage.os.makedirs", side_effect=OSError("Permission denied"))
    mock_open_func = mocker.patch("builtins.open")

    with pytest.raises(OSError, match="Permission denied"):
        await save_file(
            db=mock_db_session, 
            file=mock_upload_file, 
            meeting_id=meeting_id, 
            file_type=file_type_enum_mock
        )

    mock_os_makedirs.assert_called_once_with(mock_storage_dir, exist_ok=True)
    mock_open_func.assert_not_called()
    mock_db_session.add.assert_not_called()

@pytest.mark.asyncio
async def test_save_file_read_error(mocker, mock_upload_file: UploadFile, mock_db_session: Session):
    """Test error handling when file.read() fails."""
    meeting_id = 123
    file_type_enum_mock = mocker.Mock(spec=FileType)

    mock_storage_dir = "test_storage_read_fail"
    mock_allowed_mime_types_dict = {"audio/": ".mp3"}
    mock_upload_file.content_type = "audio/mpeg"
    mock_upload_file.read = AsyncMock(side_effect=IOError("Failed to read from upload stream"))
    original_filename, original_ext = os.path.splitext(mock_upload_file.filename)

    mocker.patch("core.storage.settings.STORAGE_DIR", mock_storage_dir)
    mocker.patch("core.storage.settings.ALLOWED_UPLOAD_PREFIXES", ["audio/"]) # Correct mock for the test
    mock_uuid_obj = Mock()
    mock_uuid_obj.__str__ = lambda: "fixed-uuid"
    mocker.patch("core.storage.uuid.uuid4", return_value=mock_uuid_obj)
    mock_os_makedirs = mocker.patch("core.storage.os.makedirs")
    # Use mocker.mock_open() to allow assertions on the handle if needed
    mock_open_func = mocker.patch("builtins.open", mocker.mock_open()) 
    mock_os_remove = mocker.patch("core.storage.os.remove")

    with pytest.raises(IOError, match="Failed to read from upload stream"):
        await save_file(
            db=mock_db_session, 
            file=mock_upload_file, 
            meeting_id=meeting_id, 
            file_type=file_type_enum_mock
        )
    
    mock_os_makedirs.assert_called_once_with(mock_storage_dir, exist_ok=True)
    expected_filename = f"fixed-uuid{original_ext}" 
    expected_file_path = os.path.join(mock_storage_dir, expected_filename)
    mock_open_func.assert_called_once_with(expected_file_path, "wb")
    assert mock_upload_file.read.called
    
    mock_open_func().write.assert_not_called()
    mock_db_session.add.assert_not_called()
    mock_os_remove.assert_not_called()


@pytest.mark.asyncio
async def test_save_file_write_error(mocker, mock_upload_file: UploadFile, mock_db_session: Session):
    """Test error handling when writing file content (f.write) fails."""
    meeting_id = 123
    file_type_enum_mock = mocker.Mock(spec=FileType)
    expected_content = b"dummy content"

    mock_storage_dir = "test_storage_write_fail"
    mock_allowed_mime_types_dict = {"audio/mpeg": ".mp3"}
    mock_upload_file.content_type = "audio/mpeg"
    mock_upload_file.read = AsyncMock(return_value=expected_content)
    original_filename, original_ext = os.path.splitext(mock_upload_file.filename)

    mocker.patch("core.storage.settings.STORAGE_DIR", mock_storage_dir)
    mocker.patch("core.storage.settings.ALLOWED_UPLOAD_PREFIXES", ["audio/"]) # Correct mock for the test
    mock_uuid_obj = Mock()
    mock_uuid_obj.__str__ = lambda: "fixed-uuid"
    mocker.patch("core.storage.uuid.uuid4", return_value=mock_uuid_obj)
    mock_os_makedirs = mocker.patch("core.storage.os.makedirs")
    
    mock_file_handle = mocker.MagicMock()
    mock_file_handle.write.side_effect = IOError("Disk full")
    # Ensure the context manager __enter__ returns the mock_file_handle
    mock_open_cm = mocker.patch("builtins.open", mocker.mock_open())
    mock_open_cm.return_value.__enter__.return_value = mock_file_handle
    
    mock_os_remove = mocker.patch("core.storage.os.remove")

    with pytest.raises(IOError, match="Disk full"):
        await save_file(
            db=mock_db_session, 
            file=mock_upload_file, 
            meeting_id=meeting_id, 
            file_type=file_type_enum_mock
        )

    mock_os_makedirs.assert_called_once_with(mock_storage_dir, exist_ok=True)
    expected_filename = f"fixed-uuid{original_ext}" 
    expected_file_path = os.path.join(mock_storage_dir, expected_filename)
    mock_open_cm.assert_called_once_with(expected_file_path, "wb")
    assert mock_upload_file.read.called
    mock_file_handle.write.assert_called_once_with(expected_content)
    
    mock_db_session.add.assert_not_called()
    mock_os_remove.assert_not_called()

@pytest.mark.asyncio
async def test_save_file_db_commit_error_no_cleanup(mocker, mock_upload_file: UploadFile, mock_db_session: Session):
    """Test error handling when db.commit fails, ensuring file is NOT cleaned up (current behavior)."""
    meeting_id = 123
    file_type_enum_mock = mocker.Mock(spec=FileType)
    expected_content = b"db commit fail content"

    mock_storage_dir = "test_storage_db_fail"
    mock_allowed_mime_types_dict = {"audio/mpeg": ".mp3"}
    fixed_uuid_value = "db-fail-uuid"

    mock_upload_file.content_type = "audio/mpeg"
    mock_upload_file.read = AsyncMock(return_value=expected_content)
    original_filename, original_ext = os.path.splitext(mock_upload_file.filename)

    mocker.patch("core.storage.settings.STORAGE_DIR", mock_storage_dir)
    mocker.patch("core.storage.settings.ALLOWED_UPLOAD_PREFIXES", ["audio/"]) # Correct mock for the test
    mock_uuid_obj = Mock()
    mock_uuid_obj.__str__ = lambda: fixed_uuid_value
    mocker.patch("core.storage.uuid.uuid4", return_value=mock_uuid_obj)
    mocker.patch("core.storage.os.makedirs")
    mock_open_func = mocker.patch("builtins.open", mocker.mock_open())
    
    MockFileModelClass = mocker.patch("core.storage.FileModel")
    mock_file_instance = Mock(spec=File)
    MockFileModelClass.return_value = mock_file_instance

    mock_db_session.commit.side_effect = Exception("Simulated DB commit error")
    mock_os_remove = mocker.patch("core.storage.os.remove")

    with pytest.raises(Exception, match="Simulated DB commit error"):
        await save_file(
            db=mock_db_session, 
            file=mock_upload_file, 
            meeting_id=meeting_id, 
            file_type=file_type_enum_mock
        )

    expected_filename = f"{fixed_uuid_value}{original_ext}"
    expected_file_path = os.path.join(mock_storage_dir, expected_filename)
    mock_open_func.assert_called_once_with(expected_file_path, "wb")
    mock_open_func().write.assert_called_once_with(expected_content)

    MockFileModelClass.assert_called_once() 
    mock_db_session.add.assert_called_once_with(mock_file_instance)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_not_called()

    mock_os_remove.assert_not_called()

@pytest.mark.asyncio
async def test_invalid_audio_file_path_transcribe():
    """Test transcribe_audio handling of invalid audio file path.
    This tests logic *before* _make_request is called if model_api.transcribe_audio does path validation.
    Based on current model_api.py, transcribe_audio doesn't do local file checks, it expects a URL.
    So, this test might need to be re-evaluated or its purpose clarified.
    If it's about the external API call failing due to a bad URL that results in a specific error,
    then the new _make_request error tests cover the error wrapping.
    If model_api.transcribe_audio itself is supposed to raise FileNotFoundError for local paths,
    it needs to be implemented in ModelAPIClient.
    For now, assuming this test expects some form of error if path is invalid.
    Given `transcribe_audio` takes `audio_url`, a `FileNotFoundError` locally is unlikely.
    Perhaps it should test for `ValueError` if `audio_url` is malformed, or `ModelAPIError` if the API call fails.
    Let's assume `ModelAPIError` due to API call failure for a bad URL.
    """
    client_instance = ModelAPIClient()
    mock_async_client = AsyncMock(spec=httpx.AsyncClient)
    # Simulate API rejecting a bad URL format or non-existent resource
    error_response = mock_httpx_response_factory()(400, text_data="Invalid audio_url")
    mock_async_client.post.return_value = error_response
    error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=Mock(spec=httpx.Request), response=error_response
    )

    with patch('httpx.AsyncClient', return_value=mock_async_client):
        with pytest.raises(ModelAPIError) as exc_info:
            await client_instance.transcribe_audio(audio_url="nonexistent_or_bad_url", language="ru")
        assert exc_info.value.status_code == 400
        assert "Invalid audio_url" in exc_info.value.detail


@pytest.mark.asyncio
async def test_invalid_transcript_format_for_protocol(): # This should test client-side validation if any
    """Test generate_protocol handling of invalid transcript format (e.g. empty list).
    If this validation is done *before* calling _make_request.
    Looking at `generate_protocol`, it doesn't seem to have specific validation for empty transcript list.
    The API might reject it. Let's assume it's an API validation for now.
    If the API returns a 400 for this, ModelAPIError will be raised.
    """
    client_instance = ModelAPIClient()
    mock_async_client = AsyncMock(spec=httpx.AsyncClient)
    error_response = mock_httpx_response_factory()(422, json_data={"detail": "Transcript cannot be empty"})
    mock_async_client.post.return_value = error_response
    error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unprocessable Entity", request=Mock(spec=httpx.Request), response=error_response
    )
    with patch('httpx.AsyncClient', return_value=mock_async_client):
        with pytest.raises(ModelAPIError) as exc_info:
            await client_instance.generate_protocol(transcript=[], summary="Valid Summary")
        assert exc_info.value.status_code == 422
        assert "Transcript cannot be empty" in exc_info.value.detail


@pytest.mark.asyncio
async def test_invalid_question_format_for_chatbot(): # This should test client-side validation
    """Test get_meeting_answer handling of invalid question format (e.g. empty string).
    `get_meeting_answer` in `model_api.py` has a `ValueError` for empty question. This test is correct.
    """
    client_instance = ModelAPIClient() # Use a fresh instance
    with pytest.raises(ValueError, match="Question cannot be empty"):
        await client_instance.get_meeting_answer(meeting_id=1, question="   ") # Test with whitespace only
    with pytest.raises(ValueError, match="Question cannot be empty"):
        await client_instance.get_meeting_answer(meeting_id=1, question="")


# New fixture for creating mock httpx.Response objects
@pytest.fixture
def mock_httpx_response_factory():
    def _factory(status_code: int, json_data: Optional[dict] = None, text_data: Optional[str] = None):
        response = Mock(spec=httpx.Response)
        response.status_code = status_code
        if json_data is not None:
            response.json = Mock(return_value=json_data)
            # httpx.HTTPStatusError uses response.text in its default message formatting
            response.text = str(json_data) if text_data is None else text_data
        else:
            response.json = Mock(side_effect=ValueError("No JSON")) # Simulate no JSON body
            response.text = text_data if text_data is not None else "Error Text"
        
        # Mock request attribute for HTTPStatusError
        request = Mock(spec=httpx.Request)
        request.method = "POST"
        request.url = "http://fakeapi/test"
        response.request = request
        return response
    return _factory

# New comprehensive error handling test for _make_request
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception_to_raise, expected_status_code, expected_detail_contains, is_request_error, is_json_decode_error",
    [
        (httpx.HTTPStatusError("Client Error", request=Mock(spec=httpx.Request), response=lambda: mock_httpx_response_factory()(400, json_data={"error": "Bad Request"}, text_data='{"error": "Bad Request"}')), 
         400, {"error": "Bad Request"}, False, False),
        (httpx.HTTPStatusError("Unauthorized", request=Mock(spec=httpx.Request), response=lambda: mock_httpx_response_factory()(401, text_data="Auth failed")),
         401, "Auth failed", False, False),
        (httpx.HTTPStatusError("Forbidden", request=Mock(spec=httpx.Request), response=lambda: mock_httpx_response_factory()(403, json_data={"message": "Permission Denied"})),
         403, {"message": "Permission Denied"}, False, False),
        (httpx.HTTPStatusError("Not Found", request=Mock(spec=httpx.Request), response=lambda: mock_httpx_response_factory()(404, json_data={"detail": "Resource not found"})),
         404, {"detail": "Resource not found"}, False, False),
        (httpx.HTTPStatusError("Server Error", request=Mock(spec=httpx.Request), response=lambda: mock_httpx_response_factory()(500, text_data="Internal Server Error")),
         500, "Internal Server Error", False, False),
        (httpx.HTTPStatusError("Service Unavailable", request=Mock(spec=httpx.Request), response=lambda: mock_httpx_response_factory()(503, text_data="Service Temporarily Unavailable")),
         503, "Service Temporarily Unavailable", False, False),
        (httpx.TimeoutException("Request timed out", request=Mock(spec=httpx.Request)), 
         None, "Request timed out", True, False),
        (httpx.ConnectError("Connection failed", request=Mock(spec=httpx.Request)),
         None, "Connection failed", True, False),
        (json.JSONDecodeError("Expecting value", "{\"bad_json\": \"test\",", 0),
         None, "Expecting value", False, True),
        (TimeoutError("Specific Timeout Error"),
         None, "Specific Timeout Error", False, False),
        (ValueError("Some other value error"),
         None, "Some other value error", False, False),
    ]
)
async def test_model_api_client_make_request_error_handling(
    exception_to_raise, 
    expected_status_code, 
    expected_detail_contains,
    is_request_error,
    is_json_decode_error,
    mock_httpx_response_factory
):
    """Test ModelAPIClient._make_request error handling and ModelAPIError population."""
    client_instance = ModelAPIClient() # Test with a fresh instance

    if isinstance(exception_to_raise, httpx.HTTPStatusError):
        status_code = exception_to_raise.response().status_code
        json_payload = None
        text_payload = None
        try:
            json_payload = exception_to_raise.response().json()
        except ValueError:
            pass 
        if not json_payload:
             text_payload = exception_to_raise.response().text
        actual_response_mock = mock_httpx_response_factory(status_code, json_data=json_payload, text_data=text_payload)
        exception_to_raise.response = actual_response_mock

    mock_async_client = AsyncMock(spec=httpx.AsyncClient)
    
    if is_json_decode_error:
        mock_successful_response = mock_httpx_response_factory(200, text_data="not valid json")
        mock_successful_response.raise_for_status = Mock()
        mock_successful_response.json = Mock(side_effect=exception_to_raise)
        mock_async_client.post.return_value = mock_successful_response
    elif isinstance(exception_to_raise, httpx.HTTPStatusError):
        mock_response = exception_to_raise.response
        mock_async_client.post.return_value = mock_response
        mock_response.raise_for_status.side_effect = exception_to_raise
    else:
        mock_async_client.post.side_effect = exception_to_raise

    with patch('httpx.AsyncClient', return_value=mock_async_client):
        with pytest.raises(ModelAPIError) as exc_info:
            await client_instance._make_request(method="POST", endpoint="test/endpoint", data={"key": "value"})

    assert exc_info.value.status_code == expected_status_code
    
    # Check that the .detail attribute is correctly populated.
    # For HTTPStatusError, expected_detail_contains is the JSON dict or error text.
    # For other exceptions (like httpx.RequestError, json.JSONDecodeError, etc.), 
    # expected_detail_contains is str(original_exception).
    # This aligns with how ModelAPIError sets its .detail attribute in _make_request.
    assert exc_info.value.detail == expected_detail_contains
    
    if expected_status_code is not None:
        # This part of the message is specific to HTTPStatusError instances
        assert f"Model API request failed for test/endpoint" in str(exc_info.value)
    elif is_request_error:
        # This part of the message is specific to httpx.RequestError instances
        assert f"Model API request error for test/endpoint: {expected_detail_contains}" in str(exc_info.value)
    else: # Covers JSONDecodeError, general TimeoutError, ValueError, etc.
        # This part of the message is for other unexpected errors
        assert f"An unexpected error occurred in ModelAPIClient for test/endpoint: {expected_detail_contains}" in str(exc_info.value)