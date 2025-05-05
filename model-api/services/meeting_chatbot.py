import requests
import os
from typing import Dict, Any, Optional
from models.Meeting import Meeting

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

def answer_question(meeting_id: str, question: str) -> Dict[str, Any]:
    """
    Stub function that returns a placeholder answer while retrieving meeting data
    
    Args:
        meeting_id (str): The ID of the meeting
        question (str): The user's question
        
    Returns:
        dict: Placeholder answer
    """
    # Get meeting data from the backend
    meeting_data = get_meeting_info(meeting_id)
    
    # Check if we got an error
    if "error" in meeting_data:
        return {"answer": f"Sorry, I couldn't access the meeting information: {meeting_data['error']}"}
    
    # Convert to Meeting model
    meeting = Meeting(**meeting_data)
    
    # Just return a generic response
    return {
        "answer": f"This is a placeholder response for meeting '{meeting.title}'. In the future, this will provide actual answers to questions about meetings."
    } 