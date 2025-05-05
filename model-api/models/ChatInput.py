from pydantic import BaseModel
 
class ChatInput(BaseModel):
    meeting_id: str
    question: str 