from fastapi import FastAPI, File, UploadFile
from services import transcriber, summarizer, diarizer, speaker_text, protocol_generator_local, meeting_chatbot
from utils.io import save_temp_file
from utils.data_formater import prepare_transcript_for_json
from models.TranscriptInput import TranscriptInput  
from models.ChatInput import ChatInput

app = FastAPI()

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    path = save_temp_file(file)
    result = transcriber.transcribe(path)
    return {"transcription": result}

@app.post("/summary")
async def summary(file: UploadFile = File(...)):
    path = save_temp_file(file)
    result = summarizer.generate_summary(path)
    return {"summary": result}

@app.post("/speakers")
async def speakers(file: UploadFile = File(...)):
    path = save_temp_file(file)
    result = diarizer.detect_speakers(path)
    return {"segments": result}

@app.post("/speaker-transcript")
async def speaker_transcript(file: UploadFile = File(...)):
    path = save_temp_file(file)
    result = speaker_text.speaker_segments(path)
    return {"segments": result}

@app.post("/protocol")
async def generate_protocol_endpoint(data: TranscriptInput):
    protocol = protocol_generator_local.generate_protocol(prepare_transcript_for_json(data.transcript))
    return protocol 

@app.post("/chat/answer")
async def chat_answer(data: ChatInput):
    """
    Endpoint for answering questions about meetings.
    """
    result = meeting_chatbot.answer_question(data.meeting_id, data.question)
    return result

@app.get("/chat/meeting/{meeting_id}")
async def get_meeting_info(meeting_id: str):
    """
    Endpoint for retrieving information about a specific meeting.
    """
    result = meeting_chatbot.get_meeting_info(meeting_id)
    return result 
