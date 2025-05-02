from fastapi import FastAPI, File, UploadFile
from services import transcriber, summarizer, diarizer, speaker_text
from utils.io import save_temp_file

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
