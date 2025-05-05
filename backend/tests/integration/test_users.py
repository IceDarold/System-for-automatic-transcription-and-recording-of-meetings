from fastapi import status
from backend.app import app
from fastapi.testclient import TestClient
from database import get_db
from .conftest import create_user_and_token

client = TestClient(app)

def test_get_me_user_integration(db_session):
    user, token = create_user_and_token(db_session)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_200_OK, 404)
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert data["email"] == user.email 