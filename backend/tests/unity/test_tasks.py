import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session

from core.tasks import process_meeting
from core.model_api import ModelAPIError
from models.meeting import Meeting, MeetingStatus
from models.file import File as FileModel, FileType


@pytest.fixture
def mock_db_session_for_tasks():
    db_session = MagicMock(spec=Session)
    mock_meeting = MagicMock(spec=Meeting)
    mock_meeting.id = 1
    mock_meeting.audio_file = MagicMock(spec=FileModel)
    mock_meeting.audio_file.url = "/files/test_audio.wav"
    mock_meeting.status = MeetingStatus.pending
    mock_meeting.processing_progress = 0
    mock_meeting.summary_file_id = None
    mock_meeting.protocol_file_id = None
    mock_meeting.error_message = None

    # Configure query to return the mock_meeting
    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = mock_meeting
    db_session.query.return_value = query_mock
    
    return db_session, mock_meeting

@pytest.mark.asyncio
async def test_process_meeting_success(mock_db_session_for_tasks):
    db_session, mock_meeting = mock_db_session_for_tasks

    transcript_data = [{
        "start_time": 0.0, "end_time": 1.0, "text": "Hello world",
        "confidence": 0.9, "language": "ru", "metadata": {}
    }]
    speaker_data = [{"speaker_id": "speaker_1"}]
    summary_text = "This is a summary."
    protocol_text = "This is a protocol."
    
    mock_summary_file = MagicMock(spec=FileModel)
    mock_summary_file.id = 101
    mock_protocol_file = MagicMock(spec=FileModel)
    mock_protocol_file.id = 102

    with patch("core.tasks.SessionLocal", return_value=db_session) as mock_session_local, \
         patch("core.tasks.model_api.transcribe_audio", AsyncMock(return_value=transcript_data)) as mock_transcribe, \
         patch("core.tasks.model_api.detect_speakers", AsyncMock(return_value=speaker_data)) as mock_detect_speakers, \
         patch("core.tasks.model_api.generate_summary", AsyncMock(return_value=summary_text)) as mock_summarize, \
         patch("core.tasks.model_api.generate_protocol", AsyncMock(return_value=protocol_text)) as mock_protocol, \
         patch("core.tasks.save_text_content_as_file", AsyncMock()) as mock_save_text:
        
        mock_save_text.side_effect = [mock_summary_file, mock_protocol_file]

        await process_meeting(meeting_id=mock_meeting.id)

        mock_session_local.assert_called_once()
        
        # Check model_api calls
        mock_transcribe.assert_called_once_with(audio_url=mock_meeting.audio_file.url, language="ru")
        mock_detect_speakers.assert_called_once_with(transcript=transcript_data, audio_url=mock_meeting.audio_file.url)
        mock_summarize.assert_called_once_with(transcript=transcript_data, language="ru")
        mock_protocol.assert_called_once_with(transcript=transcript_data, summary=summary_text, language="ru")

        # Check save_text_content_as_file calls
        assert mock_save_text.call_count == 2
        mock_save_text.assert_any_call(
            db=db_session, content=summary_text, 
            original_filename_base=f"meeting_{mock_meeting.id}_summary",
            meeting_id=mock_meeting.id, file_type=FileType.summary
        )
        mock_save_text.assert_any_call(
            db=db_session, content=protocol_text, 
            original_filename_base=f"meeting_{mock_meeting.id}_protocol",
            meeting_id=mock_meeting.id, file_type=FileType.protocol
        )

        # Check meeting object updates
        assert mock_meeting.processing_progress == 100
        assert mock_meeting.status == MeetingStatus.done
        assert mock_meeting.summary_file_id == mock_summary_file.id
        assert mock_meeting.protocol_file_id == mock_protocol_file.id
        
        # Check db session commits (approximated by number of progress updates + final commit)
        # Each step: transcribe (10%), add_all blocks (40%), detect_speakers (60%), summary (80%), protocol + final (100%)
        # Commits after each of these stages.
        assert db_session.commit.call_count == 5 
        db_session.close.assert_called_once()

@pytest.mark.asyncio
async def test_process_meeting_model_api_error(mock_db_session_for_tasks):
    db_session, mock_meeting = mock_db_session_for_tasks
    
    error_message = "Test Model API Error"

    with patch("core.tasks.SessionLocal", return_value=db_session) as mock_session_local, \
         patch("core.tasks.model_api.transcribe_audio", AsyncMock(side_effect=ModelAPIError(error_message))) as mock_transcribe:

        await process_meeting(meeting_id=mock_meeting.id)

        mock_session_local.assert_called_once()
        mock_transcribe.assert_called_once()
        
        assert mock_meeting.status == MeetingStatus.failed
        assert error_message in mock_meeting.error_message
        # One commit for initial progress, one for failure status
        assert db_session.commit.call_count == 2 
        db_session.close.assert_called_once()

@pytest.mark.asyncio
async def test_process_meeting_no_meeting_found(mock_db_session_for_tasks):
    db_session, _ = mock_db_session_for_tasks
    db_session.query.return_value.filter.return_value.first.return_value = None # Simulate no meeting found

    with patch("core.tasks.SessionLocal", return_value=db_session) as mock_session_local, \
         patch("core.tasks.model_api.transcribe_audio") as mock_transcribe: # No need for AsyncMock if not called

        await process_meeting(meeting_id=999) # Non-existent ID

        mock_session_local.assert_called_once()
        mock_transcribe.assert_not_called()
        db_session.close.assert_called_once() # Ensure session is closed even if meeting not found after opening

@pytest.mark.asyncio
async def test_process_meeting_no_audio_file(mock_db_session_for_tasks):
    db_session, mock_meeting = mock_db_session_for_tasks
    mock_meeting.audio_file = None # Simulate no audio file

    with patch("core.tasks.SessionLocal", return_value=db_session) as mock_session_local, \
         patch("core.tasks.model_api.transcribe_audio") as mock_transcribe:

        await process_meeting(meeting_id=mock_meeting.id)

        mock_session_local.assert_called_once()
        mock_transcribe.assert_not_called()
        # The session is closed inside process_meeting if no audio_file after getting meeting
        db_session.close.assert_called_once() 