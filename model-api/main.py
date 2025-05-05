from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from services import transcriber, summarizer, diarizer, speaker_text, protocol_generator_local, meeting_chatbot
from utils.io import save_temp_file
from utils.data_formater import prepare_transcript_for_json
from models.TranscriptInput import TranscriptInput  
from models.ChatInput import ChatInput
from fastapi.responses import JSONResponse
import os
from typing import Dict, Any

app = FastAPI()

@app.exception_handler(FileNotFoundError)
async def file_not_found_exception_handler(request: Request, exc: FileNotFoundError):
    return JSONResponse(
        status_code=400,
        content={"error": "File not found", "details": str(exc)}
    )

@app.exception_handler(OSError)
async def os_error_exception_handler(request: Request, exc: OSError):
    return JSONResponse(
        status_code=400,
        content={"error": "OS error", "details": str(exc)}
    )

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid value", "details": str(exc)}
    )

@app.exception_handler(KeyError)
async def key_error_exception_handler(request: Request, exc: KeyError):
    return JSONResponse(
        status_code=400,
        content={"error": "Missing required field", "details": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

def validate_file_size(file: UploadFile, max_size_mb: int = 100) -> None:
    """Validate file size before processing"""
    file_size = 0
    for chunk in file.file:
        file_size += len(chunk)
        if file_size > max_size_mb * 1024 * 1024:  # Convert MB to bytes
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
            )
    file.file.seek(0)  # Reset file pointer

def validate_audio_file(file: UploadFile) -> None:
    """Validate audio file format"""
    allowed_types = ["audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    validate_file_size(file)
    validate_audio_file(file)
    path = save_temp_file(file)
    try:
        result = transcriber.transcribe(path)
        return {"transcription": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(path):
            os.remove(path)

@app.post("/summary")
async def summary(file: UploadFile = File(...)):
    validate_file_size(file)
    path = save_temp_file(file)
    try:
        result = summarizer.generate_summary(path)
        return {"summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(path):
            os.remove(path)

@app.post("/speakers")
async def speakers(file: UploadFile = File(...)):
    validate_file_size(file)
    validate_audio_file(file)
    path = save_temp_file(file)
    try:
        result = diarizer.detect_speakers(path)
        return {"segments": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(path):
            os.remove(path)

@app.post("/protocol")
async def protocol(input_data: TranscriptInput):
    try:
        result = protocol_generator_local.generate_protocol(input_data.transcript)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/answer")
async def chat_answer(input_data: ChatInput):
    try:
        result = meeting_chatbot.get_answer(input_data.meeting_id, input_data.question)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/meeting/{meeting_id}")
async def get_meeting_info(meeting_id: str):
    try:
        result = meeting_chatbot.get_meeting_info(meeting_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
