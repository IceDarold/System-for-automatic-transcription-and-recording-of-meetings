import json

def prepare_transcript_for_json(transcript: str) -> str:
    """
    Принимает многострочный текст и возвращает безопасную строку,
    которую можно вставлять в JSON (или передавать через Swagger/UI).
    """
    return json.dumps({"transcript": transcript}, ensure_ascii=False)
import re


def sanitize_transcript(text: str) -> str:
    """
    Убирает из текста все control‑символы в диапазоне 0x00–0x1F,
    кроме \n (0x0A) и \t (0x09), а также удаляет \r.
    """
    # удаляем \r
    text = text.replace("\r", "")
    # оставляем только \n (0A) и \t (09), всё остальное в диапазоне 0x00–0x1F удаляем
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)

