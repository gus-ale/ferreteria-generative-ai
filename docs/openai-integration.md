# Integración OpenAI

## Responses API

La implementación utiliza `AsyncOpenAI` y `client.responses.create`. El cliente
se crea una vez durante el ciclo de vida de FastAPI y se cierra al detener la
aplicación.

La configuración externa controla:

- Modelo.
- Timeout.
- Reintentos.
- Cantidad máxima de turnos.
- Modelo de embeddings.

## Bucle de herramientas

La respuesta puede incluir elementos `function_call`. Para cada uno:

1. Se comprueba que el nombre esté permitido.
2. Se convierten los argumentos JSON.
3. Pydantic valida tipos y rangos.
4. El backend ejecuta la función.
5. Se registra la ejecución.
6. Se agrega `function_call_output` al contexto.
7. Se vuelve a consultar al modelo.

Si no hay llamadas, `output_text` se transforma en la respuesta final.

## Errores

Se manejan por separado:

- `APITimeoutError`
- `RateLimitError`
- `APIConnectionError`
- `APIStatusError`

El `request_id` se registra cuando existe. El cliente no devuelve detalles
internos al usuario.

## Embeddings

El proveedor real llama a `client.embeddings.create`. El orden de los resultados
se reconstruye mediante el campo `index`.

El proveedor local es un hashing lexical normalizado. Es útil para CI, pero no
se describe como búsqueda semántica real.

## Cambios de modelo

El modelo no está fijado en el código. Antes de cambiar `OPENAI_MODEL`:

1. Ejecutar la línea base de evals.
2. Cambiar el ambiente de staging.
3. Comparar calidad, costo y latencia.
4. Revisar trazas y herramientas.
5. Promover a producción si supera los umbrales.
