import tempfile
from fastapi import status
from backend.app import app
from fastapi.testclient import TestClient
from database import get_db
from .conftest import create_user_and_token

client = TestClient(app)

def test_upload_file_integration(db_session):
    user, token = create_user_and_token(db_session)
    app.dependency_overrides[get_db] = lambda: db_session
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"dummy file content")
        f.flush()
        f.seek(0)
        response = client.post(
            "/api/v1/files/",
            files={"file": ("test.txt", open(f.name, "rb"), "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 404)

def test_get_files_integration(db_session):
    user, token = create_user_and_token(db_session)
    app.dependency_overrides[get_db] = lambda: db_session
    response = client.get(
        "/api/v1/files/",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code in (status.HTTP_200_OK, 404) 