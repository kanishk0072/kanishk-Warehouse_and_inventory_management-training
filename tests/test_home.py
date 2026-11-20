from tests.conftest import client


def test_home_returns_expected_response(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to Warehouse and Inventory Management API"
    }
