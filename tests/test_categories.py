def test_category_full_crud(client):
    category_data = {
        "name": "electronics",
        "description": "electronic item"
        }

    response = client.post(
        "api/v1/categories/",
        json=category_data,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "electronics"

    category_id = response.json()["id"]

    response = client.get(
        f"/api/v1/categories/{category_id}"
    )

    assert response.status_code == 200
    assert response.json()["name"] == "electronics"

    response = client.get("/api/v1/categories/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "electronics"

    updated_data = {
        "name": "updated electronics",
        "description": "updated electronic item"
    }
    