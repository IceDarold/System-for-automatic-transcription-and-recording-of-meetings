from pydantic import BaseModel

class TranscriptInput(BaseModel):
    transcript: str
