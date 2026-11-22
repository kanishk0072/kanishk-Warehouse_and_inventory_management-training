from auth_dependencies import get_current_user
from main import app

def test_users_without_token(client):
    # Temporarily disable mocked authentication
    original = app.dependency_overrides.pop(get_current_user, None)

    try:
        response = client.get("/api/v1/users")
        assert response.status_code == 401
    finally:
        # Restore mock for other tests
        if original is not None:
            app.dependency_overrides[get_current_user] = original