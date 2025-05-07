import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "mistralai/mistral-7b-instruct"  # можно заменить

def build_protocol_prompt(transcript: str) -> str:
    return f"""
Ты — помощник, который по расшифровке совещания составляет официальный протокол.

Выдели:
- название, дату, время, участников
- список вопросов
- решения по каждому вопросу, кто говорил, какие поручения были, кто ответственный, сроки

Верни строго структурированный JSON:

{{
  "title": "...",
  "date": "...",
  "start_time": "...",
  "duration": "...",
  "participants": [...],
  "agenda": [...],
  "decisions": [...],
  "tasks": [...]
}}

Текст встречи:
{transcript}
"""

def call_openrouter_llm(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Ты умный ассистент, создающий протоколы встреч."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

def generate_protocol(transcript: str) -> dict:
    prompt = build_protocol_prompt(transcript)
    llm_output = call_openrouter_llm(prompt)

    # Попытка безопасно распарсить JSON
    try:
        json_start = llm_output.find("{")
        json_text = llm_output[json_start:]
        protocol = json.loads(json_text)
    except Exception:
        protocol = {
            "error": "Невалидный JSON от модели",
            "raw_output": llm_output
        }

    return protocol
