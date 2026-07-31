def test_seeded_manual_is_searchable(client):
    response = client.post(
        "/api/v1/knowledge/search",
        json={"query": "garantía del taladro T700", "top_k": 3},
    )

    assert response.status_code == 200
    results = response.json()
    assert results
    assert results[0]["title"] == "Manual de demostración del taladro T700"
    assert "12 meses" in results[0]["content"]


def test_document_ingestion_requires_admin_and_rejects_duplicate(
    client,
    admin_headers,
):
    payload = {
        "title": "Ficha técnica de pintura",
        "source": "tests/pintura",
        "content": (
            "La pintura exterior debe aplicarse sobre una superficie limpia y seca. "
            "El tiempo de secado de demostración es de cuatro horas."
        ),
        "metadata": {"category": "pinturas"},
    }

    forbidden = client.post("/api/v1/knowledge/documents", json=payload)
    created = client.post(
        "/api/v1/knowledge/documents",
        json=payload,
        headers=admin_headers,
    )
    duplicate = client.post(
        "/api/v1/knowledge/documents",
        json=payload,
        headers=admin_headers,
    )

    assert forbidden.status_code == 403
    assert created.status_code == 201
    assert created.json()["chunks_created"] >= 1
    assert duplicate.status_code == 409


def test_demo_chat_returns_rag_citations(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "¿Qué garantía tiene el taladro T700?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tools_used"][0]["name"] == "search_knowledge"
    assert body["citations"]
    assert body["citations"][0]["source"] == "demo/manual-taladro-t700"
