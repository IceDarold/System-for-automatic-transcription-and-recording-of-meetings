import requests
import os
from typing import Dict, Any, Optional
from models.Meeting import Meeting
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
import torch
import os
import shutil

import system_prompt

from dotenv import load_dotenv

load_dotenv()

# Backend API URL - should be set in environment variables in production
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api")


def setup_model(model_name, hf_token, cache_dir):
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)

    if torch.cuda.is_available():
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            load_in_4bit=True,
            token=hf_token
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="cpu",
            token=hf_token
        )

    model.save_pretrained(cache_dir)
    tokenizer.save_pretrained(cache_dir)

    return model, tokenizer


def load_messages() -> list[dict]:
    # Если это первый вопрос
    return []


def save_messages(messages: list[dict]):
    pass


def get_meeting_info(meeting_id: str) -> Dict[str, Any]:
    """
    Retrieves meeting information from the main backend API
    
    Args:
        meeting_id (str): The ID of the meeting
        
    Returns:
        dict: Meeting information or error details
    """
    try:
        # Make a request to the backend API
        response = requests.get(f"{BACKEND_API_URL}/meetings/{meeting_id}")
        
        # Check if the request was successful
        if response.status_code == 200:
            # Convert the response to a Meeting model
            meeting_data = response.json()
            meeting = Meeting(**meeting_data)
            return meeting.dict()
        else:
            return {
                "error": f"Failed to retrieve meeting: HTTP {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {"error": f"Error connecting to backend API: {str(e)}"}


def answer_question(meeting_id: str, question: str) -> str:
    """
    Stub function that returns a placeholder answer while retrieving meeting data
    
    Args:
        meeting_id (str): The ID of the meeting
        question: (str): The user's question
        
    Returns:
        answer: (str): The model's answer
    """
    HF_TOKEN = os.getenv("HF_TOKEN")

    if not HF_TOKEN:
        return f"ОШИБКА: не установлен HF_TOKEN в .env файле"

    MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"
    CACHE_DIR = "./mistral-7b-cache"

    os.makedirs(CACHE_DIR, exist_ok=True)

    login(token=HF_TOKEN)

    if os.path.exists(os.path.join(CACHE_DIR, "config.json")):
        tokenizer = AutoTokenizer.from_pretrained(CACHE_DIR)
        model = AutoModelForCausalLM.from_pretrained(
            CACHE_DIR,
            device_map="auto" if torch.cuda.is_available() else "cpu",
            torch_dtype=torch.float16 if torch.cuda.is_available() else None,
            load_in_4bit=torch.cuda.is_available()
        )
    else:
        model, tokenizer = setup_model(MODEL_NAME, HF_TOKEN, CACHE_DIR)

    meeting_data = get_meeting_info(meeting_id)
    if "error" in meeting_data:
        return f"ОШИБКА в meeting_data: {meeting_data['error']}"
    meeting = Meeting(**meeting_data)

    messages = load_messages()
    if not messages:
        s_prompt = system_prompt.system_prompt
        s_prompt += "\n\nТранскрипция совещания:\n"
        s_prompt += meeting.transcript
        messages = [{"role": "system", "content": s_prompt}]

    messages.append({"role": "user", "content": question})
    prompt = tokenizer.apply_chat_template(messages, tokenize=False)

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7
    )

    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

    messages.append({"role": "assistant", "content": response})
    save_messages(messages)

    return response
