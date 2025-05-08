import httpx
import logging
from typing import List, Dict, Any, Optional
from core.config import settings
from models.transcript import TranscriptBlock

logger = logging.getLogger(__name__)

class ModelAPIError(Exception):
    """Custom exception for Model API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, detail: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail

    def __str__(self):
        if self.status_code is not None:
            return f"{self.status_code} {super().__str__()} Detail: {self.detail}"
        return super().__str__()

class ModelAPIClient:
    def __init__(self):
        self.base_url = settings.MODEL_API_URL
        self.timeout = settings.MODEL_API_TIMEOUT
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to model-api"""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=data)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, json=data, files=files)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Model API request failed: {e.response.status_code} - {e.response.text}")
            # Extract more details if available, e.g., from a JSON response
            try:
                error_detail = e.response.json()
            except ValueError:
                error_detail = e.response.text
            raise ModelAPIError(
                message=f"Model API request failed for {endpoint}",
                status_code=e.response.status_code,
                detail=error_detail
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Model API request error: {e}")
            raise ModelAPIError(f"Model API request error for {endpoint}: {e}") from e
        except Exception as e:
            logger.exception(f"An unexpected error occurred in ModelAPIClient for {endpoint}")
            raise ModelAPIError(f"An unexpected error occurred in ModelAPIClient for {endpoint}: {e}") from e
    
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