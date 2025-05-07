import pytest
from fastapi.testclient import TestClient
import os
from datetime import datetime
import json
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)
test_file_path = "test.mp3"
# Test data
TEST_MEETING_ID = "1"
TEST_QUESTION = "When was the meeting held?"

@pytest.fixture
def mock_meeting_data():
    return {
        "id": 1,
        "title": "Test Meeting",
        "date": "2024-03-15",
        "start_time": "14:00:00",
        "end_time": "15:00:00",
        "duration": 3600,
        "location": "Conference Room A",
        "is_online": False,
        "is_published": True,
        "access_level": "public",
        "created_by_id": 1,
        "created_at": "2024-03-14T10:00:00",
        "updated_at": "2024-03-14T10:00:00",
        "status": "done",
        "processing_progress": 100,
        "error_message": None,
        "audio_file_id": 1,
        "transcript_file_id": 2,
        "summary_file_id": 3,
        "protocol_file_id": 4,
        "participants": [
            {"id": 1, "name": "John Doe"},
            {"id": 2, "name": "Jane Smith"}
        ],
        "tags": [
            {"id": 1, "label": "important"},
            {"id": 2, "label": "planning"}
        ],
        "transcript": "This is a test transcript",
        "summary": "This is a test summary",
        "decisions": ["Decision 1", "Decision 2"]
    }

def test_transcribe_endpoint():
    """Test the transcribe endpoint"""
    # Create a test audio file
    test_file_path = "test_audio.wav"
    with open(test_file_path, "wb") as f:
        f.write(b"dummy audio content")
    
    with open(test_file_path, "rb") as f:
        response = client.post("/transcribe", files={"file": ("test_audio.wav", f, "audio/wav")})
        print("RESPONSE /transcribe:", response.status_code, response.json())
    
    assert response.status_code == 200
    assert "transcription" in response.json()
    
    # Cleanup
    os.remove(test_file_path)

def test_summary_endpoint():
    """Test the summary endpoint"""
    # Create a test file
    test_file_path = "test_summary.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test transcript for summarization")
    
    with open(test_file_path, "rb") as f:
        response = client.post("/summary", files={"file": ("test_summary.txt", f, "text/plain")})
        print("RESPONSE /summary:", response.status_code, response.json())
    
    assert response.status_code == 200
    assert "summary" in response.json()
    
    # Cleanup
    os.remove(test_file_path)

def test_speakers_endpoint():
    """Test the speakers endpoint"""
    # Create a test audio file
    with open(test_file_path, "wb") as f:
        f.write(b"dummy audio content")
    
    with open(test_file_path, "rb") as f:
        response = client.post("/speakers", files={"file": ("test_speakers.wav", f, "audio/wav")})
        print("RESPONSE /speakers:", response.status_code, response.json())
    
    assert response.status_code == 200
    assert "segments" in response.json()
    
    # Cleanup
    os.remove(test_file_path)

def test_speaker_transcript_endpoint():
    """Test the speaker transcript endpoint"""
    # Create a test audio file
    with open(test_file_path, "wb") as f:
        f.write(b"dummy audio content")
    
    with open(test_file_path, "rb") as f:
        response = client.post("/speaker-transcript", files={"file": ("test_speaker_transcript.wav", f, "audio/wav")})
        print("RESPONSE /speaker-transcript:", response.status_code, response.json())
    
    assert response.status_code == 200
    assert "segments" in response.json()
    
    # Cleanup
    os.remove(test_file_path)

def test_protocol_endpoint():
    """Test the protocol generation endpoint"""
    test_data = {
        "transcript": "Speaker 1: Hello\nSpeaker 2: Hi there\nSpeaker 1: How are you?"
    }
    
    response = client.post("/protocol", json=test_data)
    print("RESPONSE /protocol:", response.status_code, response.json())
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_chat_answer_endpoint(mock_meeting_data, monkeypatch):
    """Test the chat answer endpoint"""
    # Mock the get_meeting_info function
    def mock_get_meeting_info(meeting_id):
        return mock_meeting_data
    
    from services import meeting_chatbot
    monkeypatch.setattr(meeting_chatbot, "get_meeting_info", mock_get_meeting_info)
    
    test_data = {
        "meeting_id": TEST_MEETING_ID,
        "question": TEST_QUESTION
    }
    
    response = client.post("/chat/answer", json=test_data)
    print("RESPONSE /chat/answer:", response.status_code, response.json())
    assert response.status_code == 200
    assert "answer" in response.json()

def test_get_meeting_info_endpoint(mock_meeting_data, monkeypatch):
    """Test the get meeting info endpoint"""
    # Mock the get_meeting_info function
    def mock_get_meeting_info(meeting_id):
        return mock_meeting_data
    
    from services import meeting_chatbot
    monkeypatch.setattr(meeting_chatbot, "get_meeting_info", mock_get_meeting_info)
    
    response = client.get(f"/chat/meeting/{TEST_MEETING_ID}")
    print(f"RESPONSE /chat/meeting/{{id}}:", response.status_code, response.json())
    assert response.status_code == 200
    assert response.json()["id"] == mock_meeting_data["id"]
    assert response.json()["title"] == mock_meeting_data["title"]

def test_error_handling():
    """Test error handling for invalid requests"""
    # Test invalid file upload
    response = client.post("/transcribe", files={"file": ("test.txt", b"invalid content", "text/plain")})
    print("RESPONSE /transcribe (invalid):", response.status_code, response.json())
    assert response.status_code in [400, 422]
    
    # Test invalid meeting ID
    response = client.get("/chat/meeting/invalid_id")
    print("RESPONSE /chat/meeting/invalid_id:", response.status_code, response.json())
    assert response.status_code in [400, 404]
    
    # Test invalid chat question format
    response = client.post("/chat/answer", json={"invalid": "data"})
    print("RESPONSE /chat/answer (invalid):", response.status_code, response.json())
    assert response.status_code == 422

class TestErrorHandling:
    """Тесты обработки ошибок для всех эндпоинтов"""

    def test_transcribe_invalid_file(self):
        """Тест обработки ошибок при загрузке неверного файла"""
        # Тест с пустым файлом
        response = client.post("/transcribe", files={"file": ("empty.wav", b"", "audio/wav")})
        print("RESPONSE /transcribe (empty):", response.status_code, response.json())
        assert response.status_code in [400, 422]
        
        # Тест с неверным форматом
        response = client.post("/transcribe", files={"file": ("test.txt", b"invalid content", "text/plain")})
        print("RESPONSE /transcribe (wrong format):", response.status_code, response.json())
        assert response.status_code in [400, 422]
        
        # Тест без файла
        response = client.post("/transcribe")
        print("RESPONSE /transcribe (no file):", response.status_code, response.json())
        assert response.status_code == 422

    def test_summary_invalid_file(self):
        """Тест обработки ошибок при генерации сводки"""
        # Тест с пустым файлом
        response = client.post("/summary", files={"file": ("empty.txt", b"", "text/plain")})
        print("RESPONSE /summary (empty):", response.status_code, response.json())
        assert response.status_code in [400, 422]
        
        # Тест с неверным форматом
        response = client.post("/summary", files={"file": ("test.wav", b"invalid content", "audio/wav")})
        print("RESPONSE /summary (wrong format):", response.status_code, response.json())
        assert response.status_code in [400, 422]

    def test_speakers_invalid_file(self):
        """Тест обработки ошибок при определении спикеров"""
        # Тест с пустым файлом
        response = client.post("/speakers", files={"file": ("empty.wav", b"", "audio/wav")})
        print("RESPONSE /speakers (empty):", response.status_code, response.json())
        assert response.status_code in [400, 422]
        
        # Тест с неверным форматом
        response = client.post("/speakers", files={"file": ("test.txt", b"invalid content", "text/plain")})
        print("RESPONSE /speakers (wrong format):", response.status_code, response.json())
        assert response.status_code in [400, 422]

    def test_protocol_invalid_data(self):
        """Тест обработки ошибок при генерации протокола"""
        # Тест с пустыми данными
        response = client.post("/protocol", json={"transcript": ""})
        print("RESPONSE /protocol (empty):", response.status_code, response.json())
        assert response.status_code in [400, 422]
        
        # Тест с неверным форматом данных
        response = client.post("/protocol", json={"invalid": "data"})
        print("RESPONSE /protocol (wrong format):", response.status_code, response.json())
        assert response.status_code == 422
        
        # Тест без данных
        response = client.post("/protocol", json={})
        print("RESPONSE /protocol (no data):", response.status_code, response.json())
        assert response.status_code == 422

    def test_chat_answer_invalid_data(self):
        """Тест обработки ошибок при ответах чат-бота"""
        # Тест с неверным ID встречи
        response = client.post("/chat/answer", json={
            "meeting_id": "invalid_id",
            "question": TEST_QUESTION
        })
        print("RESPONSE /chat/answer (invalid id):", response.status_code, response.json())
        assert response.status_code in [400, 404]
        
        # Тест с пустым вопросом
        response = client.post("/chat/answer", json={
            "meeting_id": TEST_MEETING_ID,
            "question": ""
        })
        print("RESPONSE /chat/answer (empty question):", response.status_code, response.json())
        assert response.status_code in [400, 422]
        
        # Тест с неверным форматом данных
        response = client.post("/chat/answer", json={"invalid": "data"})
        print("RESPONSE /chat/answer (wrong format):", response.status_code, response.json())
        assert response.status_code == 422

    def test_get_meeting_info_invalid_id(self):
        """Тест обработки ошибок при получении информации о встрече"""
        # Тест с несуществующим ID
        response = client.get("/chat/meeting/nonexistent_id")
        print("RESPONSE /chat/meeting/nonexistent_id:", response.status_code, response.json())
        assert response.status_code in [400, 404]
        
        # Тест с неверным форматом ID
        response = client.get("/chat/meeting/invalid_id")
        print("RESPONSE /chat/meeting/invalid_id:", response.status_code, response.json())
        assert response.status_code in [400, 404]

    def test_backend_connection_error(self, monkeypatch):
        """Тест обработки ошибок соединения с бэкендом"""
        def mock_get_meeting_info(meeting_id):
            raise Exception("Connection error")
        
        from services import meeting_chatbot
        monkeypatch.setattr(meeting_chatbot, "get_meeting_info", mock_get_meeting_info)
        
        response = client.get(f"/chat/meeting/{TEST_MEETING_ID}")
        print("RESPONSE /chat/meeting (backend error):", response.status_code, response.json())
        assert response.status_code == 500
        assert "error" in response.json()

    def test_invalid_file_size(self):
        """Тест обработки ошибок при загрузке слишком большого файла"""
        # Создаем файл размером больше допустимого (например, 100MB)
        large_file = b"0" * (100 * 1024 * 1024)  # 100MB
        
        response = client.post("/transcribe", files={"file": ("large.wav", large_file, "audio/wav")})
        print("RESPONSE /transcribe (large file):", response.status_code, response.json())
        assert response.status_code in [400, 413]  # 413 Payload Too Large

    def test_concurrent_requests(self):
        """Тест обработки одновременных запросов"""
        import threading
        import time
        
        def make_request():
            response = client.get(f"/chat/meeting/{TEST_MEETING_ID}")
            print("RESPONSE /chat/meeting (concurrent):", response.status_code, response.json())
            return response.status_code
        
        # Создаем несколько потоков для одновременных запросов
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()
        
        # Проверяем, что все запросы были обработаны
        assert all(make_request() in [200, 429] for _ in range(5))

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 