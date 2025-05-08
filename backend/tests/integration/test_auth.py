import pytest
from fastapi import status
from models import User
from datetime import datetime

# Импортируем app и get_current_user для управления зависимостями
# from backend.app import app
# from core.auth import get_current_user

def test_register_success(client, db_session):
    """Тест успешной регистрации пользователя"""
    response = client.post(
        "/api/v1/auth/register",
        data={
            "email": "newuser_reg_success@example.com",
            "password": "securepassword123",
            "first_name": "New",
            "last_name": "User",
            "middle_name": None
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
    user = db_session.query(User).filter(User.email == "newuser_reg_success@example.com").first()
    assert user is not None
    assert user.first_name == "New"
    assert user.last_name == "User"

def test_register_existing_user(client, user_factory, db_session):
    """Тест регистрации с уже существующим email"""
    unique_email = f"existing_reg_{datetime.now().timestamp()}@example.com"
    
    user_factory(
        email=unique_email,
        raw_password="password",
        first_name="Existing",
        last_name="User",
        is_active=True,
        role="user"
    )
    
    response = client.post(
        "/api/v1/auth/register",
        data={
            "email": unique_email,
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "middle_name": None
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"]

def test_register_invalid_email(client):
    """Тест регистрации с некорректным email"""
    response = client.post(
        "/api/v1/auth/register",
        data={
            "email": "invalidemail",
            "password": "password123",
            "first_name": "Invalid",
            "last_name": "Email",
            "middle_name": None
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "Invalid email format" in data["detail"]

def test_register_short_password(client):
    """Тест регистрации с коротким паролем"""
    response = client.post(
        "/api/v1/auth/register",
        data={
            "email": f"short_pass_{datetime.now().timestamp()}@example.com",
            "password": "short",
            "first_name": "Short",
            "last_name": "Password",
            "middle_name": None
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "at least 6 characters" in data["detail"]

def test_register_empty_name(client):
    """Тест регистрации с пустым именем или фамилией"""
    response_first_name = client.post(
        "/api/v1/auth/register",
        data={
            "email": f"empty_fname_{datetime.now().timestamp()}@example.com",
            "password": "password123",
            "first_name": "",
            "last_name": "User",
            "middle_name": None
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response_first_name.status_code == status.HTTP_400_BAD_REQUEST
    data_first_name = response_first_name.json()
    assert "detail" in data_first_name
    assert data_first_name["detail"] == "First name cannot be empty."

    response_last_name = client.post(
        "/api/v1/auth/register",
        data={
            "email": f"empty_lname_{datetime.now().timestamp()}@example.com",
            "password": "password123",
            "first_name": "Empty",
            "last_name": "",
            "middle_name": None
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response_last_name.status_code == status.HTTP_400_BAD_REQUEST
    data_last_name = response_last_name.json()
    assert "detail" in data_last_name
    assert data_last_name["detail"] == "Last name cannot be empty."

def test_login_success(client, user_factory):
    """Тест успешного входа в систему"""
    email_login_succ = f"login_succ_{datetime.now().timestamp()}@example.com"
    user_factory(
        email=email_login_succ,
        raw_password="correctpassword",
        first_name="Login",
        last_name="User",
        is_active=True,
        role="user"
    )
        
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email_login_succ,
            "password": "correctpassword"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_nonexistent_user(client):
    """Тест входа с несуществующим пользователем"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": f"nonexistent_login_{datetime.now().timestamp()}@example.com",
            "password": "anypassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    assert "User with this email not found" in data["detail"]

def test_login_wrong_password(client, user_factory):
    """Тест входа с неправильным паролем"""
    email_wrong_pass = f"wrong_pass_{datetime.now().timestamp()}@example.com"
    user_factory(
        email=email_wrong_pass,
        raw_password="correctpassword",
        first_name="Password",
        last_name="User",
        is_active=True,
        role="user"
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email_wrong_pass,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    assert "Incorrect password" in data["detail"]

def test_login_invalid_email(client):
    """Тест входа с некорректным форматом email"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "notanemail",
            "password": "anypassword"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "Invalid email format" in data["detail"]

def test_refresh_token(client, user_factory, auth_headers_factory, db_session):
    """Тест обновления токена"""
    test_user = user_factory(email=f"refresh_user_{datetime.now().timestamp()}@example.com")
    headers = auth_headers_factory(test_user)
    
    response = client.post(
        "/api/v1/auth/refresh",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_logout(client, user_factory, auth_headers_factory, db_session):
    """Тест выхода из системы"""
    test_user = user_factory(email=f"logout_user_{datetime.now().timestamp()}@example.com")
    headers = auth_headers_factory(test_user)
    
    response = client.post(
        "/api/v1/auth/logout",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "Successfully logged out" in data["message"]

def test_refresh_with_invalid_token(client, db_session):
    """Тест обновления токена с некорректным токеном"""
    
    # Удаляем манипуляции с зависимостями, т.к. глобального оверрайда больше нет
    # original_override = app.dependency_overrides.pop(get_current_user, None)
    # try:
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Could not validate credentials"
    # finally:
    #     if original_override:
    #         app.dependency_overrides[get_current_user] = original_override
    #     elif get_current_user in app.dependency_overrides:
    #          app.dependency_overrides.pop(get_current_user)

def test_validate_token_with_me_endpoint(client, user_factory, auth_headers_factory, db_session):
    """Тест валидации токена через эндпоинт /me"""
    test_user = user_factory(email=f"me_user_{datetime.now().timestamp()}@example.com")
    headers = auth_headers_factory(test_user)

    response = client.get(
        "/api/v1/auth/me",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["first_name"] == test_user.first_name
    assert data["last_name"] == test_user.last_name

def test_register_long_values(client, db_session):
    """Тест регистрации со слишком длинными значениями полей"""
    response = client.post(
        "/api/v1/auth/register",
        data={
            "email": f"test@{'a'*300}.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "middle_name": None
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "Email is too long" in data["detail"] or "email" in data["detail"].lower()
    
    response = client.post(
        "/api/v1/auth/register",
        data={
            "email": "test@example.com",
            "password": "password123",
            "first_name": "a"*301,
            "last_name": "User",
            "middle_name": None
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "First name is too long" in data["detail"] or "name" in data["detail"].lower()

def test_register_sql_injection(client, db_session):
    """Тест защиты от SQL-инъекций при регистрации (через валидацию email)"""
    response = client.post(
        "/api/v1/auth/register",
        data={
            "email": "test@example.com'; DROP TABLE users; --",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "middle_name": None
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Invalid email format. Please enter a valid email address."
    
    # Дополнительная проверка, что таблица не удалена (хотя до SQL дело дойти не должно)
    users_count = db_session.query(User).count() 
    assert users_count >= 0

def test_get_me_unauthenticated(client):
    """Тест получения информации о текущем пользователе без аутентификации"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    # Example: assert data["detail"] == "Not authenticated"

def test_refresh_token_unauthenticated(client):
    """Тест обновления токена без аутентификации"""
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    # Example: assert data["detail"] == "Not authenticated"

def test_logout_unauthenticated(client):
    """Тест выхода из системы без аутентификации"""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    # Example: assert data["detail"] == "Not authenticated"