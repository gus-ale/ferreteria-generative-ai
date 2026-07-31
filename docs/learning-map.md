# Mapa de aprendizaje

| Tema de Generative AI Engineer | Implementación |
|---|---|
| Prompt engineering | `SYSTEM_INSTRUCTIONS` |
| Responses API | `AgentService._run_openai` |
| Function calling | `ToolExecutor` y bucle del agente |
| Structured schemas | Argumentos Pydantic y JSON Schema estricto |
| Embeddings | `EmbeddingProvider` |
| Vector search | Similitud coseno y ranking |
| RAG | `KnowledgeService` |
| Chunking | `chunk_text` |
| Memoria | Conversation y Message |
| Guardrails | `inspect_input`, allowlist y `sanitize_output` |
| Evals | `evals/cases.json` |
| Observabilidad | Middleware, request IDs y Prometheus |
| Producción | Docker, MySQL, Alembic y CI |

## Recorrido recomendado

1. Ejecutar en modo demo.
2. Probar `/products`.
3. Probar `/knowledge/search`.
4. Conversar con `/chat`.
5. Consultar la memoria.
6. Ejecutar pytest.
7. Ejecutar evals.
8. Leer el bucle OpenAI.
9. Activar OpenAI en staging.
10. Comparar resultados con la línea base.
