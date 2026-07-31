def test_root_exposes_service_metadata(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "Ferretería Generative AI"
    assert response.json()["provider"] == "demo"
    assert response.headers["X-Request-ID"].startswith("req_")


def test_liveness_and_readiness(client):
    live = client.get("/api/v1/health/live")
    ready = client.get("/api/v1/health/ready")

    assert live.status_code == 200
    assert live.json() == {"status": "alive"}
    assert ready.status_code == 200
    assert ready.json()["database"] == "available"
    assert ready.json()["embedding_provider"] == "local"
