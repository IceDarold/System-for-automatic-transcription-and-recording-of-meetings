import httpx
from typing import List, Dict, Any, Optional
from core.config import settings
from models.transcript import TranscriptBlock

class ModelAPIError(Exception):
    """Base exception for model-api errors"""
    pass

class ModelAPIClient:
    def __init__(self):
        self.base_url = settings.MODEL_API_URL
        self.timeout = settings.MODEL_API_TIMEOUT
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a request to model-api"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise ModelAPIError(f"Model API request failed: {str(e)}")
    
    async def transcribe_audio(
        self,
        audio_url: str,
        language: str = "ru"
    ) -> List[Dict[str, Any]]:
        """Transcribe audio file"""
        data = {
            "audio_url": audio_url,
            "language": language
        }
        return await self._make_request("POST", "/transcribe", json=data)
    
    async def generate_summary(
        self,
        transcript: List[Dict[str, Any]],
        language: str = "ru"
    ) -> str:
        """Generate meeting summary"""
        data = {
            "transcript": transcript,
            "language": language
        }
        result = await self._make_request("POST", "/summarize", json=data)
        return result["summary"]
    
    async def generate_protocol(
        self,
        transcript: List[Dict[str, Any]],
        summary: str,
        language: str = "ru"
    ) -> str:
        """Generate meeting protocol"""
        data = {
            "transcript": transcript,
            "summary": summary,
            "language": language
        }
        result = await self._make_request("POST", "/protocol", json=data)
        return result["protocol"]
    
    async def detect_speakers(
        self,
        transcript: List[Dict[str, Any]],
        audio_url: str
    ) -> List[Dict[str, Any]]:
        """Detect and identify speakers in the audio"""
        data = {
            "transcript": transcript,
            "audio_url": audio_url
        }
        return await self._make_request("POST", "/detect-speakers", json=data)

    async def get_meeting_answer(
        self,
        meeting_id: int,
        question: str
    ) -> str:
        """Get answer to a question about the meeting using local model API"""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        data = {
            "meeting_id": str(meeting_id),
            "question": question
        }
        result = await self._make_request("POST", "/chat/answer", json=data)
        return result["answer"]

# Create global client instance
model_api = ModelAPIClient() 