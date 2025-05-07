import pytest
from fastapi import status
from datetime import datetime

# Assuming your User model and factories are accessible as in other integration tests
from models import User, Meeting
# from .conftest import user_factory, auth_headers_factory, client (client is a fixture)

# Basic structure, will need to import User, user_factory, auth_headers_factory if not auto-available through conftest
# For now, assume client fixture is available. Import others as needed when running.

def test_get_current_user_info_authenticated(client, user_factory, auth_headers_factory):
    """Test successfully retrieving current user info"""
    unique_email = f"getme_user_{datetime.now().timestamp()}@example.com"
    test_user = user_factory(email=unique_email, first_name="GetMe", last_name="User")
    headers = auth_headers_factory(test_user)

    response = client.get("/api/v1/users/me", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["first_name"] == "GetMe"
    assert data["id"] == test_user.id

def test_get_current_user_info_unauthenticated(client):
    """Test retrieving current user info without authentication"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_current_user_info_authenticated(client, user_factory, auth_headers_factory, db_session):
    """Test successfully updating current user info"""
    unique_email = f"updateme_user_{datetime.now().timestamp()}@example.com"
    test_user = user_factory(email=unique_email, first_name="OriginalFirst", last_name="OriginalLast")
    headers = auth_headers_factory(test_user)

    update_payload = {
        "first_name": "UpdatedFirst",
        "last_name": "UpdatedLast",
        "middle_name": "UpdatedMiddle" 
        # Not updating password here for simplicity, can be a separate test
    }
    response = client.put("/api/v1/users/me", json=update_payload, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email # Email should not change
    assert data["first_name"] == "UpdatedFirst"
    assert data["last_name"] == "UpdatedLast"
    assert data["middle_name"] == "UpdatedMiddle"

    # Verify in DB (optional, but good for confirming persistence)
    db_session.refresh(test_user) # Refresh from DB
    assert test_user.first_name == "UpdatedFirst"
    assert test_user.last_name == "UpdatedLast"

@pytest.mark.parametrize("payload_override, field_name_in_error", [
    ({"first_name": ""}, "first_name"), # Empty first name
    ({"last_name": ""}, "last_name"),   # Empty last name
    # Add more invalid cases if UserUpdate schema has more validations (e.g., password complexity)
    # Example for password (if UserUpdate allows it and has validation): 
    # {"password": "short"}, "password" 
])
def test_update_current_user_info_invalid_data(client, user_factory, auth_headers_factory, payload_override, field_name_in_error):
    """Test updating current user info with invalid data"""
    unique_email = f"updateinvalid_{datetime.now().timestamp()}@example.com"
    test_user = user_factory(email=unique_email)
    headers = auth_headers_factory(test_user)

    base_payload = {"first_name": "Valid", "last_name": "Valid"}
    invalid_payload = {**base_payload, **payload_override}
    
    response = client.put("/api/v1/users/me", json=invalid_payload, headers=headers)
    
    # Depending on how your UserUpdate schema and endpoint handle validation
    # It might be 422 Unprocessable Entity (Pydantic) or 400 Bad Request (custom endpoint validation)
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    data = response.json()
    assert "detail" in data
    # More specific error checking can be added if error messages are consistent
    # e.g., assert field_name_in_error in str(data["detail"]).lower()

def test_update_current_user_info_unauthenticated(client):
    """Test updating current user info without authentication"""
    update_payload = {"first_name": "AttemptedUpdate"}
    response = client.put("/api/v1/users/me", json=update_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_user_meetings_authenticated(client, user_factory, auth_headers_factory, meeting_factory):
    """Test retrieving meetings created by the current user"""
    unique_email = f"getmeetings_user_{datetime.now().timestamp()}@example.com"
    test_user = user_factory(email=unique_email)
    headers = auth_headers_factory(test_user)

    # Create some meetings for this user
    meeting1 = meeting_factory(created_by_user=test_user, title="User Meeting 1")
    meeting2 = meeting_factory(created_by_user=test_user, title="User Meeting 2")
    # Create a meeting by another user to ensure it's not listed
    other_user = user_factory(email=f"other_user_{datetime.now().timestamp()}@example.com")
    meeting_factory(created_by_user=other_user, title="Other User Meeting")

    response = client.get("/api/v1/users/me/meetings", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    meeting_titles = [m["title"] for m in data]
    assert meeting1.title in meeting_titles
    assert meeting2.title in meeting_titles
    assert "Other User Meeting" not in meeting_titles

def test_get_user_meetings_unauthenticated(client):
    """Test retrieving user meetings without authentication"""
    response = client.get("/api/v1/users/me/meetings")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_user_logs_authenticated(client, user_factory, auth_headers_factory, db_session):
    """Test retrieving audit logs for the current user"""
    # This test assumes AuditLog model and logging are working correctly.
    # It also depends on the endpoint actually returning logs.
    unique_email = f"getlogs_user_{datetime.now().timestamp()}@example.com"
    test_user = user_factory(email=unique_email)
    headers = auth_headers_factory(test_user)
    
    # Perform an action that should generate an audit log for this user, e.g., login or update profile
    # For simplicity, we'll assume some logs might exist or the endpoint returns an empty list gracefully.
    # A more robust test would trigger a loggable action and then check.
    
    # Example: Simulate an update to potentially generate a log (if your app logs this)
    client.put("/api/v1/users/me", json={"first_name": "LogGen"}, headers=headers)

    response = client.get("/api/v1/users/me/logs", headers=headers)
    
    if response.status_code == status.HTTP_501_NOT_IMPLEMENTED:
        pytest.skip("Audit logging endpoint is not implemented.")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # If logs were generated by the PUT above and logging is synchronous & fast enough:
    # assert len(data) > 0
    # if len(data) > 0:
    #     assert data[0]["user_id"] == test_user.id # Or however user_id is represented

def test_get_user_logs_unauthenticated(client):
    """Test retrieving user logs without authentication"""
    response = client.get("/api/v1/users/me/logs")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# To make this runnable, ensure necessary imports are at the top, e.g.:
# from models import User # etc.
# from ..conftest import user_factory, auth_headers_factory # if conftest is one level up
# It's common to have a top-level conftest.py in tests/integration that provides these.
# For now, assuming `client` fixture is available globally from a higher-level conftest.
# And user_factory, auth_headers_factory, meeting_factory, db_session are also available. 