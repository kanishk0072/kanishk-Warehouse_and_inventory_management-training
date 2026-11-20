from sqlalchemy import select
from models import User
import pytest


def test_signup_success(client, db_session, monkeypatch):
    # Avoid waiting for the simulated welcome email
    monkeypatch.setattr(
        "api.v1.auth.simulate_welcome_email",
        lambda email: None,
    )

    user_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPass123!",
    }

    response = client.post(
        "/api/v1/auth/signup",
        json=user_data,
    )

    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
    assert response.json()["role"] == "staff"

    # Verify the user was actually saved
    user = db_session.scalar(
        select(User).where(User.email == user_data["email"])
    )

    assert user is not None
    assert user.hashed_password != user_data["password"]


def test_signup_duplicate_email(client, monkeypatch):
    monkeypatch.setattr(
        "api.v1.auth.simulate_welcome_email",
        lambda email: None,
    )

    user_data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "TestPass123!",
    }

    # First signup
    first_response = client.post(
        "/api/v1/auth/signup",
        json=user_data,
    )

    assert first_response.status_code == 201

    # Second signup with same email
    second_response = client.post(
        "/api/v1/auth/signup",
        json=user_data,
    )

    assert second_response.status_code == 409
    assert second_response.json()["error"]["message"] == "Email already registered"


@pytest.fixture
def registered_user(client, monkeypatch):
    monkeypatch.setattr(
        "api.v1.auth.simulate_welcome_email",
        lambda email: None,
    )

    user_data = {
        "name": "Login Test User",
        "email": "login@example.com",
        "password": "TestPass123!",
    }

    response = client.post(
        "/api/v1/auth/signup",
        json=user_data,
    )

    assert response.status_code == 201

    return user_data


def test_login_success(client, registered_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, registered_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": registered_user["email"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401