# Ejemplos de API

Base local:

```text
http://localhost:8000/api/v1
```

## Productos

```bash
curl "http://localhost:8000/api/v1/products?query=taladro&limit=10"
```

## Crear producto

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: development-admin-key-change-me" \
  -d '{
    "sku": "MECHA-8",
    "name": "Mecha para hormigón 8 mm",
    "description": "Mecha con punta de carburo.",
    "category": "Accesorios",
    "price": 6500,
    "stock": 30
  }'
```

## Chat

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"¿Cuánto stock queda del martillo M20?"}'
```

Para continuar:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message":"Hola nuevamente",
    "conversation_id":"UUID_DEVUELTO"
  }'
```

## RAG

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query":"garantía del T700","top_k":4}'
```

## Guardrail

Una solicitud de extracción de secretos devuelve un error estructurado:

```json
{
  "error": {
    "code": "guardrail_blocked",
    "message": "The request conflicts with the assistant safety boundaries",
    "request_id": "req_..."
  }
}
```
