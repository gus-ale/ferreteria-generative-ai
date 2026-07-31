def test_seeded_products_can_be_searched(client):
    response = client.get("/api/v1/products", params={"query": "martillo M20"})

    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["sku"] == "MAR-M20"
    assert products[0]["stock"] == 18


def test_product_creation_requires_admin_key(client):
    response = client.post(
        "/api/v1/products",
        json={
            "sku": "LLA-10",
            "name": "Llave combinada 10 mm",
            "description": "Llave de acero.",
            "category": "Herramientas manuales",
            "price": "7200.00",
            "stock": 15,
        },
    )

    assert response.status_code == 403


def test_admin_can_create_product_and_duplicate_sku_is_rejected(
    client,
    admin_headers,
):
    payload = {
        "sku": "LLA-11",
        "name": "Llave combinada 11 mm",
        "description": "Llave de acero.",
        "category": "Herramientas manuales",
        "price": "7400.00",
        "stock": 12,
    }

    created = client.post(
        "/api/v1/products",
        json=payload,
        headers=admin_headers,
    )
    duplicate = client.post(
        "/api/v1/products",
        json=payload,
        headers=admin_headers,
    )

    assert created.status_code == 201
    assert created.json()["sku"] == "LLA-11"
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "conflict"
