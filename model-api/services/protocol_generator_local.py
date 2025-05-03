import openai
import json
from utils.data_formater import sanitize_transcript

client = openai.OpenAI(
    base_url="http://host.docker.internal:1234/v1",
    api_key="sk-local"
)

def generate_protocol(transcript: str) -> dict:
    # 1) Очищаем исходный текст от невидимых control-символов
    clean_text = sanitize_transcript(transcript)
    print("=== PROMPT ===")
    print(clean_text, "…")

    # 2) Составляем prompt: вставляем чистый текст напрямую
    prompt = f"""You are an expert assistant whose task is to transform a raw meeting transcript into a fully detailed, official meeting protocol. Your response must be returned in strict JSON matching the schema below, and include as much detail as possible:

{{
  "title": null,
  "date": null,
  "start_time": null,
  "duration": null,
  "location": null,
  "participants": [],
  "agenda": [],
  "decisions": [
    {{
      "topic": null,
      "speakers": [],
      "decision": null,
      "deadline": null,
      "responsible": null,
      "discussion_context": null,
      "timestamp": null
    }}
  ],
  "tasks": [
    {{
      "description": null,
      "responsible": null,
      "deadline": null
    }}
  ]
}}

Transcript:
{clean_text}""".strip()
    # 5) Для дебага можно распечатать prompt & ответ
    # 3) Отправляем ровно два сообщения: system + user
    response = client.chat.completions.create(
        model="local-model",
        messages=[
            {"role": "system", "content": "Ты — секретарь совещания."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1500
    )

    # 4) Берём сгенерированный текст
    content = response.choices[0].message.content

    print("=== RESPONSE ===")
    print(content[:500], "…")

    # 6) Парсим JSON из ответа
    try:
        json_start = content.index("{")
        return json.loads(content[json_start:])
    except Exception as e:
        return {
            "error": "Не удалось распарсить JSON",
            "exception": str(e),
            "raw_output": content
        }
