def test_users_without_token(client):
    response = client.get("/api/v1/users")

    assert response.status_code == 401