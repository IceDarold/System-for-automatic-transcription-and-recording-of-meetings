import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import os
import tempfile

from models import User, Meeting, File
from models.user import UserRole
from models.meeting import AccessLevel, MeetingStatus
from models.file import FileType
from core.storage import save_file
from core.model_api import ModelAPIClient, model_api, ModelAPIError

@pytest.fixture
def test_audio_file():
    """Create a temporary test audio file"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(b"dummy audio content")
        return f.name

@pytest.mark.asyncio
async def test_transcriber_service(test_audio_file):
    """Test transcription service"""
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = [{"text": "Test transcript", "start": 0, "end": 1}]
        result = await model_api.transcribe_audio(test_audio_file)
        assert result == [{"text": "Test transcript", "start": 0, "end": 1}]

@pytest.mark.asyncio
async def test_summarizer_service():
    """Test summarization service"""
    test_transcript = [{"text": "Test transcript", "start": 0, "end": 1}]
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"summary": "Test summary"}
        result = await model_api.generate_summary(test_transcript)
        assert result == "Test summary"

@pytest.mark.asyncio
async def test_diarizer_service(test_audio_file):
    """Test speaker diarization service"""
    test_transcript = [{"text": "Test transcript", "start": 0, "end": 1}]
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = [{"speaker": "Speaker 1", "text": "Test transcript"}]
        result = await model_api.detect_speakers(test_transcript, test_audio_file)
        assert result == [{"speaker": "Speaker 1", "text": "Test transcript"}]

@pytest.mark.asyncio
async def test_protocol_generator_service():
    """Test protocol generation service"""
    test_transcript = [{"text": "Test transcript", "start": 0, "end": 1}]
    test_summary = "Test summary"
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"protocol": "Test protocol"}
        result = await model_api.generate_protocol(test_transcript, test_summary)
        assert result == "Test protocol"

@pytest.mark.asyncio
async def test_meeting_chatbot_service(test_meeting):
    """Test meeting chatbot service"""
    test_question = "What was discussed in the meeting?"
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"answer": "Test answer"}
        result = await model_api.get_meeting_answer(test_meeting.id, test_question)
        assert result == "Test answer"

@pytest.mark.asyncio
async def test_transcriber_error_handling(test_audio_file):
    """Test transcription service error handling"""
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = ModelAPIError("API Error")
        with pytest.raises(ModelAPIError):
            await model_api.transcribe_audio(test_audio_file)

@pytest.mark.asyncio
async def test_summarizer_error_handling():
    """Test summarization service error handling"""
    test_transcript = [{"text": "Test transcript", "start": 0, "end": 1}]
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = ModelAPIError("API Error")
        with pytest.raises(ModelAPIError):
            await model_api.generate_summary(test_transcript)

@pytest.mark.asyncio
async def test_diarizer_error_handling(test_audio_file):
    """Test diarization service error handling"""
    test_transcript = [{"text": "Test transcript", "start": 0, "end": 1}]
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = ModelAPIError("API Error")
        with pytest.raises(ModelAPIError):
            await model_api.detect_speakers(test_transcript, test_audio_file)

@pytest.mark.asyncio
async def test_protocol_generator_error_handling():
    """Test protocol generation service error handling"""
    test_transcript = [{"text": "Test transcript", "start": 0, "end": 1}]
    test_summary = "Test summary"
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = ModelAPIError("API Error")
        with pytest.raises(ModelAPIError):
            await model_api.generate_protocol(test_transcript, test_summary)

@pytest.mark.asyncio
async def test_meeting_chatbot_error_handling(test_meeting):
    """Test meeting chatbot service error handling"""
    test_question = "What was discussed in the meeting?"
    with patch.object(model_api, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("API Error")
        with pytest.raises(Exception):
            await model_api.get_meeting_answer(test_meeting.id, test_question)

@pytest.mark.asyncio
async def test_invalid_audio_file():
    """Test handling of invalid audio file"""
    with pytest.raises(FileNotFoundError):
        await model_api.transcribe_audio("nonexistent.wav")

@pytest.mark.asyncio
async def test_invalid_transcript_format():
    """Test handling of invalid transcript format"""
    with pytest.raises(ValueError):
        await model_api.generate_protocol([], "Test summary")

@pytest.mark.asyncio
async def test_invalid_question_format():
    """Test handling of invalid question format"""
    with pytest.raises(ValueError):
        await model_api.get_meeting_answer(1, "") 