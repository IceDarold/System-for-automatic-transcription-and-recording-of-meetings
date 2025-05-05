import requests
import os
from typing import Dict, Any, Optional

# Backend API URL - should be set in environment variables in production
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api")

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
            return response.json()
        else:
            return {
                "error": f"Failed to retrieve meeting: HTTP {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {"error": f"Error connecting to backend API: {str(e)}"}

def answer_question(meeting_id: str, question: str) -> Dict[str, Any]:
    """
    Answers a question about a meeting by retrieving meeting data 
    from the backend API and processing the question
    
    Args:
        meeting_id (str): The ID of the meeting
        question (str): The user's question
        
    Returns:
        dict: Answer to the question or error message
    """
    # Get meeting data from the backend
    meeting_data = get_meeting_info(meeting_id)
    
    # Check if we got an error
    if "error" in meeting_data:
        return {"answer": f"Sorry, I couldn't access the meeting information: {meeting_data['error']}"}
    
    # Simple keyword matching for questions
    question_lower = question.lower()
    
    # Process the question based on keywords
    if "when" in question_lower or "time" in question_lower or "date" in question_lower:
        date = meeting_data.get("date", "unknown date")
        time = meeting_data.get("start_time", "unknown time")
        return {"answer": f"The meeting was held on {date} at {time}."}
    
    elif "who" in question_lower or "participant" in question_lower or "attend" in question_lower:
        participants = meeting_data.get("participants", [])
        if participants:
            participants_str = ", ".join([p.get("name", "Unknown") if isinstance(p, dict) else p for p in participants])
            return {"answer": f"The meeting was attended by {participants_str}."}
        else:
            return {"answer": "I don't have information about the participants."}
    
    elif "summary" in question_lower or "about" in question_lower:
        summary = meeting_data.get("summary", "No summary available.")
        return {"answer": f"Here's a summary of the meeting: {summary}"}
    
    elif "decision" in question_lower or "conclusion" in question_lower:
        decisions = meeting_data.get("decisions", [])
        if decisions:
            decisions_str = ", ".join(decisions)
            return {"answer": f"The following decisions were made: {decisions_str}"}
        else:
            return {"answer": "I don't have information about decisions made during this meeting."}
    
    elif "transcript" in question_lower or "said" in question_lower:
        transcript = meeting_data.get("transcript", "No transcript available.")
        if isinstance(transcript, str) and len(transcript) > 300:
            transcript = transcript[:297] + "..."
        return {"answer": f"Here's the transcript: {transcript}"}
    
    elif "location" in question_lower or "where" in question_lower:
        location = meeting_data.get("location", "unknown location")
        is_online = meeting_data.get("is_online", False)
        if is_online:
            return {"answer": "This was an online meeting."}
        else:
            return {"answer": f"The meeting was held at {location}."}
    
    else:
        return {"answer": "I don't have specific information to answer that question. You can ask about the time, participants, summary, decisions, or location of the meeting."} 