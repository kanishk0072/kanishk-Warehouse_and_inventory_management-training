from api.v1.products import notify_inventory_team

def test_duplicate_product_sku(client, monkeypatch):
    monkeypatch.setattr(
        notify_inventory_team,
        "delay",
        lambda sku: None,
    )

def test_product_full_crud(client):
    # 1. CREATE PRODUCT
    product_data = {
        "name": "Test Laptop",
        "sku": "TEST-LAPTOP-001",
        "description": "Laptop for testing",
        "unit_price": "1500.00",
        "status": "active",
        "category_id": None,
    }

    response = client.post(
        "/api/v1/products/",
        json=product_data,
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Test Laptop"

    product_id = response.json()["id"]

    # 2. READ PRODUCT
    response = client.get(
        f"/api/v1/products/{product_id}"
    )

    assert response.status_code == 200
    assert response.json()["sku"] == "TEST-LAPTOP-001"

    # 3. LIST PRODUCTS
    response = client.get("/api/v1/products/")

    assert response.status_code == 200
    assert any(
        product["id"] == product_id
        for product in response.json()
    )

    # 4. UPDATE PRODUCT
    updated_data = {
        "name": "Updated Laptop",
        "sku": "TEST-LAPTOP-001",
        "description": "Updated description",
        "unit_price": "2000.00",
        "status": "active",
        "category_id": None,
    }

    response = client.put(
        f"/api/v1/products/{product_id}",
        json=updated_data,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Laptop"

    # 5. DELETE PRODUCT
    response = client.delete(
        f"/api/v1/products/{product_id}"
    )

    assert response.status_code == 204

    # 6. VERIFY DELETION
    response = client.get(
        f"/api/v1/products/{product_id}"
    )

    assert response.status_code == 404