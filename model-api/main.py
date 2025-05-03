from fastapi import FastAPI, File, UploadFile
from services import transcriber, summarizer, diarizer, speaker_text, protocol_generator_local
from utils.io import save_temp_file
from utils.data_formater import prepare_transcript_for_json
from models.TranscriptInput import TranscriptInput  

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
